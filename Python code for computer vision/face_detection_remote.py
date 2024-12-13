#OpenCV face detection, taking place remotely on server (laptop) side. Angle info is sent to the raspberry pi
#for servo control.

import cv2 as cv
import socket
import time

ip = '1.2.3.4'
inet_port = 12345

bluetooth_mac = '00.00.00.00.00.00'
bluetooth_port = 4

#establish a connection with the client connected to the same wifi network (pi):
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip,inet_port))
#alternatively using bluetooth:
'''server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server.bind((bluetooth_mac,blueooth_port))'''
server.listen()
clientsocket,address = server.accept()
print('stream started')

#load in webcam feed using openCV
capture = cv.VideoCapture(0)
frame_w = 160
frame_h = 90
capture.set(cv.CAP_PROP_FRAME_WIDTH, frame_w)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, frame_h)

#load in face lbp cascade
lbp_cascade = cv.CascadeClassifier('lbpcascade_frontalface.xml')

while True:
    isTrue, frame = capture.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #detect faces within grayscale image
    faces_rect = lbp_cascade.detectMultiScale(gray, 1.1,3)

    #pull coordinates for the largest face detected
    areas = []
    for (x, y, w, h) in faces_rect:
        areas.append(w*h)
    if len(areas) > 0:
        target_index = areas.index(max(areas))
        target = faces_rect[target_index]

        x_def = target[0]
        y_def = target[1]
        width = target[2]
        height = target[3]

        xpos = int(x_def + (width/2))
        ypos = int(y_def + (height / 2))

        #determine the servos' angle of rotation depending on face position
        angle_pan = int(0.4 * ((frame_w/2) - xpos))
        angle_tilt = int(0.4 * ((frame_h/2) - ypos))

        #mark down position of the detected face on video feed
        cv.circle(frame,(xpos,ypos),5,(0,255,0),-1)

        #send angle info over to the pi
        message = f"{angle_pan} {angle_tilt}"
        clientsocket.send(message.encode('utf-8'))

        cv.imshow('Video', frame)
    #ends video feed if d key is pressed
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

server.close()
capture.release()
cv.destroyAllWindows()