import matplotlib as mpl 
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from PIL import Image, ImageFile
import numpy as np
import multiprocessing as mp
from rdt import * 
import serial
import select
import struct

##for testing:
import random
import time

ImageFile.LOAD_TRUNCATED_IMAGES = True #lol not my fault, blame PIL


###
### CWRU Case Rocket Team 2017 ground station: data processing
###

 
### global variables
teldata = mp.Array('f', 8)
oldtel = mp.Value('i', 1)  #fake boolean: 1 if teldata has been plotted, 0 otherwise
ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.25)
##ser = None ##testing


### handles the array of command line arguments
### @TODO add/configure switches, display how they work in helpmsg
def handle_args():
    helpmsg = "[ help message goes here ]"
    for arg in sys.argv:
#       print(arg)
        if arg == "-h" or arg == "-help" or arg == "--help" or arg == "--h":
            print(helpmsg)
            break


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
def plot_cont(xmax):
    i = 0 #dummy var to stall this thread until we have a packet to graph
    while (oldtel.value == 1) or (teldata == []):
#        print ("waiting for first telemetry packet...")
        i += 2
    latitudes = [100 * teldata[1]]
    longitudes = [100 * teldata[2]]
    humidities = [teldata[3]]
    temperatures = [teldata[4]]
    altitudes = [teldata[5]]
    lights = [teldata[6]]
    voltages = [teldata[7]]
    oldtel.value = 1
    print("lander has uprighted")

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
        ax1.set_ylabel('latitude (degrees)')

    def update2(i):
        x = range(len(longitudes))
        ax2.clear()
        ax2.plot(x, longitudes, 'b-')
        ax2.set_ylabel('longitude (degrees)')

    def update3(i):
        x = range(len(humidities))
        ax3.clear()
        ax3.plot(x, humidities, 'g-')
        ax3.set_ylabel('humidity (%)')

    def update4(i):
        x = range(len(temperatures))
        ax4.clear()
        ax4.plot(x, temperatures, 'c-')
        ax4.set_ylabel('temp (degrees fahrenheit)')

    def update5(i):
        x = range(len(altitudes))
        ax5.clear()
        ax5.plot(x, altitudes, 'm-')
        ax5.set_ylabel('altitude (meters)')

    def update6(i):
        x = range(len(lights))
        ax6.clear()
        ax6.plot(x, lights, 'y-')
        ax6.set_ylabel('light (%)')

    def update7(i):
        x = range(len(voltages))
        ax7.clear()
        ax7.plot(x, voltages, 'k-')
        ax7.set_ylabel('voltage (volts)')
        i = 0 #dummy var to stall this thread until we have a new packet to graph
        while (oldtel.value == 1) or (teldata == []):
            i += 2
        latitudes.append(100 * teldata[1])
        longitudes.append(100 * teldata[2])
        humidities.append(teldata[3])
        temperatures.append(teldata[4])
        altitudes.append(teldata[5])
        lights.append(teldata[6])
        voltages.append(teldata[7])
        oldtel.value = 1  #we can get a new packet now


    #these functions run continuously as the graphs update
    a1 = anim.FuncAnimation(fig, update1, frames=xmax, repeat=False)
    a2 = anim.FuncAnimation(fig, update2, frames=xmax, repeat=False)
    a3 = anim.FuncAnimation(fig, update3, frames=xmax, repeat=False)
    a4 = anim.FuncAnimation(fig, update4, frames=xmax, repeat=False)
    a5 = anim.FuncAnimation(fig, update5, frames=xmax, repeat=False)
    a6 = anim.FuncAnimation(fig, update6, frames=xmax, repeat=False)
    a7 = anim.FuncAnimation(fig, update7, frames=xmax, repeat=False)

    plt.show()



### displays an image from the local directory and prints out its properties
def showimage(filename):
    im = Image.open(filename)
    print(im.format, im.size, im.mode)
    im.show()


### takes two images and returns a new image with the 1st stitched to the right of the 2nd
### assumes 640x480 jpg images
def stitch(title1, title2, imgnum):
    width = 640
    height = 480
    im1_width = ((imgnum % 4) - 1) * width

    im1 = Image.open(title1).convert('RGB')#.save(title1)
    im2 = Image.open(title2).convert('RGB')#.save(title2)
    out = Image.new('RGB', (im1.size[0] + im2.size[0], max(im1.size[1], im2.size[1])))
    out.paste(im1, (0, 0, im1.size[0], im1.size[1]))
    out.paste(im2, (im1.size[0], 0, im2.size[0] + im1.size[0], im2.size[1]))
