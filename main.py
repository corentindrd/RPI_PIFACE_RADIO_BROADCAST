import math
import socket
import threading
import time
from datetime import datetime
from tkinter import *

try:
    import pifacedigitalio as p
except:
    pass

# fonction start chrono

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

# fonction stop chrono

def stop_chronometer():
    try:
        global process
        chrono.after_cancel(process)
    except:
        pass

# fonction pause chrono

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

# fonction création secondes

def trigo():
    while True:
        second = int(datetime.now().strftime("%S"))

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
                    C.place(relx=0.5, rely=0.5, anchor=CENTER)
            hour.config(text=datetime.now().strftime("%H:%M:%S"))

# fonction input piface raspberry

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

# fonction serveur tcp

def onair():
    global connected
    global sock
    global title
    while True:
        try:
            if connected is False:
                sock.connect((ipaddress, port))
                print("Connexion au serveur réussie")
            message = sock.recv(1024).decode("UTF-8")
            if message.find("10,1") != -1:
                stop_chronometer()
                start_chronometer()
                try:
                    p.digital_write(0, 1)
                except:
                    pass
                title.config(text="ON AIR", font=("Avenir-Black", title_size), bg='#ff0000', fg='white')
                chrono.place(relx=0.5, rely=0.9, anchor=CENTER)
            elif message.find("10,0") != -1:
                stop_chronometer()
                try:
                    p.digital_write(0, 0)
                except:
                    pass
                title.config(text="ON AIR", font=("Avenir-Black", title_size), bg='#4D0000', fg='black')

        except socket.error:
            connected = False
            sock = socket.socket()
            print("Connexion perdue... reconnexion")
            while not connected:
                try:
                    sock.connect((ipaddress, port))
                    connected = True
                    print("Re-connexion réussie")
                except socket.error:
                    time.sleep(0.5)
    sock.close()

# init

try:
    p.init()
except:
    pass

root = Tk()

# récupère les informations de l'écran pour mettre à niveau

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
screen_resolution = str(screen_width) + 'x' + str(screen_height)

#initialisation des variables écran 1920x1080

initial_screen = 1920
title_size = int(172 * screen_width / initial_screen)
chrono_size = int(142 * screen_width / initial_screen)
canvas_size = int(500 * screen_width / initial_screen)
clock_size = int(60 * screen_width / initial_screen)
width = int(515 * screen_width / initial_screen)

#initialisation des variables générales

ipaddress = '192.168.1.86'
port = 65432
rayon = width / 2
process = 0
connected = True

#création de l'interface tkinter

root.title("On Air interface")
root.geometry(screen_resolution)
root.config(background='#000000000')
root.attributes("-fullscreen", True)

#création du ONAIR

title = Label(root, text="ON AIR", font=("Avenir-Black", title_size), bg='#4D0000', fg='black')
title.place(relx=0.5, rely=0.12, anchor=CENTER)

#création du canvas

C = Canvas(root, bg="black", height=canvas_size, width=canvas_size, highlightthickness=0)

#création du chrono

chrono = Label(root, fg='white', bg='black', font=("Avenir-Black", chrono_size))
chrono['text'] = "00:00:00"

#création des threads

th1 = threading.Thread(target=onair, daemon=True)
th2 = threading.Thread(target=trigo, daemon=True)
th3 = threading.Thread(target=piface_read, daemon=True)

#initialisation du client TCP

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#fonction trigo heures

for angle in range(0, 12):
    angle = ((angle * 30) * math.pi) / 180
    x = rayon + ((rayon * 0.90) * math.cos(angle))
    y = rayon + ((rayon * 0.90) * math.sin(angle))
    x1 = int(x) - 5
    y1 = int(y) - 5
    x2 = int(x) + 5
    y2 = int(y) + 5
    C.create_oval(x1, y1, x2, y2, fill='#0003FF')
    C.place(relx=0.5, rely=0.5, anchor=CENTER)

#création de la première seconde

#C.create_oval(145, 25, 155, 35, fill='#FFAA00', tags="first")

#création de l'heure

hour = Label(root, text="",fg='#0003FF', bg='black', font=("ds-digital", clock_size))
hour.place(relx=0.5, rely=0.5, anchor=CENTER)

#th3.start()
th1.start()
th2.start()

root.mainloop()
