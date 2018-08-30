from socket import *

nomeServidor = ''
porta = 
socketCliente = socket(AF_INET6,SOCK_STREAM)											#Cria o socket do cliente, 1º Param: IPv6 e 2º Param: SOCK_STREAM = TCP
socketCliente.connect((nomeServidor,porta))												#Cria a conexão TCP, realizando 3 handshake para estabelecer a conexão
sentenca = raw_input('Input lowercase sentence:')										#Pega a sentenca									
socketCliente.send(sentenca.encode())													#Manda a sentenca atraves do socket para a conexão TCP
setencaModificada = socketCliente.recv(1024)											#Espera o SO voltar para o processo, passando os pacotes do buffer, no maximo 2014
print('From server '+nomeServidor+ ': '+ setencaModificada.decode())					#Decodifica a sentenca modificada e exibe na tela
socketCliente.close()																	#Fecha a conexão TCP entre o cliente e servidor