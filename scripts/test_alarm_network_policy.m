#import <Foundation/Foundation.h>

#import "../Alarm WatchKit Extension/AlarmNetworkPolicy.h"

static NSUInteger failures = 0;

static NSHTTPURLResponse *Response(NSURL *URL,
                                   NSInteger statusCode,
                                   NSDictionary *headers);

@interface AlarmFakeURLProtocol : NSURLProtocol

+ (void)setStatusCode:(NSInteger)statusCode
               headers:(NSDictionary *)headers
                  body:(NSData *)body;

@end


static NSInteger fakeStatusCode = 204;
static NSDictionary *fakeHeaders = nil;
static NSData *fakeBody = nil;

@implementation AlarmFakeURLProtocol

+ (BOOL)canInitWithRequest:(NSURLRequest *)request {
    return [[[request URL] host] isEqualToString:@"api.example.com"];
}

+ (NSURLRequest *)canonicalRequestForRequest:(NSURLRequest *)request {
    return request;
}

+ (void)setStatusCode:(NSInteger)statusCode
               headers:(NSDictionary *)headers
                  body:(NSData *)body {
    fakeStatusCode = statusCode;
    fakeHeaders = [headers copy];
    fakeBody = [body copy];
}

- (void)startLoading {
    NSHTTPURLResponse *response = Response(
        [[self request] URL], fakeStatusCode, fakeHeaders ?: @{});
    [[self client] URLProtocol:self
           didReceiveResponse:response
           cacheStoragePolicy:NSURLCacheStorageNotAllowed];
    if ([fakeBody length] > 0) {
        [[self client] URLProtocol:self didLoadData:fakeBody];
    }
    [[self client] URLProtocolDidFinishLoading:self];
}

- (void)stopLoading {
}

@end


@interface AlarmFakeSessionDelegate : NSObject <NSURLSessionDataDelegate>

@property(nonatomic, strong) AlarmResponseBodyGate *gate;
@property(nonatomic) NSUInteger completionCount;
@property(nonatomic, strong) NSError *completionError;
@property(nonatomic) dispatch_semaphore_t semaphore;

@end

@implementation AlarmFakeSessionDelegate

- (id)init {
    self = [super init];
    if (self != nil) {
        _gate = [[AlarmResponseBodyGate alloc] init];
        _semaphore = dispatch_semaphore_create(0);
    }
    return self;
}

- (void)URLSession:(NSURLSession *)session
          dataTask:(NSURLSessionDataTask *)dataTask
didReceiveResponse:(NSURLResponse *)response
 completionHandler:(void (^)(NSURLSessionResponseDisposition disposition))completionHandler {
    if ([AlarmNetworkPolicy isAcceptableResponse:response
                                      requestURL:[[dataTask originalRequest] URL]]) {
        [self.gate resetTask:dataTask];
        completionHandler(NSURLSessionResponseAllow);
    } else {
        completionHandler(NSURLSessionResponseCancel);
    }
}

- (void)URLSession:(NSURLSession *)session
          dataTask:(NSURLSessionDataTask *)dataTask
    didReceiveData:(NSData *)data {
    if ([self.gate shouldCancelTask:dataTask afterReceivingData:data]) {
        [dataTask cancel];
    }
}

- (void)URLSession:(NSURLSession *)session
              task:(NSURLSessionTask *)task
didCompleteWithError:(NSError *)error {
    self.completionCount += 1;
    self.completionError = error;
    [self.gate forgetTask:(NSURLSessionDataTask *)task];
    dispatch_semaphore_signal(self.semaphore);
}

@end

static void Require(BOOL condition, NSString *message) {
    if (!condition) {
        failures += 1;
        fprintf(stderr, "FAIL: %s\n", [message UTF8String]);
    }
}

static void RequireRejectedEndpoint(NSString *endpoint) {
    Require([AlarmNetworkPolicy validatedEndpointURL:endpoint] == nil,
            [NSString stringWithFormat:@"endpoint should be rejected: %@", endpoint]);
}

static NSHTTPURLResponse *Response(NSURL *URL,
                                   NSInteger statusCode,
                                   NSDictionary *headers) {
    return [[NSHTTPURLResponse alloc] initWithURL:URL
                                      statusCode:statusCode
                                     HTTPVersion:@"HTTP/1.1"
                                    headerFields:headers];
}

