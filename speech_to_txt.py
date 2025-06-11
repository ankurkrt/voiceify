from threading import Thread
from queue import Queue

import speech_recognition as sr

audio_txt = ""  # this will hold the recognized text from the audio

r = sr.Recognizer()
audio_queue = Queue()

def parse_txt_using_llm(txt):
    # This function should contain the logic to process the recognized text with your LLM
    # For demonstration, we'll just print the text
    print(txt)

def audio_to_txt():
    # this runs in a background thread
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None: break  # stop processing if the main thread is done
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            audio_txt = audio_txt + ' ' + r.recognize_google(audio, language="en-in")  # recognize the speech in the audio and print it
            parse_txt_using_llm(audio_txt)  # process the recognized text with your LLM function
        except sr.UnknownValueError:
            print(":(")
        except sr.RequestError as e:
            print("Error {0}".format(e))

        audio_queue.task_done()  # mark the audio processing job as completed in the queue

# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=audio_to_txt)
recognize_thread.daemon = True
recognize_thread.start()

with sr.Microphone() as source:
    try:
        print("Please speak something...")
        r.adjust_for_ambient_noise(source)  # adjust for ambient noise to improve recognition accuracy
        while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop