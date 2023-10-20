#include "bldcMotor.hpp"

static escDshotConfig_S motor1Config = {
    .gpio_pin = MOTOR_1_GPIO,
    .reversed = false
};

static escDshotConfig_S motor2Config = {
    .gpio_pin = MOTOR_2_GPIO,
    .reversed = true
};

static DShotRMT motor1Esc(MOTOR_1_GPIO);
static DShotRMT motor2Esc(MOTOR_2_GPIO);

void setupBldcMotor(bldcMotor_E motor) {
    switch (motor) {
        case MOTOR_1:
            motor1Esc.begin(DSHOT300, ENABLE_BIDIRECTION);
            repeatCommand(motor, motor1Config.reversed ? DSHOT_CMD_SPIN_DIRECTION_REVERSED : DSHOT_CMD_SPIN_DIRECTION_NORMAL, 10);
            motor1Esc.send_dshot_value(DSHOT_CMD_BEEP2);
            vTaskDelay(260 / portTICK_PERIOD_MS);
            break;
        case MOTOR_2:
            motor2Esc.begin(DSHOT300, ENABLE_BIDIRECTION);
            repeatCommand(motor, motor2Config.reversed ? DSHOT_CMD_SPIN_DIRECTION_REVERSED : DSHOT_CMD_SPIN_DIRECTION_NORMAL, 10);
            motor2Esc.send_dshot_value(DSHOT_CMD_BEEP2);
            vTaskDelay(260 / portTICK_PERIOD_MS);
            break;
        default:
            break;
    }
}

void armBldcMotor(bldcMotor_E motor) {
    repeatCommandTicks(motor, DSHOT_THROTTLE_ZERO, ARM_DURATION / portTICK_PERIOD_MS);
}

void setThrottlePercent(bldcMotor_E motor, double throttle_pct) {
    uint16_t throttle = (uint16_t) (throttle_pct / 100.0 * 2000);
    setThrottle(motor, throttle);
}


void setThrottle(bldcMotor_E motor, uint16_t throttle) {
    switch (motor){
        case MOTOR_1:
            motor1Esc.send_dshot_value(DSHOT_THROTTLE_ZERO + throttle);
            break;

        case MOTOR_2:
            motor2Esc.send_dshot_value(DSHOT_THROTTLE_ZERO + throttle);
            break;

        default:
            break;
    }
}

void switchDirection(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            motor1Config.reversed = !(motor1Config.reversed);
            repeatCommand(motor, motor1Config.reversed ? DSHOT_CMD_SPIN_DIRECTION_REVERSED : DSHOT_CMD_SPIN_DIRECTION_NORMAL, 10);
            break;

        case MOTOR_2:
            motor2Config.reversed = !(motor2Config.reversed);
            repeatCommand(motor, motor2Config.reversed ? DSHOT_CMD_SPIN_DIRECTION_REVERSED : DSHOT_CMD_SPIN_DIRECTION_NORMAL, 10);
            break;

        default:
            break;
    }
}

void stopBldcMotor(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            motor1Esc.send_dshot_value(DSHOT_CMD_MOTOR_STOP);
            break;

        case MOTOR_2:
            motor2Esc.send_dshot_value(DSHOT_CMD_MOTOR_STOP);
            break;

        case ALL:
            motor1Esc.send_dshot_value(DSHOT_CMD_MOTOR_STOP);
            motor2Esc.send_dshot_value(DSHOT_CMD_MOTOR_STOP);

        default:
            break;
    }
}

uint16_t getRpm(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            return motor1Esc.get_dshot_RPM();
            break;

        case MOTOR_2:
            return motor2Esc.get_dshot_RPM();
            break;

        default:
            return 0;
            break;
    }
}

void repeatCommand(bldcMotor_E motor, uint16_t command, uint8_t repeat) {
    switch (motor) {
        case MOTOR_1:
        	for (int i = 0; i < repeat; i++)
            {
                motor1Esc.send_dshot_value(command);
            }
            break;
        case MOTOR_2:
        	for (int i = 0; i < repeat; i++)
            {
                motor2Esc.send_dshot_value(command);
            }
            break;
        case ALL:
        	for (int i = 0; i < repeat; i++)
            {
                motor1Esc.send_dshot_value(command);
                motor2Esc.send_dshot_value(command);
            }
            break;
        default:
            break;
    }
}

void repeatCommandTicks(bldcMotor_E motor, uint16_t command, TickType_t ticks)
{
	TickType_t repeatStop = xTaskGetTickCount() + ticks;
    switch (motor) {
        case MOTOR_1:
            do 
            {
                motor1Esc.send_dshot_value(command);
                vTaskDelay(1);
            }
            while (xTaskGetTickCount() < repeatStop);
            break;
        case MOTOR_2:
        	do 
            {
                motor2Esc.send_dshot_value(command);
                vTaskDelay(1);
            }
            while (xTaskGetTickCount() < repeatStop);
            break;
        case ALL:
        	do 
            {
                motor1Esc.send_dshot_value(command);
                motor2Esc.send_dshot_value(command);
                vTaskDelay(1);
            }
            while (xTaskGetTickCount() < repeatStop);
            break;
        default:
            break;
    }
}