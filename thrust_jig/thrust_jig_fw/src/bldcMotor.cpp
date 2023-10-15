#include "bldcMotor.hpp"

static escDshotConfig_S motor1Config = {
    .gpio_pin = MOTOR_1_GPIO,
    .rmt_channel = MOTOR_1_RMT_CHANNEL,
    .reversed = false
};

static escDshotConfig_S motor2Config = {
    .gpio_pin = MOTOR_2_GPIO,
    .rmt_channel = MOTOR_2_RMT_CHANNEL,
    .reversed = true
};

static DShotESC motor1Esc;
static DShotESC motor2Esc;

void setupBldcMotor(bldcMotor_E motor) {
    switch (motor) {
        case MOTOR_1:
            motor1Esc.install(motor1Config.gpio_pin, motor1Config.rmt_channel);
            motor1Esc.init();
            motor1Esc.setReversed(motor1Config.reversed);
            motor1Esc.beep(1);
            break;
        case MOTOR_2:
            motor2Esc.install(motor2Config.gpio_pin, motor2Config.rmt_channel);
            motor2Esc.init();
            motor2Esc.setReversed(motor2Config.reversed);
            motor2Esc.beep(1);
            break;
        default:
            break;
    }
}

void armBldcMotor(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            motor1Esc.throttleArm(ARM_DURATION);
            break;

        case MOTOR_2:
            motor2Esc.throttleArm(ARM_DURATION);
            break;

        default:
            break;
    }
}

void setThrottlePercent(bldcMotor_E motor, double throttle_pct) {
    uint16_t throttle = (uint16_t) (throttle_pct / 100.0 * 2000);
    
    switch (motor){
        case MOTOR_1:
            motor1Esc.sendThrottle(throttle);
            break;

        case MOTOR_2:
            motor2Esc.sendThrottle(throttle);
            break;

        default:
            break;
    }
}


void setThrottle(bldcMotor_E motor, uint16_t throttle) {
    switch (motor){
        case MOTOR_1:
            motor1Esc.sendThrottle(throttle);
            break;

        case MOTOR_2:
            motor2Esc.sendThrottle(throttle);
            break;

        default:
            break;
    }
}

void switchDirection(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            motor1Config.reversed = !(motor1Config.reversed);
            motor1Esc.setReversed(motor1Config.reversed);
            break;

        case MOTOR_2:
            motor2Config.reversed = !(motor2Config.reversed);
            motor2Esc.setReversed(motor2Config.reversed);
            break;

        default:
            break;
    }
}

void stopBldcMotor(bldcMotor_E motor) {
    switch (motor){
        case MOTOR_1:
            motor1Esc.sendMotorStop();
            break;

        case MOTOR_2:
            motor2Esc.sendMotorStop();
            break;

        case ALL:
            motor1Esc.sendMotorStop();
            motor2Esc.sendMotorStop();

        default:
            break;
    }
}