#!/usr/bin/python3
# -- encoding: utf-8 --
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8000))
s.listen(1)


#dados = b''
while True:
    cli, addr = s.accept()

    dados = cli.recv(1)
    while not b'#cambio'  in dados:
    	dados += cli.recv(1)
    print(dados[:-7])
    cli.send('hello world#cambio')