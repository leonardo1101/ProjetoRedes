#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket

# Arquivo referente ao Cliente que pegará os e-mails de seu servidor de e-mail

cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cli_socket.connect(('127.0.0.1', 1100))


email_cli = input('Enter with your user: ')

sentence = 'telnet mailServer'

cli_socket.send(sentence.encode())
response = cli_socket.recv(512).decode()
print(response)
emailBody = ''


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
        print("\n\n")
        while not ('$' in emailBody):
            emailBody += cli_socket.recv(64).decode()
        
        print(emailBody)
        response = cli_socket.recv(512).decode()
        emailBody = ''
    print("\n\n")
    print(response)

		

cli_socket.close()
