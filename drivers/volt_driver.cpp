#include "drivers.h"

double get_voltage (void)
{
	return analogRead(3)/1024.0*55.0;
}
