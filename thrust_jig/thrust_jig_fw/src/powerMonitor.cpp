#include "powerMonitor.hpp"

static const PowerMonitorAdcConfig_S vbatConfig {
    .adcPin = VBAT_SENSE_PIN,
    .calibratedGain = PDB_VSENSE_GAIN,
    .calibratedOffset = PDB_VSENSE_OFFSET
};

static const PowerMonitorAdcConfig_S ibatConfig {
    .adcPin = IBAT_SENSE_PIN,
    .calibratedGain = PDB_ISENSE_GAIN,
    .calibratedOffset = PDB_ISENSE_OFFSET
};

static const PowerMonitorAdcConfig_S iMotor1Config {
    .adcPin = MOTOR1_ISENSE_PIN,
    .calibratedGain = ACS712_GAIN,
    .calibratedOffset = ACS712_OFFSET
};

static const PowerMonitorAdcConfig_S iMotor2Config {
    .adcPin = MOTOR2_ISENSE_PIN,
    .calibratedGain = ACS712_GAIN,
    .calibratedOffset = ACS712_OFFSET
};

static ESP32AnalogRead vbatAdc;
static ESP32AnalogRead ibatAdc;
static ESP32AnalogRead iMotor1Adc;
static ESP32AnalogRead iMotor2Adc;

void setupPowerMonitor(void) {
    vbatAdc.attach(vbatConfig.adcPin);
    ibatAdc.attach(ibatConfig.adcPin);
    iMotor1Adc.attach(iMotor1Config.adcPin);
    iMotor2Adc.attach(iMotor2Config.adcPin);
}

float getCurrentA(CurrentSensor_E sensor) {
    float currentAmps;
    uint32_t adcVoltageMilliVolts;

    switch (sensor)
    {
        case IBAT:
            adcVoltageMilliVolts = ibatAdc.readMiliVolts();
            break;
        
        default:
            break;
    }
}