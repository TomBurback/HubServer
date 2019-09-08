########################################################################
# HubServer Voice Assistant
#
# Author: burbacktg
# Date: 8/23/19
#
# !!!ALERT!!!: file paths for the Porcupine wake word detection engine
# must be updated for platform operating system.
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
#
# !!!ALERT!!!: COM port must be updated to match COM port number on
# individidual computer.
#!!! MUST BE UPDATED FOR SERVER !!!#
COM_PORT = "COM4"
#!!! MUST BE UPDATED FOR SERVER !!!#
#
# !!!ALERT!!!: PATH_TO_VLC_EXECUTABLE must be set to vlc.exe. PATH_TO_FIREPLACE_VIDEO must be updated to file location.
#!!! MUST BE UPDATED FOR SERVER !!!#
PATH_TO_VLC_EXECUTABLE = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
PATH_TO_FIREPLACE_VIDEO = "C:\\Users\\burbacktg\\Documents\\HubServer\\fireplace.mp4"
#!!! MUST BE UPDATED FOR SERVER !!!#
#
# !!!ALERT!!!: PATH_TO_CLOCK must be set to clock.py.
#!!! MUST BE UPDATED FOR SERVER !!!#
PATH_TO_CLOCK = "C:\\Users\\burbacktg\\Documents\\HubServer\\clock.py"
#!!! MUST BE UPDATED FOR SERVER !!!#
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

#Clock
import threading
from tkinter import *
from tkinter import ttk
from tkinter import font
import time

#Wolfram Alpha api access token
wolframalpha_access_token = '6GKWTW-YETULJ3QT6'

#Misc
import sys
from datetime import datetime
from playsound import playsound
import subprocess

#Instantiate text to speech engine
engine = pyttsx3.init()

#Uses text to speech to speak the given phrase		
def speak(phrase):
	engine.say(phrase)
	engine.runAndWait()
	
#This function launches whatever file is found at the path
#Plays in fullscreen and loops	
#Returns program instance! Necessary to close program!
def launch_vlc_with_file(file_path):
	print("Launching " + file_path + " in VLC!")
	return subprocess.Popen(PATH_TO_VLC_EXECUTABLE + " --fullscreen " + " --repeat " + file_path)

def start_clock(PATH_TO_CLOCK):
	print("Launching clock!")
	return subprocess.Popen("python " + PATH_TO_CLOCK)

#Welcome the user and announce checks.
print("[HubServer Voice Assistant] v. 1.0\nWelcome! Starting up...")
speak("Welcome. Start up sequence initiated.")

#Instantiate Speech Recognizer
speak("Initializing speech recognition.")
r = sr.Recognizer()
speak("OK.")

#Open communication with the Arduino over serial
#try:
#	#Open COM port
#	speak("Opening communication port.")
#	ser_port = serial.Serial(COM_PORT) #Must be updated to match COM port number of server
#	speak("OK.")
#except serial.serialutil.SerialException:
#	print("[ERROR] Could not open COM port! Arduino is likely disconnected! Exiting...")
#	speak("[ERROR] Could not open communication port! Arduino is likely disconnected! Exiting...")
#	sys.exit()

#Try to import Porcupine. If error is detected, double check Porcupine wake word detection dependencies at the top of the program!
try:
	#Link to Porcupine python binding. Necessary to import Porcupine.
	sys.path.append(os.path.join(os.path.dirname(__file__), PATH_TO_PYTHON_BINDING))
	#Import the Porcupine wake word detection engine.
	speak("Importing Porcupine wake word detection engine!")
	from porcupine import Porcupine
	speak("OK.")
except ModuleNotFoundError:
	print("[ERROR] Can't find Porcupine module! Check PATH_TO_PYTHON_BINDING string. Exiting...")
	speak("[ERROR] Can't find Porcupine module! Check PATH TO PYTHON BINDING string. Exiting... ")
	sys.exit()

try:
	#Instantiate Porcupine using provided file paths.
	speak("Initializing Porcupine wake word detection engine!")
	handle = Porcupine(library_path, model_file_path, keyword_file_paths=keyword_file_paths, sensitivities=sensitivities)
	speak("OK.")
