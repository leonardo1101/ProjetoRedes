#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

email_cli = input('Client\'s email: ')
email_dest = input('Recipient\'s Email: ')
ip_email_server_cli = input('Client\'s  email server IP: ')
ip_email_server_rec = input('Recipient\'s email server IP: ')

sentence = ''
body = input('Write the email body:')
while data != '.':
	body += data
	data = input()
body += '.'

cli_socket.connect((ip_email_server_cli, 2525))

sentence = 'HELO renata.ufscar'

cli_socket.send(sentence.encode())
response = cli_socket.recv(512).decode()
print(response)
if response[0:3] == '250':
	sentence = 'MAIL FROM: <' + email_cli + '>'
	cli_socket.send(sentence.encode())
	response = cli_socket.recv(512).decode()
	print(response)

	if response[0:3] == '250':
		sentence = 'RCPT TO: <' + email_dest + '>'
		cli_socket.send(sentence.encode())
		response = cli_socket.recv(512).decode()
		print(response)

		if response[0:3] == '250':
			sentence = 'ESIP ' + ip_email_server_rec 
			cli_socket.send(sentence.encode())
			response = cli_socket.recv(512).decode()
			print(response)

			if response[0:3] == '250':
				sentence = 'DATA'
				cli_socket.send(sentence.encode())
				response = cli_socket.recv(512).decode()
				print(response)

				if response[0:3] == '354':
					cli_socket.send(body.encode())
					response = cli_socket.recv(512).decode()
					print(response)

					if response[0:3] == '250':
						sentence = 'QUIT'
						cli_socket.send(sentence.encode())
						response = cli_socket.recv(512).decode()
						print(response)

cli_socket.close()
