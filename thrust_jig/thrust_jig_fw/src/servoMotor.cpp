#include "servoMotor.hpp"

static ServoConfig_S pitchVaneConfig = {
    .gpio_pin = PITCH_VANE_GPIO,
    .min_pwm_us = PITCH_VANE_MIN_US,
    .max_pwm_us = PITCH_VANE_MAX_US,
    .trim_pwm_us = PITCH_VANE_TRIM_US,
    .reversed = PITCH_VANE_REVERSED
};

static ServoConfig_S rollVaneConfig = {
    .gpio_pin = ROLL_VANE_GPIO,
    .min_pwm_us = ROLL_VANE_MIN_US,
    .max_pwm_us = ROLL_VANE_MAX_US,
    .trim_pwm_us = ROLL_VANE_TRIM_US,
    .reversed = ROLL_VANE_REVERSED
};

static Servo pitchVaneServo;
static Servo rollVaneServo;

void setupServo(ServoMotor_E servo) {
    switch (servo) {
        case PITCH_VANE:
            pitchVaneServo.attach(pitchVaneConfig.gpio_pin, 1000, 2000);
            break;
        case ROLL_VANE:
            rollVaneServo.attach(rollVaneConfig.gpio_pin, 1000, 2000);
            break;
        default:
            break;
    }
}

void setServoPwm(ServoMotor_E servo, int pwm_us) {
    Servo servoOut;
    ServoConfig_S conf;

    switch (servo) {
        case PITCH_VANE:
            servoOut = pitchVaneServo;
            conf = pitchVaneConfig;
            break;
        case ROLL_VANE:
            servoOut = rollVaneServo;
            conf = rollVaneConfig;
            break;
        default:
            return;
    }

    if (pwm_us < 1500) {
        servoOut.writeMicroseconds(
            conf.trim_pwm_us + (pwm_us - 1500)
            * (conf.trim_pwm_us - conf.min_pwm_us) / 500
        );
    } else {
        servoOut.writeMicroseconds(
            conf.trim_pwm_us + (pwm_us - 1500)
            * (conf.max_pwm_us - conf.trim_pwm_us) / 500
        );
    }
}