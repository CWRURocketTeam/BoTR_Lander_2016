import matplotlib as mpl 
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from PIL import Image, ImageFile
import glob, os
import numpy as np
import time
import random
from multiprocessing import Process, Lock

import serial
from rdt import * 
import select
import struct


###
### CWRU Case Rocket Team 2017 ground station: data processing
### @TODO look into pipes/queues to prevent race conditions
###

 
### global variables
imgnum = 0
packetnum = 0 
##ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.25)
ser = None ##testing
image = None
telemetry_data = []
camera_data = []
oldtel = True  #true if the telemetry packet has already been plotted
oldcam = False  #true if the camera packet has already been processed


### handles the array of command line arguments
### @TODO add/configure switches, display how they work in helpmsg
def handle_args():
    helpmsg = "[ help message goes here ]"
    for arg in sys.argv:
#       print(arg)
        if arg == "-h" or arg == "-help" or arg == "--help" or arg == "--h":
            print(helpmsg)
            break


### displays an image from the local directory and prints out its properties
def showimage(filename):
    im = Image.open(filename)
    print(im.format, im.size, im.mode)
    im.show()


### takes two images and returns a new image with the 1st stitched to the right of the 2nd
def stitch(im1, im2):
    if ((im1.format, im1.mode) != (im2.format, im2.mode)): 
        print("images not optimal for stitching, try making them the same format and mode to increase speeds")
    out = Image.new(im1.mode, (im1.size[0] + im2.size[0], max(im1.size[1], im2.size[1])))
    out.paste(im1, (0, 0, im1.size[0], im1.size[1]))
    out.paste(im2, (im1.size[0], 0, im2.size[0] + im1.size[0], im2.size[1]))
    return out


### generates a new random number for each call
def rand():
    return random.random() 


### generates a fake telemetry array, for testing
def rand_telemetry():
    arr = [None]*8
    for i in range (0,8):
        arr[i] = rand()
    return arr 


### continuously plots telemetry info 
def plot_cont(lock, xmax):
    lock.acquire()
    global oldtel
    global telemetry_data

    i = 0 #dummy var to stall this thread until we have a packet to graph
    while oldtel or telemetry_data == []:
        print("plot: waiting")
        i += 2

    latitudes = [data[1]]
    longitudes = [data[2]]
    humidities = [data[3]]
    temperatures = [data[4]]
    altitudes = [data[5]]
    lights = [data[6]]
    voltages = [data[7]]

    oldtel = True

    fig = plt.figure()

    ax1 = fig.add_subplot(241) #latitude
    ax2 = fig.add_subplot(242) #longitude
    ax3 = fig.add_subplot(243) #humidity
    ax4 = fig.add_subplot(244) #temperature
    ax5 = fig.add_subplot(245) #altitude
    ax6 = fig.add_subplot(246) #light
    ax7 = fig.add_subplot(247) #voltage

    ### update functions can't take extra parameters... there's probably a much less boilerplate-ish way around this, but this works (using a wrapper function didn't)
    def update1(i):
        x = range(len(latitudes))
        ax1.clear()
        ax1.plot(x, latitudes, 'r-')
        ax1.set_ylabel('latitude ')

    def update2(i):
        x = range(len(longitudes))
        ax2.clear()
        ax2.plot(x, longitudes, 'b-')
        ax2.set_ylabel('longitude ')

    def update3(i):
        x = range(len(humidities))
        ax3.clear()
        ax3.plot(x, humidities, 'g-')
        ax3.set_ylabel('humidity (%) ')

    def update4(i):
        x = range(len(temperatures))
        ax4.clear()
        ax4.plot(x, temperatures, 'c-')
        ax4.set_ylabel('temp (degrees fahrenheit) ')

    def update5(i):
        x = range(len(altitudes))
        ax5.clear()
        ax5.plot(x, altitudes, 'm-')
        ax5.set_ylabel('altitude (meters) ')

    def update6(i):
        x = range(len(lights))
        ax6.clear()
        ax6.plot(x, lights, 'y-')
        ax6.set_ylabel('light (%) ')

    def update7(i):
        x = range(len(voltages))
        ax7.clear()
        ax7.plot(x, voltages, 'k-')
        ax7.set_ylabel('voltage (volts) ')

        i = 0 #dummy var to stall this thread until we have a new packet to graph
        while oldtel or telemetry_data == []:
            i += 2

        latitudes.append(data[1])
        longitudes.append(data[2])
        humidities.append(data[3])
        temperatures.append(data[4])
        altitudes.append(data[5])
        lights.append(data[6])
        voltages.append(data[7])

    a1 = anim.FuncAnimation(fig, update1, frames=xmax, repeat=False)
    a2 = anim.FuncAnimation(fig, update2, frames=xmax, repeat=False)
    a3 = anim.FuncAnimation(fig, update3, frames=xmax, repeat=False)
    a4 = anim.FuncAnimation(fig, update4, frames=xmax, repeat=False)
    a5 = anim.FuncAnimation(fig, update5, frames=xmax, repeat=False)
    a6 = anim.FuncAnimation(fig, update6, frames=xmax, repeat=False)
    a7 = anim.FuncAnimation(fig, update7, frames=xmax, repeat=False)

    plt.show()
    lock.release()


