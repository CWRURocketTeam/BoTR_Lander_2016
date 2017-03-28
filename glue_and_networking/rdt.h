#ifndef RDT_H
#define RDT_H

extern char can_send;
extern int recv_timeout;
extern int send_timeout;
extern int (*recv_function)(char*, int, int);
extern void (*send_function)(char*, int);

void dispatch (void);
void initialize (int (*__recv_function)(char*, int, int), void (*__send_function)(char*, int), int __recv_timeout, int __send_timeout);
char* recv_data (void);
void send_data (char* data, int len);

#endif
