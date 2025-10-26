from socket import *
import cv2

S = socket()
S.bind(('0.0.0.0', 1101))
S.listen()
print("等待连接...")

s, addr = S.accept()
print("连接来自:", addr)

print("功能选择：")
print("1.远程监控")

choice = input("请输入功能编号：")
s.send(choice.encode())

if choice == '1':
    while True:
        size = int(s.recv(1024).decode())
        s.send('ok'.encode())

        cursize = 0
        with open('monitor.png', 'wb') as f:
            while cursize < size:
                data = s.recv(2048)
                f.write(data)
                cursize += len(data)
        
        cv2.namedWindow('monitor')
        image = cv2.imread('save.png')
        cv2.imshow('monitor', image)
        cv2.waitKey(1)

        s.send('ok'.encode())