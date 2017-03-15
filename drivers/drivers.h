struct gps_coord
{
	double latitude;
	double longitude;
};

void gps_setup (int pin1, int pin2);
struct gps_coord get_gps_coords (void);

void humidity_setup (int pin);
int get_humidity (void);

void altimeter_setup (int pin1, int pin2);
double get_altitude (void);

void light_setup (int pin);
int get_light (void);

void camera_setup (int pin1, int pin2);
void camera_read (void (*callback)(char*, int, char, void*), void* parameter); //Parameters for the callback function: byte buffer, number of bytes in buffer, whether this is the last readout or not, user provided parameter
									       //The camera sends data 32 bytes at a time. Every 32 bytes, the callback function is called. The last read may not be the full 32 bytes, that's what the second parameter is for.
									       //The bool is whether or not this is the last time the callback will be called for this current read loop. Useful for control packet fragmentation, etc.
									       //The last parameter of the callback is the same as the last parameter of the camera_read function. We probably won't be using this for sending camera data over the network, but this is helpful for e.g. saving to an SD card. You can use this parameter to specify the filename

void xbee_setup (int pin1, int pin2);
void xbee_send (char* buf, int len);
void xbee_recv (char* buf, int len, int timeout);
