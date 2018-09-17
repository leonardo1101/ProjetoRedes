#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json

# Arquivo referente ao Servidor de e-mail que esperará uma conexão com o Cliente para enviar seus e-mails

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 1100))
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
        
       # Comando para listar todos os e-mails
       
       elif(message == 'list all'):
            with open('emailServe.json') as json_file:  
                data = json.load(json_file)
                for e in data ['emails']:
                    print(data)
                    email_cli = e['emailFrom']
                    email_dest = e['emailTO']
                    body = e['emailBody']
                    men = '355 Sending email, ending with $'
                    cli.send(men.encode())
                    
                    message = cli.recv(1024).decode()
                    vectorMessage = message.split(' ')
                    print(vectorMessage)
                    if(email_dest == user and vectorMessage[0] == '200'):
                        email = "Email from " + email_cli + " : \n" + body + '$'
                        print(email)
                        cli.send(email.encode())
                    
                fim = "099 There are no emails"
                cli.send(fim.encode())
                break
            break    
    cli.close()
    



print('<conexao fechada>') 
