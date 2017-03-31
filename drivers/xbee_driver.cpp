#include <Arduino.h>
#include <SoftwareSerial.h>
#include "drivers.h"

SoftwareSerial* xbee_serial;

void xbee_setup (int pin1, int pin2, unsigned int baudrate)
{
	xbee_serial = new SoftwareSerial(pin1, pin2);
	xbee_serial->begin(baudrate);
}

void xbee_send (char* buf, int len)
{
	xbee_serial->write(buf, len);
}

int xbee_recv (char* buf, int len, int timeout)
{
	xbee_serial->setTimeout(timeout);
	return xbee_serial->readBytes(buf, len);
}
