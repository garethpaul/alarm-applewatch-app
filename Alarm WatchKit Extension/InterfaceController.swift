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
private let minimumAlarmHour = 5
private let maximumAlarmHour = 11
private let alarmRequestTimeout: NSTimeInterval = 10.0
private let alarmResourceTimeout: NSTimeInterval = 15.0
private let alarmResponseBodyGate = AlarmResponseBodyGate()
private let alarmRequestManager: Manager = {
    let configuration = NSURLSessionConfiguration.ephemeralSessionConfiguration()
    configuration.HTTPShouldSetCookies = false
    configuration.HTTPCookieStorage = nil
    configuration.URLCredentialStorage = nil
    configuration.URLCache = nil
    configuration.HTTPAdditionalHeaders = Manager.defaultHTTPHeaders
    configuration.timeoutIntervalForRequest = alarmRequestTimeout
    configuration.timeoutIntervalForResource = alarmResourceTimeout
    let manager = Manager(configuration: configuration)
    manager.delegate.taskWillPerformHTTPRedirection = {
        (_, _, _, _) in
        return nil
    }
    manager.delegate.dataTaskDidReceiveResponse = {
        (_, dataTask, response) in
        if let requestURL = dataTask.originalRequest?.URL {
            if AlarmNetworkPolicy.isAcceptableResponse(response, requestURL: requestURL) {
                alarmResponseBodyGate.resetTask(dataTask)
                return .Allow
            }
        }
        return .Cancel
    }
    manager.delegate.dataTaskDidReceiveData = {
        (_, dataTask, data) in
        if alarmResponseBodyGate.shouldCancelTask(dataTask, afterReceivingData: data) {
            dataTask.cancel()
        }
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

func alarmEndpointURL() -> String? {
    if let endpoint = NSBundle.mainBundle().objectForInfoDictionaryKey("AlarmEndpointURL") as? String {
        if let URL = AlarmNetworkPolicy.validatedEndpointURL(endpoint) {
            return URL.absoluteString
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
                if let dataTask = request.task as? NSURLSessionDataTask {
                    alarmResponseBodyGate.forgetTask(dataTask)
                }
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