static NSURLSessionDataTask *SuspendedTask(NSURL *URL) {
    NSURLSessionConfiguration *configuration =
        [NSURLSessionConfiguration ephemeralSessionConfiguration];
    NSURLSession *session = [NSURLSession sessionWithConfiguration:configuration];
    return [session dataTaskWithURL:URL];
}

static void TestEndpointValidation(void) {
    NSURL *URL = [AlarmNetworkPolicy
        validatedEndpointURL:@"  HTTPS://API.EXAMPLE.COM./alarm  "];
    Require(URL != nil, @"public HTTPS endpoint should be accepted");
    Require([[URL absoluteString] isEqualToString:@"https://api.example.com/alarm"],
            @"accepted endpoints should be canonicalized");

    NSArray *rejected = @[
        @"http://api.example.com/alarm",
        @"https://example.invalid/alarm",
        @"https://nested.example.invalid/alarm",
        @"https://localhost/alarm",
        @"https://service.local/alarm",
        @"https://service.internal/alarm",
        @"https://service.home.arpa/alarm",
        @"https://127.0.0.1/alarm",
        @"https://2130706433/alarm",
        @"https://0x7f000001/alarm",
        @"https://0177.0.0.1/alarm",
        @"https://[::1]/alarm",
        @"https://169.254.169.254/alarm",
        @"https://éxample.com/alarm",
        @"https://xn--xample-9ua.com/alarm",
        @"https://api.example.com:443/alarm",
        @"https://user:password@api.example.com/alarm",
        @"https://api.example.com/%61larm",
        @"https://api.example.com/alarm?next=/private",
        @"https://api.example.com/alarm#fragment",
        @"https://api.example.com/alarm/../alarm",
        @"https://api.example.com\\@127.0.0.1/alarm",
        @"https://singlelabel/alarm",
        @"https://-api.example.com/alarm",
        @"https://api_.example.com/alarm"
    ];

    for (NSString *endpoint in rejected) {
        RequireRejectedEndpoint(endpoint);
    }
}

static void TestResponseValidation(void) {
    NSURL *requestURL = [NSURL URLWithString:@"https://api.example.com/alarm"];

    Require([AlarmNetworkPolicy
                isAcceptableResponse:Response(requestURL, 204, @{})
                           requestURL:requestURL],
            @"empty 204 response should be accepted");
    Require([AlarmNetworkPolicy
                isAcceptableResponse:Response(
                    requestURL,
                    200,
                    @{@"Content-Type" : @"application/json; charset=utf-8",
                      @"Content-Length" : @"2"})
                           requestURL:requestURL],
            @"small JSON response should be accepted");

    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(requestURL, 500, @{})
                            requestURL:requestURL],
            @"non-2xx response should be rejected");
    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(
                     requestURL, 200, @{@"Content-Type" : @"text/html"})
                            requestURL:requestURL],
            @"declared HTML response should be rejected");
    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(
                     requestURL,
                     200,
                     @{@"Content-Type" : @"application/json",
                       @"Content-Length" : @"4097"})
                            requestURL:requestURL],
            @"oversized declared response should be rejected");
    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(
                     requestURL,
                     200,
                     @{@"Content-Type" : @"application/json",
                       @"Content-Length" : @"2, 2"})
                            requestURL:requestURL],
            @"ambiguous content length should be rejected");
    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(
                     requestURL,
                     200,
                     @{@"Content-Type" : @"application/json",
                       @"Content-Length" : @"٢"})
                            requestURL:requestURL],
            @"non-ASCII content length should be rejected");
    Require(![AlarmNetworkPolicy
                 isAcceptableResponse:Response(
                     [NSURL URLWithString:@"https://other.example.com/alarm"],
                     200,
                     @{@"Content-Type" : @"application/json"})
                            requestURL:requestURL],
            @"response URL drift should be rejected");
}

