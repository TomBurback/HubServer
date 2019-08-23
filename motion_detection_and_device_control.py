import cv2
import numpy as np
from playsound import playsound
import serial

#Open serial port on COM4
ser_port = serial.Serial('COM4')

#Webcam capture
video = cv2.VideoCapture(0)

#history, Threshold, Detect Shadows
fgbg = cv2.createBackgroundSubtractorMOG2(300, 400, True)

#Current frame number
currentFrameNumber = 0

#Number of frames since last activation
frameCount = 0

#Current frame state: motion = true, no motion = false
currentFrameState = False
#Last frame state: motion = true, no motion = false
lastFrameState = False

while True:
	#return value and current frame
	ret, frame = video.read()

	#check if a current frame actually exists
	if not ret:
		break
	
	#update frames since last activation
	frameCount += 1

	currentFrameNumber += 1

	#get the foreground mask
	fmask = fgbg.apply(frame)

	#count all nonzero pixels within mask
	count = np.count_nonzero(fmask)

	#print("Frame: %d, Pixel Count: %d" % (frameCount, count))

	cv2.imshow("Frame", frame)
	#cv2.imshow("Mask", fmask)

	if (currentFrameNumber > 1 and count > 5000):
		currentFrameState = True
	else:
		currentFrameState = False

	#if it's been 45 frames since the last activation
	if frameCount > 45:
		#if the current frame has motion but the last frame didn't, say it
		if currentFrameState == True and lastFrameState == False:
			#turn on LED
			ser_port.write(b'1')
			playsound("motion_trigger.mp3")
			#reset frame count since last activation
			frameCount = 0
			
	#update last frame
	lastFrameState = currentFrameState
	#turn off LED
	ser_port.write(b'0')

	k = cv2.waitKey(40) & 0xff
	if k == 27: #if escape key is pressed
		break

video.release()
cv2.destroyAllWindows()
