from rdt import *
import serial
import struct

ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.25)

def my_recv_function(size, timeout):
	return bytearray(ser.read(size))

def my_send_function(to_send):
	ser.write(to_send)

initialize(my_recv_function, my_send_function, 250, 250)

outfile = open('outfile.jpg', 'bw')

tmp = None
parsed_tmp = None

while True:
	dispatch()

	tmp = recv_data()
	if not (tmp is None):
		if tmp[0] == 0x55 and tmp[1] == 0x55: #Check continuity
			print("Continuity: " + str(tmp[2]))
		if tmp[0] == 0x41 and tmp[1] == 0x43: #Arduino is little endian, so the numbers are the reverse of what you'd expect
			parsed_tmp = struct.unpack("<HHB32s", tmp)
			outfile.write(parsed_tmp[3])
			if parsed_tmp[2] != 0:
				break
		if tmp[0] == 0x45 and tmp[1] == 0x54:
			parsed_tmp = struct.unpack("<HffHffHf", tmp)
			print("Latitude: " + str(parsed_tmp[1])) #The first index of this tuple is the magic, ignore it
			print("Longitude: " + str(parsed_tmp[2]))
			print("Humidity: " + str(parsed_tmp[3]) + "%")
			print("Temperature: " + str(parsed_tmp[4]) + "F")
			print("Altitude: " + str(parsed_tmp[5]) + "M")
			print("Light: " + str(parsed_tmp[6]))
			print("Voltage: " + str(parsed_tmp[7]) + "V")

outfile.close()
print("done!")
