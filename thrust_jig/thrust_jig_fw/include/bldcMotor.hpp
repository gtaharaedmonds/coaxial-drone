#ifndef BLDCMOTOR_H_
#define BLDCMOTOR_H_

/* Includes */
#include "DShotESC.h"
#include <stdint.h>

/* Symbolic Constants */
#define MOTOR_1_GPIO GPIO_NUM_12
#define MOTOR_2_GPIO GPIO_NUM_13
#define MOTOR_1_RMT_CHANNEL RMT_CHANNEL_0
#define MOTOR_2_RMT_CHANNEL RMT_CHANNEL_1

#define ARM_DURATION 3000

/* Type Definitions */
enum bldcMotor_E {
    MOTOR_1,
    MOTOR_2,
    ALL
};

struct escDshotConfig_S {
    gpio_num_t gpio_pin;
    rmt_channel_t rmt_channel;
    bool reversed;
};

/* Function Definitions */
void setupBldcMotor(bldcMotor_E motor);
void armBldcMotor(bldcMotor_E motor);
void setThrottlePercent(bldcMotor_E motor, double throttle_pct);
void setThrottle(bldcMotor_E motor, uint16_t throttle);
void switchDirection(bldcMotor_E motor);
void stopBldcMotor(bldcMotor_E motor);

#endif
