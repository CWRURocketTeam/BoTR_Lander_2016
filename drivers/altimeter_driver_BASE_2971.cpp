#include "drivers.h"
#include "Wire.h"
#include "Adafruit_BMP085.h"
/*^download above libraries from adafruit github, also BMP085 works for BMP180*/

/*BMP180 Barometric Pressure/Temperature/Altitude Sensor*/

float initial_pressure;

/*need to input current air pressure @ sea level for accurate reading*/
void altimeter_setup (int pin1, int pin2)
{
  Serial.begin(9600);
  bmp.begin();
}

float get_altitude (void)
{
  return bmp.pressureToAltitude(SENSORS_PRESSURE_SEALEVELHPA,event.pressure);
}
