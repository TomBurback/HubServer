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
#
# Robot_blip_2-Marianne_Gagnon-299056732.mp3 
# used from http://soundbible.com/1669-Robot-Blip-2.html under the
# https://creativecommons.org/licenses/by/3.0/us/ license. No changes
# were made to the file.
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

#Text to speech
import pyttsx3

#Search Engines
import wolframalpha
import wikipedia

#Wolfram Alpha api access token
wolframalpha_access_token = '6GKWTW-YETULJ3QT6'

#Misc
import sys
from datetime import datetime
from playsound import playsound

#Instantiate text to speech engine
engine = pyttsx3.init()

#Welcome the user and announce checks.
print("[HubServer Voice Assistant] v. 1.0\nWelcome! Starting up...")
engine.say("Welcome. Start up sequence initiated.")
engine.runAndWait()

#Instantiate Speech Recognizer
engine.say("Initializing speech recognition.")
engine.runAndWait()
r = sr.Recognizer()
engine.say("OK.")
engine.runAndWait()

#!!! MUST BE UPDATED FOR SERVER !!!#
try:
	#Open COM port
	engine.say("Opening communication port.")
	engine.runAndWait()
	ser_port = serial.Serial('COM4') #Must be updated to match COM port number of server
	engine.say("OK.")
	engine.runAndWait()
except serial.serialutil.SerialException:
	print("[ERROR] Could not open COM port! Arduino is likely disconnected! Exiting...")
	engine.say("[ERROR] Could not open communication port! Arduino is likely disconnected! Exiting...")
	engine.runAndWait()
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
try:
	#Link to Porcupine python binding. Necessary to import Porcupine.
	sys.path.append(os.path.join(os.path.dirname(__file__), PATH_TO_PYTHON_BINDING))
	#Import the Porcupine wake word detection engine.
	engine.say("Importing Porcupine wake word detection engine!")
	engine.runAndWait()
	from porcupine import Porcupine
	engine.say("OK.")
	engine.runAndWait()
except ModuleNotFoundError:
	print("[ERROR] Can't find Porcupine module! Check PATH_TO_PYTHON_BINDING string. Exiting...")
	engine.say("[ERROR] Can't find Porcupine module! Check PATH TO PYTHON BINDING string. Exiting... ")
	engine.runAndWait()
	sys.exit()

try:
	#Instantiate Porcupine using provided file paths.
	engine.say("Initializing Porcupine wake word detection engine!")
	engine.runAndWait()
	handle = Porcupine(library_path, model_file_path, keyword_file_paths=keyword_file_paths, sensitivities=sensitivities)
	engine.say("OK.")
	engine.runAndWait()
except IOError:
	print("[ERROR] Can't instantiate Porcupine! Check library, model, and keyword paths. Check sensitivities. Exiting...")
	engine.say("[ERROR] Can't instantiate Porcupine! Check library, model, and keyword paths. Check sensitivities. Exiting...")
	engine.runAndWait()
	sys.exit()

#Instantiate Wolfram Alpha API	
engine.say("Initializing Wolfram Alpha!")
engine.runAndWait()
wolf_client = wolframalpha.Client(wolframalpha_access_token)
engine.say("OK.")
engine.runAndWait()

#Calibrate microphone
source = sr.Microphone()
with sr.Microphone() as source:
	print("Silence please. Calibrating microphone...")  
	engine.say("Silence please. Calibrating microphone...")
	engine.runAndWait()
	# listen for 5 seconds and create the ambient noise energy level  
	r.adjust_for_ambient_noise(source, duration=5)  
	print("Microphone calibrated.")
	engine.say("Microphone calibrated.")
	engine.runAndWait()

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
	engine.say('Listening for keyword porcupine...')
	engine.runAndWait()

	#Main loop
	while True:
			#Read from audio stream
			pcm = audio_stream.read(handle.frame_length)
			pcm = struct.unpack_from("h" * handle.frame_length, pcm)
			result = handle.process(pcm)
			if result:
				print('[%s] detected keyword' % str(datetime.now()))
				playsound("Robot_blip_2-Marianne_Gagnon-299056732.mp3")
				with sr.Microphone() as source:
					print("Listening...")
					#Grab microphone data
					audioData = r.listen(source)
					#Try and recognize it
					try:
						text = r.recognize_wit(audioData, wit_access_token)
						print("User said " + text)
						if("light" in text and "on" in text):
							print("Turning light on!")
							engine.say("Turning light on!")
							engine.runAndWait()
							ser_port.write(b'11')
						elif("light" in text and "off" in text):
							print("Turning light off!")
							engine.say("Turning light off!")
							engine.runAndWait()
							ser_port.write(b'10')
						else: 
							try: #Query Wolfram Alpha for answer to potential question
								res = wolf_client.query(text)
								output = next(res.results).text
								print("Wolfram Alpha: ")
								print(output)
								engine.say(output)
								engine.runAndWait()
							except: #If Wolfram Alpha can not answer, query Wikipedia
								output = wikipedia.summary(text)
								print("Wikipedia: ")
								print(output)
								engine.say(output)
								engine.runAndWait()
					except:
						print("Sorry, I didn't get that!")
						engine.say("Sorry, I didn't get that!")
						engine.runAndWait()
				print('\nListening for keyword porcupine...')
				
except KeyboardInterrupt:
		print("Exiting!")

finally:
    if handle is not None:
        handle.delete()

    if audio_stream is not None:
        audio_stream.close()

    if pa is not None:
        pa.terminate()