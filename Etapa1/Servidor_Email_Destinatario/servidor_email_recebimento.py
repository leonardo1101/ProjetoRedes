#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 2525))
s.listen(1)

# Arquivo referente ao Servidor de e-mail que receberá o e-mail do Cliente ou de outro Servido de e-mail

while True:
    cli, addr = s.accept()
    mailServer = ''
    email = ''
    emailRC = ''
    emailServerIP = ''
    emailBody = b''

    while True:
        message = cli.recv(1024).decode()

        print(message)
        vectorMessage = message.split(' ')

        if(vectorMessage[0] == 'HELO'):
        	mailServer = vectorMessage[1]
        	hello = '250 Hello ' + vectorMessage[1] + ', pleased to meet you'
        	cli.send(hello.encode())

        elif(vectorMessage[0] == 'MAIL'):
        	email= vectorMessage[2]
        	email = email.replace('<','')
        	email = email.replace('>','')
        	emailFrom = '250 '+ email +' ... Sender ok'	
        	cli.send(emailFrom.encode())

        elif(vectorMessage[0] == 'RCPT'):
        	emailRC= vectorMessage[2]
        	emailRC = emailRC.replace('<','')
        	emailRC = emailRC.replace('>','')
        	emailTo = '250 '+ emailRC +' ... Recipient ok'	
        	cli.send(emailTo.encode())

        elif(vectorMessage[0] == 'ESIP'):
        	emailServerIP= vectorMessage[1]
        	messageEmailServer = '250 '+ emailServerIP +' ... IP of the mail server saved'	
        	cli.send(messageEmailServer.encode())

        elif(vectorMessage[0] == 'DATA'):
        	response = '354 Enter mail, end with ”.” on a line by itself'
        	cli.send(response.encode())
        	while not (b'.' in emailBody):
        		emailBody += cli.recv(64)
        	confirmData = '250 Message accepted for delivery'
        	cli.send(confirmData.encode())

        # Escreve em um arquivo json as informações referentes ao e-mail.
        
        else:
            closeConnection = '221 ufscar.edu closing connection'
            cli.send(closeConnection.encode())
            data = {}
            data ['emails'] = []
            data['emails'].append({  
			    'serverName': mailServer,
			    'emailFrom': email,
			    'emailTO': emailRC,
			    'emailServerIP' : emailServerIP ,
			    'emailBody' : emailBody.decode()
			})
            with open('emailServerD.json', 'w') as outfile:
                json.dump(data, outfile)
            break
    cli.close()
    



print('<conexao fechada>')
