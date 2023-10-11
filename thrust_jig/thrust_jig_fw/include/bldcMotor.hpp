#ifndef BLDCMOTOR_H_
#define BLDCMOTOR_H_

/* Includes */
#include "DShotESC.h"
#include <stdint.h>

/* Symbolic Constants */
#define MOTOR_1_GPIO 5
#define MOTOR_2_GPIO 6
#define MOTOR_1_RMT_CHANNEL 0
#define MOTOR_2_RMT_CHANNEL 1

/* Type Definitions */
enum bldcMotor_E {
    MOTOR_1,
    MOTOR_2
};

struct escDshotConfig_S {
    uint8_t gpio_pin;
    uint8_t rmt_channel;
};

/* Function Definitions */
void setupBldcMotor(bldcMotor_E motor);
void setThrottlePercent(bldcMotor_E motor, double throttle_pct);
void setThrottle(bldcMotor_E motor, uint16_t throttle);
void switchDirection(bldcMotor_E motor);
void stopBldcMotor(bldcMotor_E motor);

#endif
