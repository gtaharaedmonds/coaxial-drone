#ifndef POWERMONITOR_H_
#define POWERMONITOR_H_

/* Includes */
#include "ESP32AnalogRead.h"
#include <stdint.h>

/* Symbolic Constants */
// ESP32 GPIO PINS
#define VBAT_SENSE_PIN 15
#define IBAT_SENSE_PIN 2
#define MOTOR1_ISENSE_PIN 34
#define MOTOR2_ISENSE_PIN 35

// CALIBRATION CONSTANTS (from datasheets for now)
#define PDB_VSENSE_GAIN 21.0/1000.0
#define PDB_VSENSE_OFFSET 0.0
#define PDB_ISENSE_GAIN 0.08
#define PDB_ISENSE_OFFSET 0.0
#define MOTOR1_GAIN -0.01454
#define MOTOR2_GAIN -0.01391
#define MOTOR1_OFFSET 2658
#define MOTOR2_OFFSET 2640

/* Type Definitions */
struct PowerMonitorAdcConfig_S {
    int adcPin;
    double calibratedGain;
    double calibratedOffset;
};

enum CurrentSensor_E {
    IBAT,
    IMOTOR1,
    IMOTOR2
};

enum VoltageSensor_E {
    VBAT
};

/* Function Definitions */
void setupPowerMonitor(void);
float getCurrentA(CurrentSensor_E sensor);
float getVoltageV(VoltageSensor_E sensor);
float getPowerW(CurrentSensor_E sensor);

#endif // POWERMONITOR_H_