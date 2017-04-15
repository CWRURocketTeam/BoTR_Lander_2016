import matplotlib as mpl 
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from PIL import Image, ImageFile
import glob, os
import numpy as np
import time
import random
from multiprocessing import Process, Lock

##import gs_recv as recv


###
### CWRU Case Rocket Team 2017 ground station: data processing
###


#global variables for BOTR scoring
imgnum = 0
packetnum = 0  


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


### continuously plots the result of a given function, once per second
#def plot_cont(func, xmax):
def plot_cont(xmax, ser):

    data = []
    while len(data) < 4:   # fetch packets until we get a telemetry one
        data = handle_telemetry(ser)
 
    latitudes = [data[1]]
    longitudes = [data[2]]
    humidities = [data[3]]
    temperatures = [data[4]]
    altitudes = [data[5]]
    lights = [data[6]]
    voltages = [data[7]]

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

    def update2(i):
        x = range(len(longitudes))
        ax2.clear()
        ax2.plot(x, longitudes, 'b-')

    def update3(i):
        x = range(len(humidities))
        ax3.clear()
        ax3.plot(x, humidities, 'g-')

    def update4(i):
        x = range(len(temperatures))
        ax4.clear()
        ax4.plot(x, temperatures, 'c-')

    def update5(i):
        x = range(len(altitudes))
        ax5.clear()
        ax5.plot(x, altitudes, 'm-')

    def update6(i):
        x = range(len(lights))
        ax6.clear()
        ax6.plot(x, lights, 'y-')

    def update7(i):
        x = range(len(voltages))
        ax7.clear()
        ax7.plot(x, voltages, 'k-')

        #the packet has been plotted -> get new packet 
        data = []
        while len(data) < 4:   # fetch packets until we get another telemetry one
            data = handle_telemetry(ser)
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



def handle_telemetry(ser):
    data = rand_telemetry()  ##testing
##  data = recv.get_data(ser)
    if len(data) > 4:
        print("got a telemetry packet")
        global packetnum
        packetnum += 1
        print (str(packetnum) + " packets have been recieved") 
        return data


def handle_camera(ser):
    global packetnum
    data = [0x00, 0x00, 0x00, bytes([0x01]*32)]  ##testing
##  data = recv.get_data(ser)
    if len(data) < 5 and len(data) > 1:
        print("got a camera packet")
        packetnum += 1
        print (str(packetnum) + " packets have been recieved") 
        ### add to current image
        with open('o.jpg', 'bw') as img:
            img.write(data[3])
            if data[2] != 0: 
                print("made an image")
                return img
 

### takes a list of images and stitches them together sequentially
def panorama_cont(ser):
    out = None
    img = None
    prev = None
    global imgnum

    while imgnum < 4:  #replace 4 with the number of images in a panorama
        while img is None:  #exits once we have a full image
            img = handle_camera(ser)

        if out is None and prev is not None: 
            out = stitch(prev, img)

        elif out is not None:
            out = stitch(out, img)

        if out is not None:
            out.show()
            out.save('pan' + str(i) + '.jpg')  #save panorama to disk

        imgnum += 1 
        print (str(imgnum) + " images have been constructed")
        img.save('img' + str(i) + '.jpg')  #save image to disk 
        prev = img
        img = None

               

if __name__ == '__main__':

    ser = None  ##testing
##  ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.25)
##  initialize(my_recv_function, my_send_function, 250, 250)  #initialize the xbee connection

    try:
        plotpr = Process(target=plot_cont, args=(999, ser))
        imgpr = Process(target=panorama_cont, args=(ser,))
        plotpr.start()
        imgpr.start()
    except KeyboardInterrupt:
        plotpr.terminate()
        imgpr.terminate()




