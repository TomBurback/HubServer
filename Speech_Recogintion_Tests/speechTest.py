import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
	print("Speak something: \n")
	audioData = r.listen(source)
	try:
		text = r.recognize_google(audioData)
		print("You said " + text)
	except:
		print("Sorry, I didn't get that!")