#include <Adafruit_GPS.h>
#include <Drivers.h>
#include <SoftwareSerial.h>

SoftwareSerial* mySerial;
Adafruit_GPS* GPS;

void gps_setup (int pin1, int pin2)
{

  mySerial = new SoftwareSerial(pin1, pin2);
  GPS = new Adafruit_GPS(mySerial);

  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS->begin(9600);
  

  // uncomment this line to turn on only the "minimum recommended" data
  GPS->sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
 
  // Set the update rate
  GPS->sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  // For the parsing code to work nicely and have time to sort thru the data, and
  // print it out we don't suggest using anything higher than 1 Hz

  GPS->sendCommand(PGCMD_ANTENNA);

  TIMSK0 &= ~_BV(OCIE0A);

  mySerial->println(PMTK_Q_RELEASE);
}


struct gps_coord get_gps_coords (void)
{
  struct gps_coord my_coord;
  int i;

  // if a sentence is received, we can check the checksum, parse it...
  for (i; i < 100; i++)
  {
        GPS->read();
	if (GPS->newNMEAreceived())
		break;
	delay(20);
  }

  if (i = 100)
  {
     my_coord.latitude = 0;
     my_coord.longitude = 0;
     return my_coord;
  }
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences! 
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
  
  GPS->parse(GPS->lastNMEA());   // this also sets the newNMEAreceived() flag to false

  my_coord.latitude = GPS->latitude;
  my_coord.longitude = GPS->longitude; 
  return my_coord;
}
