#include <Arduino.h>
#include "drivers.h"

double get_voltage (void)
{
	return analogRead(A3)/1024.0*55.0;
}