except IOError:
	print("[ERROR] Can't instantiate Porcupine! Check library, model, and keyword paths. Check sensitivities. Exiting...")
	speak("[ERROR] Can't instantiate Porcupine! Check library, model, and keyword paths. Check sensitivities. Exiting...")
	sys.exit()

#Instantiate Wolfram Alpha API	
speak("Initializing Wolfram Alpha!")
wolf_client = wolframalpha.Client(wolframalpha_access_token)
speak("OK.")

#Calibrate microphone
source = sr.Microphone()
with sr.Microphone() as source:
	print("Silence please. Calibrating microphone...")  
	speak("Silence please. Calibrating microphone...")
	# listen for 5 seconds and create the ambient noise energy level  
	r.adjust_for_ambient_noise(source, duration=5)  
	print("Microphone calibrated.")
	speak("Microphone calibrated.")
	
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
	speak('Listening for keyword porcupine...')
	
	#Fireplace instance variable
	#Instance allows for termination of the vlc program
	#None if not currently running
	fireplace_instance = None
	
	#Clock
	clock_instance = start_clock(PATH_TO_CLOCK)
	
	#Main loop
	while True:
			#Read from audio stream
			pcm = audio_stream.read(handle.frame_length)
			pcm = struct.unpack_from("h" * handle.frame_length, pcm)
			result = handle.process(pcm)
			if result:
				print('[%s] detected keyword' % str(datetime.now()))
				playsound("Robot_blip_2-Marianne_Gagnon-299056732.mp3")
				### AUDIO RETREIVAL ###
				with sr.Microphone() as source:
					print("Listening...")
					#Grab microphone data
					audioData = r.listen(source)
					#Try and recognize it
					try:
						### SPEECH RECOGNITION ###
						#Send audioData to Wit.ai to recognize speech
						#text is speech converted to text
						text = r.recognize_wit(audioData, wit_access_token)
						#Print what the user said
						print("User said " + text)
						### COMMAND IMPLEMENTATION ###
						#If "light" and "on" are spoken, turn the LED on
						if("light" in text and "on" in text):
							print("Turning light on!")
							speak("Turning light on!")
#							ser_port.write(b'11')
						#If "light" and "off" are spoken, turn the LED off
						elif("light" in text and "off" in text):
							print("Turning light off!")
							speak("Turning light off!")
#							ser_port.write(b'10')
						#If "light" or "on" or "start" and "fireplace" is heard, launch the fireplace
						elif(("light" in text or "on" in text or "start" in text) and "fireplace" in text):
							#If the fireplace_instance isn't None, the fireplace is already running
							if(fireplace_instance != None):
								speak("The fireplace is already running!")
							else: #If it's not running, launch the fireplace
								print("Starting the fireplace!")
								speak("OK!")
								#Update the fireplace_instance to the current instance of VLC
								fireplace_instance = launch_vlc_with_file(PATH_TO_FIREPLACE_VIDEO)
								
								#STOP CLOCK
								clock_instance.terminate()
								clock_instance = None
						#If "extinguish" or "off" or "stop" and "fireplace" is heard, close the fireplace
						elif(("extinguish" in text or "off" in text or "stop" in text) and "fireplace" in text):
							#If the fireplace_instance is None, the fireplace isn't running
							if(fireplace_instance == None):
								speak("The fireplace is not currently running!")
							else: #If it is running, close the fireplace 
								print("Stopping the fireplace!")
								speak("OK!")
								#Terminate the current instance of VLC
								fireplace_instance.terminate()
								#Set the fireplace_instance to None to show the fireplace is no longer running
								fireplace_instance = None
								
								#START CLOCK
								clock_instance = start_clock(PATH_TO_CLOCK)
						elif("nevermind" in text or "stop" in text or "cancel" in text or "forget it" in text):
							print("OK!")
						else: 
							try: #Query Wolfram Alpha for answer to potential question
								res = wolf_client.query(text)
								output = next(res.results).text
								print("Wolfram Alpha: ")
								print(output)
								speak(output)
							except: #If Wolfram Alpha can not answer, query Wikipedia
								output = wikipedia.summary(text)
								print("Wikipedia: ")
								print(output)
								speak(output)								
					except:
						print("Sorry, I didn't get that!")
						speak("Sorry, I didn't get that!")						
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