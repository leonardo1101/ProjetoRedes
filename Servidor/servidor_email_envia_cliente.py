#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json
import time


while True:
    print("This prints once a minute.")
    time.sleep(60)

	cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	with open('emailServer.json') as json_file:  
	    data = json.load(json_file)
	    for e in data ['emails']:

	    	email_cli = e['emailFrom']
			email_dest = e['emailTO']
			ip_email_server_rec = e['emailServerIP']
			mailServer = e['serverName']
			body = e['emailBody']
			body += '.'

			cli_socket.connect((ip_email_server_cli, 2525))

			sentence = 'HELO ' + mailServer

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

print('<conexao fechada>')