from rdt import *
import socket
import sys
import time
import select

mysocket = None
myport = 5050
myhost = ''

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysocket.bind((myhost, myport))
mysocket.listen(1)
connection, addr = mysocket.accept()

poller = select.poll()
poller.register(connection, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)

def my_recv_function(size, timeout):
	poll_results = poller.poll(timeout)
	if len(poll_results) != 0:
		return bytearray(connection.recv(size))
	else:
		return None

initialize(my_recv_function, connection.send, 10, 10)

tmp = None

while tmp is None:
	dispatch()

	tmp = recv_data()
	time.sleep(0.25)

print(tmp.decode("utf-8") + "\n")

while not done_sending():
	dispatch()
	time.sleep(0.25)

send_data(bytearray("Goodbye world!", "utf-8"))

while not done_sending():
	dispatch()
	time.sleep(0.25)

connection.close()
