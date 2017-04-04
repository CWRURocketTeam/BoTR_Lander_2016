#include <Arduino.h>
#include <SoftwareSerial.h>
#include "drivers.h"

SoftwareSerial* xbee_serial;

void xbee_setup (int pin1, int pin2, unsigned int __baudrate)
{
	xbee_serial = new SoftwareSerial(pin1, pin2);
	xbee_serial->begin(__baudrate);
}

void xbee_send (char* buf, int len)
{
	xbee_serial->write(buf, len);
}

int xbee_recv (char* buf, int len, int timeout)
{
	xbee_serial->setTimeout(timeout);
	xbee_serial->listen();
	return xbee_serial->readBytes(buf, len);
}
