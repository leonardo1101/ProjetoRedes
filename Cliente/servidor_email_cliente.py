#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 2525))
s.listen(1)


while True:
    cli, addr = s.accept()

    while True:
        message = b''
        while not (b'\n' in message):
            pedaco = cli.recv(1024)
            if pedaco == b'':
                break
            message += pedaco

        print(message)
        vectorMessage = message.split(" ")

        if(vectorMessage[0] == "HELO"):
        	hello = "250 Hello " + vectorMessage[1] + ", pleased to meet you"
        	cli.send(hello)
        elif(vectorMessage[0] == "MAIL"):
        	email= vectorMessage[2]
        	email = email.replace("<","")
        	email = email.replace(">","")
        	emailFrom = "250 "+ emailFrom +" ... Sender ok"	
        	cli.send(emailFrom)
        elif(vectorMessage[0] == "RCPT"):
        	email= vectorMessage[2]
        	email = email.replace("<","")
        	email = email.replace(">","")
        	emailFrom = "250 "+ emailFrom +" ... Recipient ok"	
        	cli.send(emailFrom)
        elif(vectorMessage[0] == "DATA"):
        	response = "354 Enter mail, end with ”.” on a line by itself"
        	cli.send(response)
        	emailBody = ""
        	while not (b'.' in emailBody):
        		emailBody += cli.recv(64)
        	print(emailBody)
        	confirmData = " 250 Message accepted for delivery"
        else:
        	closeConnection = " 221 hamburger.edu closing connection"
        	cli.send(closeConnection)

    cli.close()



print('<conexao fechada>')