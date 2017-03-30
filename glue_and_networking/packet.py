from struct import *
from checksum import *

PACK_ACK = 2
PACK_DAT = 3
PACK_UNK = 0

MAX_PACK_SIZE = 128

header_format = '<HHBB'
header_size = 6

def packet_length(to_measure):
	length = to_measure[2]
	length |= to_measure[3] << 8
	return length

def create_packet(to_packetize, packet_type, seq_num):
	global header_format
	global header_size

	tmp = bytearray(pack(header_format + str(len(to_packetize)) + 's', 0, len(to_packetize) + header_size, packet_type, seq_num, bytearray(to_packetize)))
	new_checksum = ones_checksum(tmp)
	return bytearray(pack(header_format + str(len(to_packetize)) + 's', new_checksum, len(to_packetize) + header_size, packet_type, seq_num, bytearray(to_packetize)))

def unpack_packet(to_unpack):
	global header_format
	global header_size

	length = packet_length(to_unpack)

	if (length - header_size) > 0:
		return unpack(header_format + str(length - header_size) + 's', to_unpack)
	else:
		return unpack(header_format, to_unpack)
