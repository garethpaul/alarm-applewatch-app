//
//  InterfaceController.swift
//  AlarmClock WatchKit Extension
//
//  Created by Gareth on 5/9/15.
//

import WatchKit
import Foundation
import Alamofire

private let alarmTimeParameter = "alarmTime"
private let alarmEndpointPath = "/alarm"
private let placeholderAlarmHost = "example.invalid"
private let minimumAlarmHour = 5
private let maximumAlarmHour = 11
private let alarmRequestManager: Manager = {
    let configuration = NSURLSessionConfiguration.defaultSessionConfiguration()
    configuration.HTTPAdditionalHeaders = Manager.defaultHTTPHeaders
    let manager = Manager(configuration: configuration)
    manager.delegate.taskWillPerformHTTPRedirection = {
        (_, _, _, _) in
        return nil
    }
    return manager
}()

func normalizedAlarmHour(hour: Int) -> Int {
    if hour < minimumAlarmHour {
        return minimumAlarmHour
    }

    if hour > maximumAlarmHour {
        return maximumAlarmHour
    }

    return hour
}

func normalizedAlarmHour(value: Float) -> Int {
    if value != value {
        return minimumAlarmHour
    }

    if value < Float(minimumAlarmHour) {
        return minimumAlarmHour
    }

    if value > Float(maximumAlarmHour) {
        return maximumAlarmHour
    }

    return normalizedAlarmHour(Int(value))
}

func alarmDisplayText(hour: Int) -> String {
    return "\(normalizedAlarmHour(hour)) am"
}

func canonicalAlarmHost(host: String) -> String {
    return host.lowercaseString.stringByTrimmingCharactersInSet(NSCharacterSet(charactersInString: "."))
}

func canonicalAlarmScheme(scheme: String) -> String {
    return scheme.lowercaseString
}

func isPlaceholderAlarmHost(host: String) -> Bool {
    let canonicalHost = canonicalAlarmHost(host)
    return canonicalHost == placeholderAlarmHost ||
        canonicalHost.hasSuffix("." + placeholderAlarmHost)
}

func alarmEndpointURL() -> String? {
    if let endpoint = NSBundle.mainBundle().objectForInfoDictionaryKey("AlarmEndpointURL") as? String {
        let trimmedEndpoint = endpoint.stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())
        if count(trimmedEndpoint) > 0 {
            if let url = NSURL(string: trimmedEndpoint) {
                if let host = url.host {
                    if let scheme = url.scheme {
                        if let path = url.path {
                            if canonicalAlarmScheme(scheme) == "https" &&
                                count(host) > 0 &&
                                !isPlaceholderAlarmHost(host) &&
                                path == alarmEndpointPath &&
                                url.port == nil &&
                                url.user == nil &&
                                url.password == nil &&
                                url.query == nil &&
                                url.fragment == nil {
                                return trimmedEndpoint
                            }
                        }
                    }
                }
            }
        }
    }

    return nil
}

class InterfaceController: WKInterfaceController {
    
    var wakeUp = 5
    private var alarmRequest: Request?
    
    @IBOutlet weak var slider: WKInterfaceSlider?
    
    @IBOutlet weak var alarmValue: WKInterfaceLabel?
    
    @IBAction func update(value: Float) {
        wakeUp = normalizedAlarmHour(value)
        alarmValue?.setText(alarmDisplayText(wakeUp))
    }
    
    @IBAction func setAlarm() {
        alarmRequest?.cancel()
        alarmRequest = nil

        if let endpoint = alarmEndpointURL() {
            let request = alarmRequestManager.request(.POST, endpoint, parameters: alarmParameters())
            alarmRequest = request
            request.validate().response { [weak self] (_, _, _, error) in
                if let controller = self {
                    if controller.alarmRequest === request {
                        controller.alarmRequest = nil
                        if error != nil {
                            NSLog("Alarm submission failed.")
                        }
                    }
                }
            }
        } else {
            NSLog("Alarm endpoint is not configured; skipping alarm request.")
        }
    }

    func alarmParameters() -> [String: String] {
        return [alarmTimeParameter: String(normalizedAlarmHour(wakeUp))]
    }
    
    override func awakeWithContext(context: AnyObject?) {
        super.awakeWithContext(context)
        // Configure interface objects here.
        alarmValue?.setText(alarmDisplayText(wakeUp))
    }
    
    override func willActivate() {
        // This method is called when watch view controller is about to be visible to user
        super.willActivate()
    }
    
    override func didDeactivate() {
        // This method is called when watch view controller is no longer visible
        alarmRequest?.cancel()
        alarmRequest = nil
        super.didDeactivate()
    }
    
}
