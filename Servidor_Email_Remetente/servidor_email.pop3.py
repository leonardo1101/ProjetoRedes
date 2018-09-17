#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 110))
s.listen(1)

while True:
    cli, addr = s.accept()

	user = ''

    while True:
        message = cli.recv(1024).decode()
        print(message)
        vectorMessage = message.split(' ')

        if(vectorMessage[0] == 'telnet'):
        	ready = '+OK POP3 server ready'
        	cli.send(ready.encode())

        elif(vectorMessage[0] == 'user'):
        	user= vectorMessage[1]
        	emailFrom = '+OK user successfully logged on'	
        	cli.send(emailFrom.encode())

        elif(message == 'list all'):
        	with open('emailServer.json') as json_file:  
		    data = json.load(json_file)
		    for e in data ['emails']:
		    	email_cli = e['emailFrom']
				email_dest = e['emailTO']
				body = e['emailBody']

				cli.send('355 Sending email, ending with $')

				message = cli.recv(1024).decode()
				vectorMessage = message.split(' ')
				
				if(email_dest == user and vectorMessage[1] == '200'):
					email = "Email from " + email_cli + " : \n" + body + '$'
					cli.send(email)

			fim = "099 There are no emails"
	cli.close()
    



print('<conexao fechada>') 
