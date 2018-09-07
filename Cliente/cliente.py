#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli_socket.connect(('192.168.15.11', 2525))

email_cli = input('Client\'s email: ')
email_dest = input('Recipient\'s Email: ')
ip_server_cli = input('Client\'s server IP: ')
ip_server_dest = input('Recipient\'s server IP: ')


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
		print("entrei")
		sentence = 'RCPT TO: <' + email_dest + '>'
		cli_socket.send(sentence.encode())
		response = cli_socket.recv(512).decode()
		print(response)

		if response[0:3] == '250':
			sentence = 'DATA'
			cli_socket.send(sentence.encode())
			response = cli_socket.recv(512).decode()
			print(response)

			if response[0:3] == '354':
				sentence = ''
				data = input()
				while data != '.':
					sentence += data
					data = input()
				cli_socket.send(sentence.encode())
				response = cli_socket.recv(512).decode()
				print(response)

				if response[0:3] == '250':
					sentence = 'QUIT'
					cli_socket.send(sentence.encode())
					response = cli_socket.recv(512).decode()
					print(response)

cli_socket.close()
