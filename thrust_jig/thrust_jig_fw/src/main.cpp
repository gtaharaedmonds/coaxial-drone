#include <stdint.h>

#include "HX711.h"
#include "bldcMotor.hpp"
#include "loadCell.hpp"

void setup()
{
    Serial.begin(115200);
    Serial.println("Thrust Jig Firmware Program");

    Serial.println("Setting up Motor");
    setupBldcMotor(MOTOR_2);
    delay(100);

    Serial.println("Arming Motor");
    armBldcMotor(MOTOR_2);
}

static int loop_i = 0;

void loop()
{
    if (loop_i < 10000) {
        setThrottle(MOTOR_2, 50);
    }
    else if (loop_i == 10000) {
        stopBldcMotor(MOTOR_2);
    }
    
    loop_i++;
    delay(1);
}