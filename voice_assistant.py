########################################################################
# HubServer Voice Assistant
#
# Author: burbacktg
# Date: 8/23/19
#
# !!!ALERT!!!: file paths for the Porcupine wake word detection engine
# must be updated for platform operating system. See code.
#
# !!!ALERT!!!: COM port must be updated to match COM port number on
# individidual computer. See code.
#
# Description:
#	This program monitors for the word "Porcupine" and 
#	listens to whatever command is given afterword. It
#	uses serial communication to send a signal to an Arduino 
# 	that can be programmed and hooked to whatever one desires.
########################################################################

#Hardware communication
import serial

#Speech recognition
import speech_recognition as sr

# Wit.ai api access token
wit_access_token = 'ZPLG244YIBKZODROIERY7KVRZHE2W37U'

#Wake word detection
import pyaudio
import struct
import os
import platform

#Misc
import sys
from datetime import datetime

#Instantiate Speech Recognizer
r = sr.Recognizer()

#Calibrate microphone
source = sr.Microphone()
with sr.Microphone() as source:
	print("Please wait. Calibrating microphone...")  
	# listen for 5 seconds and create the ambient noise energy level  
	r.adjust_for_ambient_noise(source, duration=5)  
	print("Microphone calibrated.")

#!!! MUST BE UPDATED FOR SERVER !!!#
try:
	#Open COM port
	ser_port = serial.Serial('COM4') #Must be updated to match COM port number of server
except serial.serialutil.SerialException:
	print("[ERROR] Could not open COM port! Arduino is likely disconnected! Exiting...")
	sys.exit()
#!!! MUST BE UPDATED FOR SERVER !!!#

#Porcupine wake word detection dependencies.
#These files and directories can be downloaded by cloning the Porcupine git repo found at: https://github.com/Picovoice/Porcupine
#They are necessary for this program to operate.
#!!! MUST BE UPDATED FOR SERVER !!!#
PATH_TO_PYTHON_BINDING = 'C:/Users/burbacktg/Documents/Porcupine/binding/python'
library_path = 'C:/Users/burbacktg/Documents/Porcupine/lib/windows/amd64/libpv_porcupine.dll' # Path to Porcupine's C library available under lib/${SYSTEM}/${MACHINE}/
model_file_path = 'C:/Users/burbacktg/Documents/Porcupine/lib/common/porcupine_params.pv' # It is available at lib/common/porcupine_params.pv
keyword_file_paths = ['C:/Users/burbacktg/Documents/Porcupine/keywords/porcupine_windows.ppn']
sensitivities = [0.5]
#!!! MUST BE UPDATED FOR SERVER !!!#

#Link to Porcupine python binding. Necessary to import Porcupine.
sys.path.append(os.path.join(os.path.dirname(__file__), PATH_TO_PYTHON_BINDING))
#Import the Porcupine wake word detection engine.
from porcupine import Porcupine

#Instantiate Porcupine using provided file paths.
handle = Porcupine(library_path, model_file_path, keyword_file_paths=keyword_file_paths, sensitivities=sensitivities)

try:
	#Instantiate pyaudio
	pa = pyaudio.PyAudio()
	#Open audio stream
	audio_stream = pa.open(
			rate=handle.sample_rate,
			channels=1,
			format=pyaudio.paInt16,
			input=True,
			frames_per_buffer=handle.frame_length)
	print('Listening for keyword porcupine...')

	#Main loop
	while True:
			#Read from audio stream
			pcm = audio_stream.read(handle.frame_length)
			pcm = struct.unpack_from("h" * handle.frame_length, pcm)
			result = handle.process(pcm)
			if result:
				print('[%s] detected keyword' % str(datetime.now()))
				with sr.Microphone() as source:
					print("Listening...")
					#Grab microphone data
					audioData = r.listen(source)
					#Try and recognize it
					try:
						text = r.recognize_wit(audioData, wit_access_token)
						print("You said " + text)
						if("light" in text and "on" in text):
							ser_port.write(b'1')
						elif("light" in text and "off" in text):
							ser_port.write(b'0')
					except:
						print("Sorry, I didn't get that!")
				
				
except KeyboardInterrupt:
		print("Exiting!")

finally:
    if handle is not None:
        handle.delete()

    if audio_stream is not None:
        audio_stream.close()

    if pa is not None:
        pa.terminate()