#    out = Image.new('RGB', (im1_width + width, height))
#    out.paste(im1, (0, 0, im1_width, height))
#    out.paste(im1, (0, 0, 640, 480); )
#    out.paste(im2, (im1_width, 0, im1_width + width, height))
    im2.show()
    out.show()
    out.save('pan' + str(imgnum-1) + '.jpg')
    return out


### xbee functions:
def my_recv_function(size, timeout):
    global ser
    return bytearray(ser.read(size))

def my_send_function(to_send):
    global ser
    ser.write(to_send)


### gets and unpacks structs of xbee data ( either camera or telemetry )
def get_data():
    imgnum = 0
    packetnum = 0
    tel_packetnum = 0
    firstpacket = False  #to see if a packet is the first in a new image (not the first image)
    tmp = None
    parsed_tmp = None
    firstimg = None #temp var for first panorama iteration
    out = None   #stores current panoramic image

    image = open('out1.jpg', 'bw')  

    while True:
#       if oldtel.value == 1: #don't get a new packet unless the last one has been plotted

            #for i in range (1,8):
            #    teldata[i] = rand() ##testing
            #seed = rand() ##testing

            print("getting data...")
            dispatch()
            tmp = recv_data()

            #if True:  ##testing
            if tmp is not None:

                #telemetry packet
                #if seed < 0.1:  ##testing
                if tmp[0] == 0x45 and tmp[1] == 0x54:
                    packetnum += 1
                    tel_packetnum += 1
                    print("got a telemetry packet: " + str(packetnum) + " recieved so far" )
                    #print (str(packetnum) + " packets have been recieved") 
                    parsed_tmp = struct.unpack("<HffHffHf", tmp)
                    for i in range (1, 8): # the only way to update a global array
                        teldata[i] = parsed_tmp[i]
                        #teldata[i] = rand() ##testing
                    oldtel.value = 0  #this is a new packet, so allow it to be plotted

                #camera packet
                #if seed >= 0.1: ##testing
                if tmp[0] == 0x41 and tmp[1] == 0x43: 
                    packetnum += 1
                    print("got a camera packet")
                    print (str(packetnum) + " packets have been recieved") 
                    parsed_tmp = struct.unpack("<HHB32s", tmp)
                    #parsed_tmp = [0x00, 0x00, 0x00, bytes([0x02]*32)]
                    camera_data = parsed_tmp[3]

#                   if imgnum < 4:  #assumes there are 4 images in a panorama
                    if firstpacket: #starts a new image 
                        image = open('out' + str(imgnum+1) + '.jpg', 'bw')  
                        firstpacket = False
                    image.write(parsed_tmp[3])  #add to current image

                    if parsed_tmp[2] != 0:  #last packet in the image
                        imgnum += 1 
                        firstpacket = True #next packet is the first in a new image
                        print (str(imgnum) + " images have been constructed")
                        if firstimg is None and imgnum < 4: 
                            firstimg = image
                            #firstimg.show()
                        elif imgnum < 4:
                            if out is None:
                                out = stitch('out1.jpg', 'out2.jpg', imgnum)
                            else:
                                out = stitch('pan' + str(imgnum-2) + '.jpg', 'out' + str(imgnum) + '.jpg', imgnum)
                                ##out.show()
                                #out.PIL.save('pan' + str(imgnum) + '.jpg')  #save iteration of panorama to disk

###                        else: #panorama is done and we just want to save more images
###                            tempimg = Image.open('out'+str(imgnum)+'.jpg').convert('RGB')
###                            out.save('pan' + str(imgnum-1) + '.jpg')

                        #image.PIL.save('img' + str(imgnum) + '.jpg')  #save image to disk 
                        #image = None

                    #elif out is not None:
                        #out.PIL.save('completed_pan' + str((int)(imgnum/4)) + '.jpg')  #save final panorama to disk



if __name__ == '__main__':
    
    initialize(my_recv_function, my_send_function, 250, 250)  #initialize the xbee connection

    try:
        getdatapr = mp.Process(target=get_data, args=())
        plotpr = mp.Process(target=plot_cont, args=(9999999,))

        getdatapr.start()
        plotpr.start()

        getdatapr.join()
        plotpr.join()

    except KeyboardInterrupt:
        getdatapr.terminate()
        plotpr.terminate()

