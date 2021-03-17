
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import re
import os
import smtplib
from email.message import EmailMessage
import sqlite3

# creating current atmosphere
class Date():
    time = datetime.datetime.now()
    day = time.strftime("%A")
    date, month, year = time.date().day, time.strftime("%B"), time.date().year
    h, m, zone = time.hour, time.minute, "am"
    if h == 0:
        h = 12
    elif h > 12:
        h -= 12
        zone = "pm"

# your name
master = "meet"

# retriving your email and password
with open("info.txt",'r') as scanner:
    text = scanner.readlines()
    email = text[0].split(':- ')[1].replace("\n","")
    password = text[1].split(':- ')[1]

# set your web browser path
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# set your music directory path
music_path = "D:\\songs"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# initializing voice engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 175)

#connecting to database
conn = sqlite3.connect("email.sqlite")
cur = conn.cursor()


def speak(audio):
    # This function makes engine speak the string passed to it
    print(audio)
    engine.say(audio)
    engine.runAndWait()




def wishme(d1):
    # this function runs at the begining and wishes you according to current time
    if d1.zone == "am":
        speak(f"Good Morning {master}")
    elif d1.zone == "pm" and d1.h < 4:
        speak(f"Good Afternoon {master}")
    else:
        speak(f"Good Evening {master}")
    speak(f"It's {d1.h} {d1.m} {d1.zone}")
    speak("How may I help you?")


def takecommand():
    # this function uses your current mic to take input speaks it and returns it as string. If speech is un recognized you have to type in the string
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.....")
        # pausethreshold can be increased to increase wait time 
        # r.pause_threshold = 1
        r.energy_threshold = 350
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-in')
        print(query)
    except Exception:
        speak("Sorry i couldn't understand this please type:- ")
        query = input()
    return query


def sendemail(to):
    # This function takes name as input to whom we want to send email.
    # It returns any error occur or speaks email sent successfully
    # it takes email corresponding to name from database
    cur.execute('SELECT email FROM email WHERE name = ?', (to, ))
    receivers_email = cur.fetchone()
    # if name is not found in database it can create a record in database or send mail without adding to database
    if not receivers_email:
        speak("no such contact")
        speak("do you want to add new contact?")
        query = takecommand().lower()
        if 'yes' in query:
            contactadder(to)
            cur.execute('SELECT email FROM email WHERE name = ?', (to, ))
            receivers_email = cur.fetchone()
        else:
            speak("Enter mail address: ")
            r = input()
            receivers_email = []
            receivers_email.append(r)
    speak("sending email to "+to)
    # creates an object of email with properties such as subject, body, etc.
    msg = EmailMessage()
    msg['From'] = email
    msg['To'] = receivers_email
    speak("What should be the subject?")
    msg['Subject'] =  takecommand()
    speak("What should i say say?")
    msg.set_content(takecommand())
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
        server.login(email, password)
        server.send_message(msg)


def contactadder(name):
    # adds record to database
    speak("Please type in the email")
    email = input("Please type in the email:- ")
    speak(f"adding {name}")
    cur.execute('INSERT OR IGNORE INTO emails (name,email) VALUES(?,?)', (name, email))
    conn.commit()


if __name__ == "__main__":
    d1 = Date()
    wishme(d1)
    while True:
        query = takecommand().lower()
        if "search" in query:
            # searches on wikipedia
            if "on wikipedia" in query:
                speak("searching wikipedia...")
                se = re.findall('search (.+) on wikipedia', query)
                results = wikipedia.summary(se[0]+" according to ", sentences=2)
                print(results)
                speak(results)
            # opens youtube and searches given topic
            elif "on youtube" in query:
                speak("Opening youtube")
                se = re.findall("search (.+) on youtube", query)
                webbrowser.get("chrome").open_new_tab("https://www.youtube.com/results?search_query="+se[0])
            # searches on google
            else:
                speak("Opening google")
                se = re.findall("search (.+)", query)
                webbrowser.get("chrome").open_new_tab("https://www.google.com/search?q="+se[0])
        # plays music given in particular directory
        elif "play music" in query:
            speak("Playing music")
            songs = os.listdir(music_path)
            for num,i in enumerate(songs):
                print(str(num)+"  "+ i)
            song_number = int(input("Enter song number to be played:- "))
            os.startfile(os.path.join(music_path, songs[song_number]))
        # speaks current time
        elif "the time" in query:
            speak(f"It's {d1.h} {d1.m} {d1.zone}")
        # speaks current date
        elif "the date" in query:
            speak(f"It's {d1.day} {d1.date} {d1.month} {d1.year}")
        # speaks current day
        elif "the day" in query:
            speak(f"It's {d1.day}")
        # sends email
        elif "send email" in query:
            se = re.findall("to (.+)", query)
            try:
                sendemail(se[0])
                speak(f"Email sent to {se[0]}")
            except Exception as e:
                speak(f"Sorry {master} couldnt send email to {se[0]} due to {e}")
        # adds to database
        elif "to contact" in query:
            name = re.findall('add (.+?)\s', query)
            contactadder(name[0])
            speak(f"added {name[0]}")
        # starts python command prompt
        elif "start python" in query:
            speak("starting python")
            os.startfile("C:\\Users\\meetc\\AppData\\Local\\Programs\\Python\\Python39\\python.exe")
        # starts git cmd
        elif "start git" in query:
            speak("starting github")
            os.startfile("C:\\Program Files\\Git\\git-cmd.exe")
        # starts vlc
        elif "start vlc" in query:
            speak("starting VLC")
            os.startfile("C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe")
        break
