#ifndef LOADCELL_H_
#define LOADCELL_H_

/* Includes */
#include "HX711.h"
#include <stdint.h>

/* Symbolic Constants */
#define THRUST_DATA_PIN 18
#define TORQUE_DATA_PIN 32
#define THRUST_CLK_PIN 19
#define TORQUE_CLK_PIN 33

#define LOAD_CELL_CALIBRATION 5000

/* Type Definitions */
enum LoadCellType_E {
    THRUST,
    TORQUE
};

struct LoadCellAmpConfig_S {
    uint8_t data_pin;
    uint8_t clk_pin;
    int calibration;
};

/* Function Definitions */
void setupLoadCell(LoadCellType_E loadCellType);
double getLoadCellValue(LoadCellType_E loadCellType);
void tareLoadCell(LoadCellType_E loadCellType);

#endif