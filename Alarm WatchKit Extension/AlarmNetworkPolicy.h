#import <Foundation/Foundation.h>

FOUNDATION_EXPORT NSUInteger const AlarmMaximumResponseBodyBytes;

@interface AlarmNetworkPolicy : NSObject

+ (NSURL *)validatedEndpointURL:(NSString *)endpoint;
+ (BOOL)isAcceptableResponse:(NSURLResponse *)response requestURL:(NSURL *)requestURL;

@end

@interface AlarmResponseBodyGate : NSObject

- (void)resetTask:(NSURLSessionDataTask *)task;
- (BOOL)shouldCancelTask:(NSURLSessionDataTask *)task afterReceivingData:(NSData *)data;
- (void)forgetTask:(NSURLSessionDataTask *)task;

@end
