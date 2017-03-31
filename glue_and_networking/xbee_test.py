from rdt import *
import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.25);

def my_recv_function(size, timeout):
	return bytearray(ser.read(size))

def my_send_function(to_send):
	ser.write(to_send)

initialize(my_recv_function, my_send_function, 250, 250)

tmp = None

while True:
	dispatch()

	tmp = recv_data()
	if not (tmp is None):
	#	print(tmp.decode("utf-8") + "\n")
		print(str(tmp))
