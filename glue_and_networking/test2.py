from rdt import *
import socket
import sys
import time
import select

mysocket = None
myport = 5050
myhost = str(sys.argv[1])

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysocket.connect((myhost, myport))

poller = select.poll()
poller.register(mysocket, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)

def my_recv_function(size, timeout):
	poll_results = poller.poll(timeout)
	if len(poll_results) != 0:
		return bytearray(mysocket.recv(size))
	else:
		return None

initialize(my_recv_function, mysocket.send, 10000, 10000)

tmp = None

while not done_sending():
	dispatch()

send_data(bytearray("Hello world!", "utf-8"))

#while tmp is None:
#	dispatch()

#	tmp = recv_data()

#print(tmp.decode("utf-8") + "\n")

while True:
	dispatch()
	tmp = recv_data()
	if not (tmp is None):
		print(tmp.decode("utf-8") + "\n")
