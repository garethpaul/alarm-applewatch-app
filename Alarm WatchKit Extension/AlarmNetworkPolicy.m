#import "AlarmNetworkPolicy.h"

NSUInteger const AlarmMaximumResponseBodyBytes = 4096;

@implementation AlarmNetworkPolicy

+ (NSString *)canonicalHost:(NSString *)host {
    NSString *canonical = [host lowercaseString];
    while ([canonical hasSuffix:@"."]) {
        canonical = [canonical substringToIndex:[canonical length] - 1];
    }
    return canonical;
}

+ (BOOL)isDisallowedHost:(NSString *)host {
    NSArray *suffixes = @[
        @"localhost",
        @"local",
        @"internal",
        @"alt",
        @"arpa",
        @"home.arpa",
        @"onion",
        @"invalid",
        @"test",
        @"example.com",
        @"example.net",
        @"example.org",
        @"example"
    ];

    for (NSString *suffix in suffixes) {
        if ([host isEqualToString:suffix] ||
            [host hasSuffix:[@"." stringByAppendingString:suffix]]) {
            return YES;
        }
    }

    return NO;
}

+ (BOOL)isValidPublicDNSHost:(NSString *)host {
    if ([host length] == 0 || [host length] > 253 ||
        [host rangeOfString:@":"].location != NSNotFound ||
        [self isDisallowedHost:host]) {
        return NO;
    }

    NSArray *labels = [host componentsSeparatedByString:@"."];
    if ([labels count] < 2) {
        return NO;
    }

    NSCharacterSet *invalidCharacters =
        [[NSCharacterSet characterSetWithCharactersInString:
            @"abcdefghijklmnopqrstuvwxyz0123456789-"] invertedSet];
    NSCharacterSet *letters = [NSCharacterSet letterCharacterSet];

    for (NSString *label in labels) {
        if ([label length] == 0 || [label length] > 63 ||
            [label hasPrefix:@"-"] || [label hasSuffix:@"-"] ||
            [label hasPrefix:@"xn--"] ||
            [label rangeOfCharacterFromSet:invalidCharacters].location != NSNotFound) {
            return NO;
        }
    }

    NSString *topLevelLabel = [labels lastObject];
    return [topLevelLabel rangeOfCharacterFromSet:letters].location != NSNotFound;
}

+ (NSURL *)validatedEndpointURL:(NSString *)endpoint {
    if (![endpoint isKindOfClass:[NSString class]]) {
        return nil;
    }

    NSString *trimmed = [endpoint
        stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if ([trimmed length] == 0 ||
        ![trimmed canBeConvertedToEncoding:NSASCIIStringEncoding] ||
        [trimmed rangeOfCharacterFromSet:[NSCharacterSet controlCharacterSet]].location != NSNotFound ||
        [trimmed rangeOfString:@"\\"].location != NSNotFound) {
        return nil;
    }

    NSURLComponents *components = [NSURLComponents componentsWithString:trimmed];
    if (components == nil || components.scheme == nil || components.host == nil ||
        [components.scheme caseInsensitiveCompare:@"https"] != NSOrderedSame ||
        components.port != nil || components.user != nil || components.password != nil ||
        components.query != nil || components.fragment != nil ||
        ![components.percentEncodedPath isEqualToString:@"/alarm"]) {
        return nil;
    }

    NSString *host = [self canonicalHost:components.host];
    if (![self isValidPublicDNSHost:host]) {
        return nil;
    }

    components.scheme = @"https";
    components.host = host;
    return components.URL;
}

+ (NSString *)headerValue:(NSString *)name response:(NSHTTPURLResponse *)response {
    for (id key in response.allHeaderFields) {
        if ([[key description] caseInsensitiveCompare:name] == NSOrderedSame) {
            id value = [response.allHeaderFields objectForKey:key];
            return [value isKindOfClass:[NSString class]] ? value : [value description];
        }
    }
    return nil;
}

+ (BOOL)isAcceptableResponse:(NSURLResponse *)response requestURL:(NSURL *)requestURL {
    if (![response isKindOfClass:[NSHTTPURLResponse class]] || requestURL == nil) {
        return NO;
    }

    NSHTTPURLResponse *HTTPResponse = (NSHTTPURLResponse *)response;
    NSURL *responseURL = HTTPResponse.URL;
    if (responseURL == nil ||
        [responseURL.scheme caseInsensitiveCompare:requestURL.scheme] != NSOrderedSame ||
        ![[self canonicalHost:responseURL.host] isEqualToString:
            [self canonicalHost:requestURL.host]] ||
        ![responseURL.path isEqualToString:requestURL.path] ||
        responseURL.port != nil || responseURL.user != nil || responseURL.password != nil ||
        responseURL.query != nil || responseURL.fragment != nil) {
        return NO;
    }

    if (HTTPResponse.statusCode < 200 || HTTPResponse.statusCode > 299) {
        return NO;
    }

    NSString *contentLength = [self headerValue:@"Content-Length" response:HTTPResponse];
    if (contentLength != nil) {
        NSCharacterSet *nonDigits =
            [[NSCharacterSet characterSetWithCharactersInString:@"0123456789"] invertedSet];
        if ([contentLength length] == 0 ||
            [contentLength rangeOfCharacterFromSet:nonDigits].location != NSNotFound ||
            [contentLength longLongValue] > (long long)AlarmMaximumResponseBodyBytes) {
            return NO;
        }
    }

    NSString *contentType = [self headerValue:@"Content-Type" response:HTTPResponse];
    if (contentType != nil) {
        NSString *mediaType = [[contentType componentsSeparatedByString:@";"] firstObject];
        mediaType = [[mediaType
            stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]]
            lowercaseString];
        if (![mediaType isEqualToString:@"application/json"] &&
            ![mediaType isEqualToString:@"text/plain"]) {
            return NO;
        }
    }

    return YES;
}

@end

@interface AlarmResponseBodyGate ()

@property(nonatomic, strong) NSMapTable *receivedBytesByTask;

@end

@implementation AlarmResponseBodyGate

- (id)init {
    self = [super init];
    if (self != nil) {
        _receivedBytesByTask = [NSMapTable weakToStrongObjectsMapTable];
    }
    return self;
}

- (void)resetTask:(NSURLSessionDataTask *)task {
    @synchronized(self) {
        [self.receivedBytesByTask setObject:@0 forKey:task];
    }
}

- (BOOL)shouldCancelTask:(NSURLSessionDataTask *)task afterReceivingData:(NSData *)data {
    @synchronized(self) {
        NSUInteger received = [[self.receivedBytesByTask objectForKey:task] unsignedIntegerValue];
        if ([data length] > AlarmMaximumResponseBodyBytes - received) {
            [self.receivedBytesByTask removeObjectForKey:task];
            return YES;
        }

        [self.receivedBytesByTask setObject:@(received + [data length]) forKey:task];
        return NO;
    }
}

- (void)forgetTask:(NSURLSessionDataTask *)task {
    @synchronized(self) {
        [self.receivedBytesByTask removeObjectForKey:task];
    }
}

@end
