#include <stdint.h>

#include "HX711.h"

typedef struct
{
    uint8_t data_pin;
    uint8_t clk_pin;
    int calibration;
} LoadCellAmpConfig;

static const LoadCellAmpConfig thrust_config = {
    .data_pin = 18,
    .clk_pin = 19,
    .calibration = 5000,
};

static const LoadCellAmpConfig torque_config = {
    .data_pin = 32,
    .clk_pin = 33,
    .calibration = 5000,
};

static HX711 thrust_cell;
static HX711 torque_cell;

void setup()
{
    Serial.begin(9600);
    Serial.println("Thrust Jig Firmware Program");

    thrust_cell.begin(thrust_config.data_pin, thrust_config.clk_pin);
    torque_cell.begin(torque_config.data_pin, torque_config.clk_pin);

    thrust_cell.set_scale(thrust_config.calibration);
    torque_cell.set_scale(torque_config.calibration);

    // Zero the
    thrust_cell.tare();
    torque_cell.tare();
}

void loop()
{
    // Print unscaled thrust value, then unscaled torque value
    // To be interpreted in Python program

    Serial.print(thrust_cell.get_value(), 1);
    Serial.print(" ");
    Serial.print(torque_cell.get_value(), 1);
    Serial.println();

    delay(100);
}