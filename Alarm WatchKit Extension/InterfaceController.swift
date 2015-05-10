//
//  InterfaceController.swift
//  AlarmClock WatchKit Extension
//
//  Created by Gareth on 5/9/15.
//

import WatchKit
import Foundation
import Alamofire

class InterfaceController: WKInterfaceController {
    
    var wakeUp = 5
    
    @IBOutlet weak var slider: WKInterfaceSlider!
    
    @IBOutlet weak var alarmValue: WKInterfaceLabel!
    
    @IBAction func update(value: Float) {
        wakeUp = Int(value)
        alarmValue.setText("\(wakeUp) am")
    }
    
    @IBAction func setAlarm() {
        // Send HTTP Request to Set Alarm
        Alamofire.request(.GET, "http://myhome.com/alarm", parameters: ["alarmTime": String(wakeUp)])
    }
    
    override func awakeWithContext(context: AnyObject?) {
        super.awakeWithContext(context)
        // Configure interface objects here.
        alarmValue.setText("\(wakeUp) am")
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
