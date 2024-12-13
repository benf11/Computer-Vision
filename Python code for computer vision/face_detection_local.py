#OpenCV face detection and servo control, taking place entirely on the raspberry pi.
#pigpio needs to be initialised before running this file (-sudo pigpiod) or it will not run.

import cv2 as cv
import time
import pigpio

#load in webcam feed using openCV
capture = cv.VideoCapture(0)
frame_w = 160
frame_h = 90
capture.set(cv.CAP_PROP_FRAME_WIDTH,frame_w)
capture.set(cv.CAP_PROP_FRAME_HEIGHT,frame_h)

#import face lbp cascade
lbp_cascade = cv.CascadeClassifier('lbpcascade_frontalface.xml')

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

#loop over each video frame
while True:
    isTrue, frame = capture.read()
    #detect faces within grayscale image
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces_rect = lbp_cascade.detectMultiScale(gray, 1.1, 3)

    #pull coordinates for the largest face detected
    areas = []
    for(x,y,w,h) in faces_rect:
        areas.append(w*h)
    if len(areas) > 0:
        target_index = areas.index(max(areas))
        target = faces_rect[target_index]

        x_def = target[0]
        y_def = target[1]
        width = target[2]
        height = target[3]

        #rotate servos depending on face position
        xpos = int(x_def+(width/2))
        angle_pan = -int(0.2*((frame_w/2)-xpos))
        pwm.set_servo_pulsewidth(servo_pan,1500+(1000*angle_pan/90))
        
        ypos = int(y_def+(height/2))
        angle_tilt = -int(0.2*((frame_h/2)-ypos))
        pwm.set_servo_pulsewidth(servo_tilt,1500+(1000*angle_tilt/90))

        #mark down position of the detected face on video feed
        cv.circle(frame,(xpos,ypos), 5, (0,255,0), -1)

    cv.imshow('Video', frame)
    #ends video feed if d key is pressed
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

#clean everything up
pwm.set_PWM_dutycycle(servo_pan,0)
pwm.set_PWM_dutycycle(servo_tilt,0)
pwm.set_PWM_frequency(servo_pan,0)
pwm.set_PWM_frequency(servo_tilt,0)
capture.release()
cv.destroyAllWindows()