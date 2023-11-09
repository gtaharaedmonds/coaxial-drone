#include "serialProtocol.hpp"

std::deque<CommandSet_S> test_spec;

void receiveTestSpec(void) {
    String input;
    int num_values;
    Serial.println("Ready to load test spec");
    while (true) {
        input = Serial.readStringUntil('\n');
        if (input == "Begin new test spec") {
            break;
        } else if (input != "") {
            Serial.println("Invalid command");
        }
    }
    while (true) {
        test_spec.clear();
        // Ignore CSV header line
        do {
            input = Serial.readStringUntil('\n');
        } while (input == "");
        while (true) {
            do {
                input = Serial.readStringUntil('\n');
            } while (input == "");
            if (input == "Begin new test spec") {
                break;
            } else if (input == "Run test") {
                if (test_spec.size() == 0) {
                    Serial.println("Invalid state");
                    continue;
                } else {
                    return;
                }
            } else {
                CommandSet_S command_set;
                num_values = sscanf(
                    input.c_str(),
                    "%lu,%lf,%lf,%d,%d",
                    &command_set.time_ms,
                    &command_set.top_percent,
                    &command_set.bot_percent,
                    &command_set.pitch_us,
                    &command_set.roll_us
                );
                if (num_values == NUM_COMMAND_SET_VALUES) {
                    test_spec.push_back(command_set);
                } else {
                    Serial.println("Invalid command");
                }
            }
        }
    }
}
