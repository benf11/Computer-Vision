#client (pi) side of computer vision projects where image processing is done remotely on
#another device. The pi's sole responsibilty is to recieve angle information to control
#the servos connected to it.
#this file is to be used in conjunction with face_detection_remote or mediapipe_hand_detection.

import time
import pigpio
import socket

ip = '1.2.3.4'
inet_port = 12345

bluetooth_mac = '00.00.00.00.00.00'
bluetooth_port = 4

#set up client side using sockets using the same wifi network
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip,inet_port))

#alternatively use bluetooth
'''client=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
client.connect((bluetooth_mac,bluetooth_port))'''
    
#set servo gpio pins (in this case 12 and 13) as outputs
servo_pan = 12
servo_tilt = 13
pwm = pigpio.pi()
pwm.set_mode(servo_pan, pigpio.OUTPUT)
pwm.set_mode(servo_tilt, pigpio.OUTPUT)

#assign 50hz pulse frequency to both servos
pwm.set_PWM_frequency(servo_pan,50)
pwm.set_PWM_frequency(servo_tilt,50)

#set both servos at 90 degrees to start
pwm.set_servo_pulsewidth(servo_pan,1500);
pwm.set_servo_pulsewidth(servo_tilt,1500);
time.sleep(1)

while True:
    message = (client.recv(1024).decode('utf-8'))
    angles = message.split(maxsplit = 1)
    print(angles)
    #socket sometimes causes two strings to be concactenated during data transfer leading to an invalid angle.
    #setting the max valid string length per packet to 3 filters out any of these events.
    if len(angles[0]) >3 or len(angles[1]) >3:
        continue
    angle_pan = int(angles[0])
    angle_tilt = int(angles[1])
    #direct the servos towards the particular angle
    pwm.set_servo_pulsewidth(servo_pan,1500+(1000*angle_pan/90))
    pwm.set_servo_pulsewidth(servo_tilt,1500+(1000*angle_tilt/90))
