#ifndef SERVOMOTOR_H_
#define SERVOMOTOR_H_

/* Includes */
#include <ESP32Servo.h>

/* Symbolic constants */
#define PITCH_VANE_GPIO GPIO_NUM_26
#define ROLL_VANE_GPIO GPIO_NUM_27
#define PITCH_VANE_MIN_US 1280
#define PITCH_VANE_MAX_US 1725
#define PITCH_VANE_TRIM_US 1495
#define ROLL_VANE_MIN_US 1280
#define ROLL_VANE_MAX_US 1790
#define ROLL_VANE_TRIM_US 1525
#define PITCH_VANE_REVERSED false
#define ROLL_VANE_REVERSED true

/* Type definitions */
enum ServoMotor_E {
    PITCH_VANE,
    ROLL_VANE
};

struct ServoConfig_S {
    gpio_num_t gpio_pin;
    int min_pwm_us;
    int max_pwm_us;
    int trim_pwm_us;
    bool reversed;
};

/* Function definitions */
void setupServo(ServoMotor_E servo);
void setServoPwm(ServoMotor_E servo, int pwm_us);

#endif