#include "loadCell.hpp"

static const LoadCellAmpConfig_S thrust_config = {
    .data_pin = THRUST_DATA_PIN,
    .clk_pin = THRUST_CLK_PIN,
    .calibration = THRUST_CELL_CALIBRATION,
};

static const LoadCellAmpConfig_S torque_config = {
    .data_pin = TORQUE_DATA_PIN,
    .clk_pin = TORQUE_CLK_PIN,
    .calibration = TORQUE_CELL_CALIBRATION,
};

static HX711 thrust_cell;
static HX711 torque_cell;
static double thrust_value = NAN;
static double torque_value = NAN;

void setupLoadCell(LoadCellType_E loadCellType){
    switch (loadCellType) {
        case THRUST:
            thrust_cell.begin(thrust_config.data_pin, thrust_config.clk_pin);
            thrust_cell.set_scale(thrust_config.calibration);
            break;
        case TORQUE:
            torque_cell.begin(torque_config.data_pin, torque_config.clk_pin);
            torque_cell.set_scale(torque_config.calibration);
            break;
    }

    tareLoadCell(loadCellType);
}

double getLoadCellValue(LoadCellType_E loadCellType){
    switch (loadCellType) {
        case THRUST:
            if (thrust_cell.is_ready()) {
                thrust_value = thrust_cell.get_units();
            }
            return thrust_value;
            break;
        case TORQUE:
            if (torque_cell.is_ready()) {
                torque_value = torque_cell.get_units();
            }
            return torque_value;
            break;
        default:
            return 0;
            break;
    }
}

void tareLoadCell(LoadCellType_E loadCellType){
    switch (loadCellType) {
    case (THRUST):
        thrust_cell.tare();
        break;
    case (TORQUE):
        torque_cell.tare();
        break;
    }
}