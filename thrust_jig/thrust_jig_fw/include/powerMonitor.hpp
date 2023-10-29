#ifndef POWERMONITOR_H_
#define POWERMONITOR_H_

/* Includes */
#include "ESP32AnalogRead.h"
#include <stdint.h>

/* Symbolic Constants */
// ESP32 GPIO PINS
#define VBAT_SENSE_PIN 36
#define IBAT_SENSE_PIN 39
#define MOTOR1_ISENSE_PIN 34
#define MOTOR2_ISENSE_PIN 35

// CALIBRATION CONSTANTS (reporting raw ADC voltage for now)
#define PDB_VSENSE_GAIN 1.0
#define PDB_VSENSE_OFFSET 0.0
#define PDB_ISENSE_GAIN 1.0 
#define PDB_ISENSE_OFFSET 0.0
#define ACS712_GAIN 1.0
#define ACS712_OFFSET 0.0

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