#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.15.17', 8901))

sentence = 'helloooooooo todossssss'
sentence += '#cambio'

s.send(sentence.encode())

modified = s.recv(1)
while not b'#cambio' in modified:
	modified += s.recv(1)

modified = modified[:-7]
print(modified.decode())

s.close()