#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cli_socket.connect((ip_email_server_cli, 110))


email_cli = input('Enter with your user: ')

sentence = 'telnet mailServer'

cli_socket.send(sentence.encode())
response = cli_socket.recv(512).decode()
print(response)


if response[0:3] == '+OK':
	sentence = 'user ' + email_cli
	cli_socket.send(sentence.encode())
	response = cli_socket.recv(512).decode()
	print(response)

	if response == '+OK user successfully logged on':
		sentence = 'list all'
		cli_socket.send(sentence.encode())
		response = cli_socket.recv(512).decode()
		print(response)

		while response[0:3] == "355" :
			resp = "200 the client is ready to receive the email."
			cli_socket.send(resp.encode())

			while not (b'$' in emailBody):
        		emailBody += cli.recv(64)

        	print(emailBody)
        	response = cli_socket.recv(512).decode()
			print(response)
			
		print(response)

		

cli_socket.close()
