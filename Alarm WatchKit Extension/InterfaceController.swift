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
    return normalizedAlarmHour(Int(value))
}

func alarmDisplayText(hour: Int) -> String {
    return "\(normalizedAlarmHour(hour)) am"
}

func alarmEndpointURL() -> String? {
    if let endpoint = NSBundle.mainBundle().objectForInfoDictionaryKey("AlarmEndpointURL") as? String {
        let trimmedEndpoint = endpoint.stringByTrimmingCharactersInSet(NSCharacterSet.whitespaceAndNewlineCharacterSet())
        if count(trimmedEndpoint) > 0 && trimmedEndpoint.hasPrefix("https://") {
            return trimmedEndpoint
        }
    }

    return nil
}

class InterfaceController: WKInterfaceController {
    
    var wakeUp = 5
    
    @IBOutlet weak var slider: WKInterfaceSlider!
    
    @IBOutlet weak var alarmValue: WKInterfaceLabel!
    
    @IBAction func update(value: Float) {
        wakeUp = normalizedAlarmHour(value)
        alarmValue.setText(alarmDisplayText(wakeUp))
    }
    
    @IBAction func setAlarm() {
        if let endpoint = alarmEndpointURL() {
            Alamofire.request(.GET, endpoint, parameters: alarmParameters())
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
        alarmValue.setText(alarmDisplayText(wakeUp))
    }
    
    override func willActivate() {
        // This method is called when watch view controller is about to be visible to user
        super.willActivate()
    }
    
    override func didDeactivate() {
        // This method is called when watch view controller is no longer visible
        super.didDeactivate()
    }
    
}
