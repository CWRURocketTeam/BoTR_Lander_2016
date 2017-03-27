#include "drivers.h"
#include "Adafruit_VC0706.h"

SoftwareSerial cameraconnection=SoftwareSerial(2,3);

Adafruit_VC0706 cam=Adafruit_VC0706(&cameraconnection);

void camera_setup(channel_number){
  //default is apparently pin 10
  pinMode(channel_number,OUTPUT);
  Serial.begin(9600);
  cam.setImageSize(VC0706_640x480);
}

 //Parameters for the callback function: byte buffer, number of bytes in buffer, whether this is the last readout or not, user provided parameter
void camera_read(void (*callback)(char* bytebuffer,int numberBytes,char last,void* filename),void*parameter)){
  cam.takePicture();
  //idk how you're storing this file
  File imgFile=SD.open(filename,FILE_WRITE);
  
  //idk if correct
  pinMode(8,OUTPUT);
  
  //1 if last, 0 else
  while(last!=1){
    if(min(32,numberBytes)==32){
      imgFile.write(cam.readPicture(32),32);
      numberBytes-32;
    }
    else{
      imgFile.write(cam.readPicture(numberBytes),numberBytes);
      last=1;
    }
  }
}

void loop(){
}
