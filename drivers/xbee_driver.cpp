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
	int i;

	xbee_serial->listen();

	for (i = 0; i < timeout; i+=10)
	{
		if (xbee_serial->available())
			break;

		delay(9);
	}
	if (i >= timeout)
		return 0;

	i = 0;
	while (i < len && xbee_serial->available())
	{
		buf[0] = xbee_serial->read();
		buf++;
		i++;
		delay(1);
	}
}
