#ifndef SERIALPROTOCOL_H_
#define SERIALPROTOCOL_H_

/* Includes */
#include <deque>
#include <HardwareSerial.h>

/* Symbolic constants */
#define NUM_COMMAND_SET_VALUES 5

/* Type definitions */
struct CommandSet_S
{
    unsigned long time_ms;
    double top_percent;
    double bot_percent;
    int pitch_us;
    int roll_us;
};

/* Global variables */
extern std::deque<CommandSet_S> test_spec;

/* Function definitions */
void receiveTestSpec(void);

#endif