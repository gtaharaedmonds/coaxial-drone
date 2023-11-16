#include <stdint.h>

#include "bldcMotor.hpp"
#include "servoMotor.hpp"
#include "loadCell.hpp"
#include "powerMonitor.hpp"
#include "serialProtocol.hpp"

void setup()
{
    Serial.begin(115200);
    Serial.println("Thrust Jig Firmware Program");

    Serial.println("Setting up");
    setupBldcMotor(MOTOR_1);
    setupBldcMotor(MOTOR_2);
    setupServo(PITCH_VANE);
    setupServo(ROLL_VANE);
    setupLoadCell(THRUST);
    setupLoadCell(TORQUE);
    setupPowerMonitor();
}

enum ProgramState_E {
    SETUP_TEST,
    RUN_TEST
};
static ProgramState_E state = SETUP_TEST;
static unsigned long start_time_micros = 0;
static unsigned long start_time_millis = 0;
static CommandSet_S current_command;
static String input = "";

void loop()
{
    switch (state)
    {
    case SETUP_TEST:
        receiveTestSpec();
        armBldcMotor(ALL);
        start_time_micros = micros();
        start_time_millis = millis();
        Serial.println("Starting test");
        Serial.println("time_us,top_rpm,bot_rpm,v_bat,i_bat,i_top,i_bot,thrust_N,torque_Nm");
        state = RUN_TEST;
        break;
    
    case RUN_TEST:
        if (test_spec.size() > 1 && test_spec.at(1).time_ms < millis() - start_time_millis) {
            test_spec.pop_front();
        }
        current_command = test_spec.front();
        setThrottlePercent(MOTOR_1, current_command.top_percent);
        setThrottlePercent(MOTOR_2, current_command.bot_percent);
        setServoPwm(PITCH_VANE, current_command.pitch_us);
        setServoPwm(ROLL_VANE, current_command.roll_us);
        Serial.printf(
            "%lu,%" PRIu16 ",%" PRIu16 ",%f,%f,%f,%f,%f,%f\n",
            micros() - start_time_micros,
            getRpm(MOTOR_1),
            getRpm(MOTOR_2),
            getVoltageV(VBAT),
            getCurrentA(IBAT),
            getCurrentA(IMOTOR1),
            getCurrentA(IMOTOR2),
            getLoadCellValue(THRUST),
            getLoadCellValue(TORQUE)
        );
        // Nonblocking string read persistent over multiple loop iterations
        while (Serial.available()) {
            char c = Serial.read();
            if (c == '\n' && input != "Stop") {
                input.clear();
            } else if (c >= 0) {
                input += c;
            }
        }
        if (test_spec.size() <= 1 || input == "Stop\n") {
            input = "";
            stopBldcMotor(ALL);
            setServoPwm(PITCH_VANE, 1500);
            setServoPwm(ROLL_VANE, 1500);
            state = SETUP_TEST;
            Serial.println("Stopped");
        }
        delay(1);
        break;
    }
}