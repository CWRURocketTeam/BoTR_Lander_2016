#include <Arduino.h>
#include "drivers.h"

bool valid_pyrochannel(int chan)
{
	if(chan > 0 && chan < 4){
		return true;
	}
	return false;
}

void setup_pyrochannel (int channel_number)
{
	if(valid_pyrochannel(channel_number))
	{
		pinMode(channel_number+3, OUTPUT);
	}
}

void setup_continuity (int channel_number)
{
  pinMode(channel_number,INPUT);
}

void fire_pyrochannel (int channel_number)
{
	if(valid_pyrochannel(channel_number))
	{
		digitalWrite(channel_number+3, HIGH);
	}
}

char check_pyro_continuity (int channel_number)
{
  return digitalRead(channel_number);
}
