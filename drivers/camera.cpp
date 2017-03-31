#include <Adafruit_VC0706.h>
#include <Arduino.h>
#include "drivers.h"

Adafruit_VC0706* cam;

void camera_setup(int pin1, int pin2)
{
	cam = new Adafruit_VC0706(new SoftwareSerial(pin1, pin2));
	cam->setImageSize(VC0706_640x480);
}

void camera_read(void (*callback)(char*, int, char, void*), void* parameter)
{
	uint16_t len;
	uint8_t* buf;

	if (!cam->takePicture())
		return;

	len = cam->frameLength();
	while (len > 32)
	{
		buf = cam->readPicture(32);
		callback(buf, 32, 0, parameter);
		len -= 32;
	}
	buf = cam->readPicture(len);
	callback(buf, len, 1, parameter);
}
