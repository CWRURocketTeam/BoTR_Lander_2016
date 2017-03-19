#include "drivers.h"

void light_setup (void)
{
  pinMode(A3, INPUT);
}

int get_light (void)
{
  float val = (float) analogRead(A3);
  float percent = (val/1024)*100;
  return percent;
}
