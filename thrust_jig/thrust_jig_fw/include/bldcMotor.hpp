#ifndef BLDCMOTOR_H_
#define BLDCMOTOR_H_

/* Includes */
#include <DShotRMT.h>
#include <stdint.h>

/* Symbolic Constants */
#define MOTOR_1_GPIO GPIO_NUM_12
#define MOTOR_2_GPIO GPIO_NUM_13
#define MOTOR_1_RMT_CHANNEL RMT_CHANNEL_0
#define MOTOR_2_RMT_CHANNEL RMT_CHANNEL_1
#define DSHOT_CMD_SPIN_DIRECTION_NORMAL 20U
#define DSHOT_CMD_SPIN_DIRECTION_REVERSED 21U
#define DSHOT_THROTTLE_ZERO 48U

#define ARM_DURATION 3000

/* Type Definitions */
enum bldcMotor_E {
    MOTOR_1,
    MOTOR_2,
    ALL
};

struct escDshotConfig_S {
    gpio_num_t gpio_pin;
    bool reversed;
};

/* Function Definitions */
void setupBldcMotor(bldcMotor_E motor);
void armBldcMotor(bldcMotor_E motor);
void setThrottlePercent(bldcMotor_E motor, double throttle_pct);
void setThrottle(bldcMotor_E motor, uint16_t throttle);
void switchDirection(bldcMotor_E motor);
void stopBldcMotor(bldcMotor_E motor);
uint16_t getRpm(bldcMotor_E motor);
void repeatCommand(bldcMotor_E motor, uint16_t command, uint8_t repeat);
void repeatCommandTicks(bldcMotor_E motor, uint16_t command, TickType_t ticks);

#endif
