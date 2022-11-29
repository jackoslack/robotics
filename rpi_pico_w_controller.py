# Program to send commands to a local
# Pico Web Server embedded in a robot
# Based on Tony Goodhew program to read
# RGB values from a local Pico Web Server
# Tony Goodhew 5th July 2022
# https://thepihut.com/blogs/raspberry-pi-tutorials/wireless-communication-between-two-raspberry-pi-pico-w-boards

import urequests
import gc
import machine

i2c = machine.I2C(id=0, scl=machine.Pin(17), sda=machine.Pin(16))

from PiicoDev_SSD1306 import *
from PiicoDev_CAP1203 import PiicoDev_CAP1203
from PiicoDev_MPU6050 import PiicoDev_MPU6050
from PiicoDev_Unified import sleep_ms # Cross-platform compatible sleep function

debug = False
address = ''                       # Robot ip
robot = ''                         # Robot name
to = 1                             # Timeout for request
new_robot = True

# Initialise I2C devices
touchSensor = PiicoDev_CAP1203(touchmode='single', sensitivity=6, sda=machine.Pin(16), scl=machine.Pin(17)) # Low sensitivity
display = create_PiicoDev_SSD1306(sda=machine.Pin(16), scl=machine.Pin(17))
motion = PiicoDev_MPU6050(sda=machine.Pin(16), scl=machine.Pin(17))
touch = ''

def start_display():
    display.fill(0)
    display.text(" PiicoDev",30,20, 1)
    display.text("Controller",30,40, 1)
    display.show()
    sleep_ms(5000)
        
def instruct():        # Show arrows
    # Menu
    display.fill(0)
    display.text("Buttons",30,5, 1)
    display.text(" 1     2    3",0,20, 1)
    display.text("Yes/ Robot No/",0,35, 1)
    display.text("Nod  Menu Shake",0,45, 1)
    display.show()
    sleep_ms(5000)
    # Directions
    display.fill(0)
    display.text("^",64,5, 1)
    display.text("|",64,15, 1)
    display.text("<-  Tilt  ->",20,30, 1)
    display.text("|",64,40, 1)
    display.text("v",64,50, 1)
    display.show()
    sleep_ms(5000)

def choose_robot():# display startup menu
    global address
    print('In choose_robot')
    display.fill(0)
    display.text("Choose Robot",10,10, 1)
    display.text("1 -> Johnny5",10,25, 1)
    display.text("2 -> Zero Rover",10,35, 1)
    display.text("3 -> SMARS 1",10,45, 1)
    display.show()
    touch = ''
    sleep_ms(500)
    
    touch = touchSensor.read()
    # Wait for response
    while not (touch[1] or touch[2] or touch[3]):
        touch = touchSensor.read()
        sleep_ms(250)
        
    if touch[1]:
        address = 'http://192.168.0.18'
        robot = 'Johnny5'
        touch[1] = 0   
        Johnny5()
        
    if touch[2]:
        address = 'http://192.168.0.30:8000'
        robot = 'Zero Rover'
        touch[2] = 0
        ZeroRover()        
        
    if touch[3]:
        address = 'http://192.168.0.??'
        robot = 'SMARS 1'
        touch[3] = 0
        SMARS1()
        
def Johnny5(): 
    # display controller status
    print('Starting Johnny5 Controller')
    display.fill(0)
    display.text("Johnny5",25,20, 1)
    display.text("Controller",20,40, 1)
    display.show()
    sleep_ms(2000)        
    gc.collect()
    
def ZeroRover(): 
    # display controller status
    print('Starting Zero Rover Controller')
    display.fill(0)
    display.text("Pi Zero Rover",17,20, 1)
    display.text("Controller",20,40, 1)
    display.show()
    sleep_ms(2000)        
    gc.collect()
    
def SMARS1(): 
    # display controller status
    print('Starting SMARS 1 Controller')
    display.fill(0)
    display.text("SMARS 1",22,20, 1)
    display.text("Controller",20,40, 1)
    display.show()
    sleep_ms(2000)         
    gc.collect()
    
def send(command):
    bugprint('Sending ' + command)
    s = command.upper()
    display.fill(0)
    display.text(s ,30,20, 1)
    display.show()
    try:
        response = urequests.get(address + "/" + command, timeout=to)
        if response.status_code == 200:
            message = 'received'
            
        bugprint(message)
        display.text(message,20,40, 1)
        display.show()
        sleep_ms(250)    
        gc.collect() 
    except:        
        bugprint('Sending ' + command)    
        display.fill(0)
        display.text('Send',42,10, 1)
        display.text(command.upper(),40,30, 1)
        display.text('failed.' ,42,50, 1)
        display.show()
        oldDir = ''
        bugprint('Connection failed.')
      
def bugprint(txt):
    if debug:
        print(txt)
    
xStat = ''
yStat = ''
oldDir = ''

start_display()
choose_robot()

while True:
    if new_robot:
        instruct()
        new_robot = False

    touch = touchSensor.read()
    bugprint(touch)
    
    # Button 1 controls Yes/Nod
    if touch[1] :
        touch[1] = 0
        send('nod')
        
    # Button 2 controls Robot Menu
    if touch[2] :
        touch[2] = 0
        new_robot = True
        choose_robot()
        
    # Button 3 controls No/Shake
    if touch[3] :
        touch[3] = 0
        send('shake')
        
    # Accelerometer data
    accel = motion.read_accel_data() # read the accelerometer [ms^-2]
    
    aX = accel["x"]  # Left/Right
    aY = accel["y"]  # Forward/Reverse
    aZ = accel["z"]  # Not Used
    
    # Handle left/right input
    if (aX > 2) :
        xStat = 'r'   # left
        
    elif aX < -2 :
        xStat = 'l'   # right
        
    else:
        xStat = 's'   # neither        
     
    # Handle forward/reverse input
    if aY < -2:
        yStat = 'f'   # forward
        
    elif aY > 2 :
        yStat = 'b'   # backwards
        
    else:
        yStat = 's'   # stop if not l/r 
        
    dir = (yStat + xStat)
    
    bugprint('Direction = ' + dir)
    
    # Send but only send if it hasn't already been sent    
    if dir == 'fs' and oldDir != 'fs':   
        send('forward')
        
    if dir == 'bs' and oldDir != 'bs':
        send('reverse')        
        
    if dir == 'fl' and oldDir != 'fl':
        send('fleft')
        
    if dir == 'fr' and oldDir != 'fr':
        send('fright')
        
    if dir == 'bl'and oldDir != 'bl':
        send('bleft')
               
    if dir == 'br'and oldDir != 'br':
        send('bright')
        
    if dir == 'ss'and oldDir != 'ss':
        send('stop')
        
    if dir == 'sl'and oldDir != 'sl':
        send('left')
        
    if dir == 'sr'and oldDir != 'sr':
        send('right')
                      
    oldDir = dir  # Record last instruction sent
    yStat = ''
    bugprint('Old direction ' + oldDir)
        
    sleep_ms(50)    
    
display.fill(0)
display.show()