def create_image():
    global image
    global packetnum
    global oldcam

    if not oldcam and camera_data != []:
        image.write(camera_data[3])  #add to current image
        oldcam = True
        if data[2] != 0:  #signals end of image
            print("completed an image!")
            return True
    return False
 

### generates a 360 degree panorama from camera packets
def panorama_cont(lock):
    lock.acquire()
    global image 
    global imgnum
    firstimg = None
    out = None   #stores current panoramic image

    while imgnum < 4:  #assumes there are 4 images in a panorama
        image = open('out.jpg', 'bw')  #start new image
        done = False
        while not done:  #exits once we have a full image
            done = create_image()

        if firstimg is None:
            firstimg = image
        else:
            if out is None:
                out = stitch(firstimg, image)
            else:
                out = stitch(out, image)
                out.show()
                out.save('pan' + str(imgnum) + '.jpg')  #save iteration of panorama to disk

        imgnum += 1 
        print (str(imgnum) + " images have been constructed")
        image.save('img' + str(imgnum) + '.jpg')  #save image to disk 
        image = None

    out.save('completed_pan' + str((int)(imgnum/4)) + '.jpg')  #save final panorama to disk
    lock.release()


def my_recv_function(size, timeout):
    global ser
    return bytearray(ser.read(size))

def my_send_function(to_send):
    global ser
    ser.write(to_send)


### gets and unpacks structs of xbee data ( either camera or telemetry )
def get_data(lock):
    lock.acquire()
    global oldcam
    global oldtel
    global camera_data
    global telemetry_data
    tmp = None
    parsed_tmp = None

    while True:
        if oldcam or oldtel:

#            camera_data = [0x00, 0x00, 0x00, bytes([0x04]*32)] ##testing
            telemetry_data = rand_telemetry() ##testing
#            oldcam = False
            oldtel = False

##          dispatch()
##          tmp = recv_data()

            if not (tmp is None):
                #Arduino is little endian, so the numbers are the reverse of what you'd expect
                #camera packet
                if tmp[0] == 0x41 and tmp[1] == 0x43:
                    parsed_tmp = struct.unpack("<HHB32s", tmp)
                    camera_data = parsed_tmp
                    oldcam = False
                    print("got a camera packet")
                    packetnum += 1
                    #print (str(packetnum) + " packets have been recieved") 

                #telemetry packet
                if tmp[0] == 0x45 and tmp[1] == 0x54:
                    parsed_tmp = struct.unpack("<HffHffHf", tmp)
                    telemetry_data = parsed_tmp
                    oldtel = False
    lock.release()



if __name__ == '__main__':
    
    lock = Lock()
    initialize(my_recv_function, my_send_function, 250, 250)  #initialize the xbee connection

    try:
        getdatapr = Process(target=get_data, args=(lock,))
        plotpr = Process(target=plot_cont, args=(lock,99999))
        imgpr = Process(target=panorama_cont, args=(lock,))
        getdatapr.start()
        plotpr.start()
        imgpr.start()
    except KeyboardInterrupt:
        getdatapr.terminate()
        plotpr.terminate()
        imgpr.terminate()




