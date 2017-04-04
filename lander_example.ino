#include <drivers.h>
#include <lander_protocol.h>
#include <rdt.h>

int i = 0;

void camera_callback (char* buf, int len, char is_last, void* arg)
{
  struct camera_packet pack;

  if (!(i % 32))
    send_telemetry();
  i++;
  
  pack.magic = CAMERA_MAGIC;
  pack.len = len;
  pack.last_packet_flag = is_last;
  memcpy((char*)&(pack.data), buf, len);

  while (!can_send)
    dispatch();

  send_data((char*)&pack, sizeof(struct camera_packet));
}

void send_telemetry (void)
{
  struct telemetry_packet pack;
  struct gps_coord coord;

  coord = get_gps_coords();
  
  pack.magic = TELEMETRY_MAGIC;
  pack.latitude = coord.latitude;
  pack.longitude = coord.longitude;
  pack.humidity = get_humidity();
  pack.temperature = get_temperature(true);
  pack.altitude = get_altitude();
  pack.light = get_light();
  pack.voltage = get_voltage();

  while(!can_send)
    dispatch();

  send_data((char*)&pack, sizeof(struct telemetry_packet));
}

void setup() {
  altimeter_setup();
  humidity_setup();
  gps_setup(11, 10);
  camera_setup(2, 3);
  xbee_setup(13, 12, 9600);
  initialize(xbee_recv, xbee_send, 250, 250);
  setup_continuity(1);
  Serial.begin(9600);
}

void loop() {
  camera_read(camera_callback, NULL);

  Serial.println("done!");

  while(1)
  {
    dispatch();
    delay(500);
  }
}
