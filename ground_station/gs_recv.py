from rdt import *
import select
import struct


def my_recv_function(size, timeout):
    return bytearray(ser.read(size))

def my_send_function(to_send):
    ser.write(to_send)


### returns an unpacked struct with a packet of xbee data ( either camera or telemetry )
def get_data(ser):

    tmp = None
    parsed_tmp = None

    dispatch()
    tmp = recv_data()

    if not (tmp is None):

        #Arduino is little endian, so the numbers are the reverse of what you'd expect
        #camera packet
        if tmp[0] == 0x41 and tmp[1] == 0x43:
            parsed_tmp = struct.unpack("<HHB32s", tmp)

        #telemetry packet
        if tmp[0] == 0x45 and tmp[1] == 0x54:
            parsed_tmp = struct.unpack("<HffHffHf", tmp)
            #The first index of this tuple is the magic, ignore it
#	        print("Latitude: " + str(parsed_tmp[1])) 
#	        print("Longitude: " + str(parsed_tmp[2]))
#	        print("Humidity: " + str(parsed_tmp[3]) + "%")
#	        print("Temperature: " + str(parsed_tmp[4]) + "F")
#	        print("Altitude: " + str(parsed_tmp[5]) + "M")
#	        print("Light: " + str(parsed_tmp[6]))
#	        print("Voltage: " + str(parsed_tmp[7]) + "V")

    return parsed_tmp
