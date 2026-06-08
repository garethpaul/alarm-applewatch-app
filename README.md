# Alarm Apple Watch App

Legacy Swift/WatchKit alarm sample. The watch extension lets a user choose an
alarm hour and sends that value to the configured alarm endpoint.

## Toolchain

This project was created with an early Swift and WatchKit toolchain and uses a
CocoaPods-era workspace:

- Open and build `Alarm.xcworkspace`, not `Alarm.xcodeproj`.
- CocoaPods is required to restore Alamofire.
- `Podfile.lock` records Alamofire 1.2.1 and CocoaPods 0.37.0 beta-era state.

Install dependencies before opening the workspace:

```sh
pod install
```

## Verify

List schemes:

```sh
xcodebuild -list -workspace Alarm.xcworkspace
```

Run the app test target with an available simulator destination:

```sh
xcodebuild test \
  -workspace Alarm.xcworkspace \
  -scheme Alarm \
  -destination 'platform=iOS Simulator,name=iPhone 6'
```

This environment does not currently provide `xcodebuild` or `pod`, so local
verification is limited to source review and git checks until the Apple
toolchain is installed.

## Modernization Notes

The WatchKit extension still uses a hardcoded plain HTTP endpoint and
Alamofire 1.2.1. A future pass should move the endpoint to configuration,
prefer HTTPS, update the dependency stack, and replace placeholder XCTest
coverage with tests around extracted app behavior.
