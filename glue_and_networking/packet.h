#include <stdint.h>

#ifndef PACKET_H
#define PACKET_H

#define PACK_ACK    2
#define PACK_DAT    3
#define PACK_UNK    0

#define MAX_PACK_SIZE 128

struct packet_hdr
{
	uint16_t checksum;
	uint16_t len; //Includes header length
	uint8_t type;
	uint8_t seq_num;
};

#endif