static void TestResponseBodyGate(void) {
    NSURL *URL = [NSURL URLWithString:@"https://api.example.com/alarm"];
    NSURLSessionDataTask *task = SuspendedTask(URL);
    AlarmResponseBodyGate *gate = [[AlarmResponseBodyGate alloc] init];
    NSData *boundary = [NSMutableData dataWithLength:AlarmMaximumResponseBodyBytes];
    NSData *oneByte = [NSData dataWithBytes:"x" length:1];

    [gate resetTask:task];
    Require(![gate shouldCancelTask:task afterReceivingData:boundary],
            @"body exactly at the limit should be accepted");
    Require([gate shouldCancelTask:task afterReceivingData:oneByte],
            @"body above the limit should cancel");
    [gate forgetTask:task];

    [gate resetTask:task];
    Require(![gate shouldCancelTask:task afterReceivingData:oneByte],
            @"forgotten task should not retain previous byte counts");
    [task cancel];
}

static void TestEphemeralConfiguration(void) {
    NSURLSessionConfiguration *configuration =
        [NSURLSessionConfiguration ephemeralSessionConfiguration];
    configuration.HTTPShouldSetCookies = NO;
    configuration.HTTPCookieStorage = nil;
    configuration.URLCredentialStorage = nil;
    configuration.URLCache = nil;

    Require(!configuration.HTTPShouldSetCookies,
            @"ephemeral alarm session should not set cookies");
    Require(configuration.HTTPCookieStorage == nil,
            @"ephemeral alarm session should not retain cookie storage");
    Require(configuration.URLCredentialStorage == nil,
            @"ephemeral alarm session should not retain credentials");
    Require(configuration.URLCache == nil,
            @"ephemeral alarm session should not retain cache data");
}

static AlarmFakeSessionDelegate *RunFakeRequest(NSData *body,
                                                NSDictionary *headers) {
    [AlarmFakeURLProtocol setStatusCode:200 headers:headers body:body];
    NSURLSessionConfiguration *configuration =
        [NSURLSessionConfiguration ephemeralSessionConfiguration];
    configuration.protocolClasses = @[[AlarmFakeURLProtocol class]];
    configuration.HTTPShouldSetCookies = NO;
    configuration.HTTPCookieStorage = nil;
    configuration.URLCredentialStorage = nil;
    configuration.URLCache = nil;
    AlarmFakeSessionDelegate *delegate = [[AlarmFakeSessionDelegate alloc] init];
    NSURLSession *session = [NSURLSession sessionWithConfiguration:configuration
                                                          delegate:delegate
                                                     delegateQueue:nil];
    NSURLSessionDataTask *task =
        [session dataTaskWithURL:[NSURL URLWithString:@"https://api.example.com/alarm"]];
    [task resume];
    long result = dispatch_semaphore_wait(
        delegate.semaphore,
        dispatch_time(DISPATCH_TIME_NOW, (int64_t)(5 * NSEC_PER_SEC)));
    Require(result == 0, @"fake network request should finish within five seconds");
    [session invalidateAndCancel];
    return delegate;
}

static void TestFakeNetworkBoundaries(void) {
    AlarmFakeSessionDelegate *valid = RunFakeRequest(
        [@"{}" dataUsingEncoding:NSUTF8StringEncoding],
        @{@"Content-Type" : @"application/json"});
    Require(valid.completionCount == 1,
            @"valid fake response should complete exactly once");
    Require(valid.completionError == nil,
            @"valid fake response should complete without error");

    NSData *oversized = [NSMutableData
        dataWithLength:AlarmMaximumResponseBodyBytes + 1];
    AlarmFakeSessionDelegate *rejected = RunFakeRequest(
        oversized,
        @{@"Content-Type" : @"application/json"});
    Require(rejected.completionCount == 1,
            @"oversized fake response should complete exactly once");
    Require(rejected.completionError != nil,
            @"oversized fake response should be cancelled");
}

int main(void) {
    @autoreleasepool {
        TestEndpointValidation();
        TestResponseValidation();
        TestResponseBodyGate();
        TestEphemeralConfiguration();
        TestFakeNetworkBoundaries();
    }

    if (failures != 0) {
        fprintf(stderr, "%lu alarm network policy tests failed\n",
                (unsigned long)failures);
        return 1;
    }

    puts("Alarm native network policy tests passed.");
    return 0;
}
