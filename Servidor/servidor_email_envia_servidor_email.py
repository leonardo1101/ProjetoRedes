#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import socket
import json
import time

# Arquivo referente ao Servidor de e-mail que enviará o e-mail para outro Servidor de e-mail

while True:
    print("Servidor enviando.")
    time.sleep(60)
    cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Lê o arquivo Json e envia as informações para outro Servidor de e-mail
    
    with open('emailServer.json') as json_file:  
        data = json.load(json_file)
        for e in data ['emails']:
            try:
                email_cli = e['emailFrom']
                email_dest = e['emailTO']
                ip_email_server_rec = e['emailServerIP']
                mailServer = e['serverName']
                body = e['emailBody']
                
                del e['serverName']
                del e['emailFrom']
                del e['emailTO']
                del e['emailServerIP']
                del e['emailBody']
                body += '.'
                
                cli_socket.connect((ip_email_server_rec, 2525))
                
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
                with open('emailServer.json', 'w') as outfile:
                    json.dump(data, outfile)
                break
            except:
                print("Não há emails disponiveis.")
            
print('<conexao fechada>')
