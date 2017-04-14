#include <drivers.h>
#include <lander_protocol.h>
#include <rdt.h>
#include <Servo.h>

//Remember: always leave RESET unplugged unless you have the programmer powered lest you try to debug an error you don't understand.
//Also, UART is high by default and the TX pin happens to be the same as the first continuity check pin. So if you have the programmer in it will register continuity

int i = 0;

Servo camera_servo;
Servo latch_servo;

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
  xbee_setup(13, 12, 57600);
  initialize(xbee_recv, xbee_send, 500, 500);
  setup_continuity(1);
  setup_pyrochannel(1);
  //Serial.begin(9600);
}

void loop() {
  double base_altitude = get_altitude();
  struct cont_packet continuity_signal;
  char continuity = check_pyro_continuity(1);

  continuity_signal.magic = CONT_MAGIC;
  continuity_signal.cont_status = continuity;
  send_data((char*)&continuity_signal, sizeof(struct cont_packet));

  if (continuity)
  {
    while (get_altitude() - base_altitude < 250)
    {
      dispatch();
    }

    while (get_altitude() - base_altitude > 215) 
    {}

    fire_pyrochannel(1);
  }

  delay(5000);
  latch_servo.attach(8);
  latch_servo.write(100);
  latch_servo.detach();

  while (1)
  {
    delay(1000);
    camera_read(camera_callback, NULL);
    camera_servo.attach(9); //Need to attach and detach when using this servo because camera interferes
    camera_servo.write(90);
    delay(2950);
    camera_servo.write(89);
    camera_servo.detach();
    camera_read(camera_callback, NULL);
    camera_servo.attach(9);
    camera_servo.write(90);
    delay(2950);
    camera_servo.write(89);
    camera_servo.detach();
    camera_read(camera_callback, NULL);
    camera_servo.attach(9);
    camera_servo.write(90);
    delay(2950);
    camera_servo.write(89);
    camera_servo.detach();
    camera_read(camera_callback, NULL);
    camera_servo.attach(9);
    camera_servo.write(88);
    delay(5400);
    camera_servo.write(89);
    camera_servo.detach();
  }
}
