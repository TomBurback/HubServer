import speech_recognition as sr
import serial

#Open COM4 port
ser_port = serial.Serial('COM4')

#Instantiate recognizer
r = sr.Recognizer()

while True:
	#Listen to the microphone
	with sr.Microphone() as source:
		print("Listening...")
		#Grab microphone data
		audioData = r.listen(source)
		#Try and recognize it
		try:
			text = r.recognize_google(audioData)
			print("You said " + text)
			if("LED" in text and "on" in text):
				ser_port.write(b'1')
			elif("LED" in text and "off" in text):
				ser_port.write(b'0')
		except:
			print("Sorry, I didn't get that!")