#include "bldcMotor.hpp"

static escDshotConfig_S motor1Config = {
    .gpio_pin = MOTOR_1_GPIO,
    .rmt_channel = MOTOR_1_RMT_CHANNEL
};

static escDshotConfig_S motor2Config = {
    .gpio_pin = MOTOR_2_GPIO,
    .rmt_channel = MOTOR_2_RMT_CHANNEL
};

static DShotESC motor1Esc;
static DShotESC motor2Esc;

void setupBldcMotor(bldcMotor_E motor) {

}

void setThrottlePercent(bldcMotor_E motor, double throttle_pct) {

}


void setThrottle(bldcMotor_E motor, uint16_t throttle) {

}

void switchDirection(bldcMotor_E motor) {

}

void stopBldcMotor(bldcMotor_E motor) {

}