#include <Arduino.h>
#include "drivers.h"

int get_light (void)
{
  float val = (float) analogRead(A2);
  float percent = (val/1024)*100;
  return percent;
}
