#MediaPipe hand detection, taking place remotely on server (laptop) side. Angle info is sent to the raspberry pi
#for servo control.

import mediapipe as mp
import cv2 as cv
import numpy as np
import math
import socket

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

#load and configure MediaPipe's hand detection solution
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5,max_num_hands=1)

#load in webcam feed using openCV
capture = cv.VideoCapture(0)
frame_w = 640
frame_h = 480
capture.set(cv.CAP_PROP_FRAME_WIDTH, frame_w)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, frame_h)

while True:
    isTrue, frame = capture.read()

    #MediaPipe's hand detection is done using the RBG colour space. openCV's default colour space is
    #BGR so temporary conversion is required. (rgb = the frame that mediaPipe uses to detect hands,
    #img = the frame that openCV displays as a live video feed).

    frame.flags.writeable = False
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    detected_hands = hands.process(rgb)
    frame.flags.writeable = True

    img = cv.cvtColor(rgb, cv.COLOR_RGB2BGR)

    if detected_hands.multi_hand_landmarks:

        #pull coordinates for the palm [0], thumb [4], and index finger [8].
        palm_x = int(frame_w*detected_hands.multi_hand_landmarks[0].landmark[0].x)
        palm_y = int(frame_h*detected_hands.multi_hand_landmarks[0].landmark[0].y)
        thumb_x = int(frame_w*detected_hands.multi_hand_landmarks[0].landmark[4].x)
        thumb_y = int(frame_h*detected_hands.multi_hand_landmarks[0].landmark[4].y)
        index_x = int(frame_w*detected_hands.multi_hand_landmarks[0].landmark[8].x)
        index_y = int(frame_h*detected_hands.multi_hand_landmarks[0].landmark[8].y)

        for hand in detected_hands.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

        #draw additional markings around the palm, thumb, and index finger.
        cv.line(img, (index_x, index_y), (thumb_x, thumb_y), (0, 0, 0), 2)

        cv.circle(img, (palm_x, palm_y), 7, (0,0,0), -1)
        cv.circle(img, (thumb_x, thumb_y), 7, (0,0,0), -1)
        cv.circle(img, (index_x, index_y), 7, (0,0,0), -1)

        cv.circle(img, (palm_x, palm_y), 5, (0, 255, 0), -1)
        cv.circle(img, (thumb_x, thumb_y), 5, (255, 0, 0), -1)
        cv.circle(img, (index_x, index_y), 5, (255, 0, 0), -1)

        #calculate the angle of separation betwen the palm, thumb, and index finger using the cosine law.
        p_12 = math.dist((palm_x, palm_y),(thumb_x, thumb_y))
        p_13 = math.dist((palm_x, palm_y), (index_x, index_y))
        p_23 = math.dist((thumb_x, thumb_y), (index_x, index_y))

        angle = (180/3.14)*math.acos(((p_12**2)+(p_13**2)-(p_23**2))/(2*p_12*p_13))

        #ensure that the angle does not exceed the servos' range of motion.
        if angle < 125:
            angle_pan = int(angle)-45
            angle_tilt = -int(angle)+45
            #send angle info over to the pi
            message = f"{angle_pan} {angle_tilt}"
            clientsocket.send(message.encode('utf-8'))

    cv.imshow('ben f', img)
    #ends video feed if d key is pressed
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()