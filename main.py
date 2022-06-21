import math
import socket
import threading
import time
import pifacedigitalio as p
from datetime import datetime
from tkinter import *

#fonction start chrono
def start_chronometer(h=0, m=0, s=0):
    global process
    try:
        stop_chronometer()
    except:
        pass

    if s >= 60:
        s = 0
        m = m + 1
        if m >= 60:
            m = 0
            h = h + 1
            if h >= 24:
                h = 0
    if s < 10:
        secss = '0' + str(s)
    else:
        secss = str(s)
    if m < 10:
        minss = '0' + str(m)
    else:
        minss = str(m)
    if h < 10:
        hourss = '0' + str(h)
    else:
        hourss = str(h)

    chrono['text'] = hourss + ":" + minss + ":" + secss
    process = chrono.after(1000, start_chronometer, h, m, (s + 1))

#fonction stop chrono
def stop_chronometer():
    try:
        global process
        chrono.after_cancel(process)
    except:
        pass

#fonction pause chrono
def resume_chronometer():
    try:
        global process
        hours = int(chrono['text'].split(':')[0])
        mins = int(chrono['text'].split(':')[1])
        secs = int(chrono['text'].split(':')[2]) + 1
        stop_chronometer()
        start_chronometer(h=hours, m=mins, s=secs)
    except:
        pass

#fonction heure
def clock():

    C.delete("clock")
    C.create_text(width / 2, width / 2, font=("ds-digital", 50, 'bold'), text=datetime.now().strftime("%H:%M:%S"),fill="#0003FF", tags="clock")
    time.sleep(0.6)

#fonction création secondes
def trigo():
    second = datetime.now().second

    if second == 0:
        C.delete("second")
    else:
        second = second - 15
        for angle in range(-15, 45):
            if angle <= second:
                angle = ((angle * 6) * math.pi) / 180
                x = rayon + ((rayon * 0.80) * math.cos(angle))
                y = rayon + ((rayon * 0.80) * math.sin(angle))
                x1 = int(x) - 5
                y1 = int(y) - 5
                x2 = int(x) + 5
                y2 = int(y) + 5
                C.create_oval(x1, y1, x2, y2, fill='#FFAA00', tags="second")
                C.pack()
#fonction start secondes + heure
def second():
    while True:
        clock()
        trigo()

#fonctio input piface raspberry
def piface_read():
    while True:
        if p.digital_read(0) == 1:
            sock.send(bytes("9999,0\r\n", "UTF-8"))
            time.sleep(0.3)
        elif p.digital_read(1) == 1:
            sock.send(bytes("9998,0\r\n", "UTF-8"))
            time.sleep(0.3)
        elif p.digital_read(2) == 1:
            sock.send(bytes("9997,0\r\n", "UTF-8"))
            time.sleep(0.3)
        elif p.digital_read(3) == 1:
            sock.send(bytes("9996,0\r\n", "UTF-8"))
            time.sleep(0.3)

#fonction serveur tcp
def onair():
    global connected
    global sock
    global title
    while True:
        try:
            if connected is False:
                sock.connect(('192.168.2.166', 65432))
                print("Connexion au serveur réussie")
            message = sock.recv(1024).decode("UTF-8")
            if message.find("10,1") != -1:
                stop_chronometer()
                start_chronometer()
                chrono.pack()
                p.digital_write(0, 1)
                title.config(text="ON AIR", font=("Avenir-Black", 300), bg='#ff0000', fg='white', anchor=CENTER)
            elif message.find("10,0") != -1:
                stop_chronometer()
                p.digital_write(0, 0)
                title.config(text="ON AIR", font=("Avenir-Black", 300), bg='#4D0000', fg='black', anchor=CENTER)

        except socket.error:
            connected = False
            sock = socket.socket()
            print("Connexion perdue... reconnexion")
            while not connected:
                try:
                    sock.connect(('192.168.2.166', 65432))
                    connected = True
                    print("Re-connexion réussie")
                except socket.error:
                    time.sleep(0.5)
    sock.close()


#init
p.init()

root = Tk()
root.title("On Air interface")
root.geometry("640x480")
root.config(background='#000000')
root.attributes("-fullscreen", True)

title = Label(root, text="ON AIR", font=("Avenir-Black", 300), bg='#4D0000', fg='black', anchor=CENTER)
title.config(anchor=CENTER)
title.pack()

msgserver = "10,0"
width = 300
rayon = width / 2
process = 0
connected = True

C = Canvas(root, bg="black", height=width, width=width, highlightthickness=0)

chrono = Label(root, fg='white', bg='black', font=("Avenir-Black", 50))
chrono['text'] = "00:00:00"

th1 = threading.Thread(target=onair)
th2 = threading.Thread(target=second)
th3 = threading.Thread(target=piface_read)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

for angle in range(0, 12):
    angle = ((angle * 30) * math.pi) / 180
    x = rayon + ((rayon * 0.90) * math.cos(angle))
    y = rayon + ((rayon * 0.90) * math.sin(angle))
    x1 = int(x) - 5
    y1 = int(y) - 5
    x2 = int(x) + 5
    y2 = int(y) + 5
    C.create_oval(x1, y1, x2, y2, fill='#0003FF')
    C.pack()
    chrono.pack()

C.create_oval(145, 25, 155, 35, fill='#FFAA00', tags="first")

th3.start()
th1.start()
th2.start()

root.mainloop()