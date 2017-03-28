#include "drivers.h"
//#include "Wire.h"
#include "Adafruit_BMP085.h"
/*^download above libraries from adafruit github, also BMP085 works for BMP180*/

/*BMP180 Barometric Pressure/Temperature/Altitude Sensor*/

Adafruit_BMP085 bmp = Adafruit_BMP085();

/*need to input current air pressure @ sea level for accurate reading*/
void altimeter_setup (int pin1, int pin2)
{
  bmp.begin();
}

double get_altitude (void) // in meters
{
  return bmp.readAltitude();
}
