# -*- coding: utf-8 -*-
import socket
import asyncio
import struct
import threading

conexoes = {}

ETH_P_IP = 0x0800

# Coloque aqui o endereço de destino para onde você quer mandar o ping
dest_addr = '0.0.0.0'

def delete(num):
    global conexoes
    if num in conexoes.keys:
        del conexoes[num]

def send_ping(send_fd):
    print('enviando ping')
    # Exemplo de pacote ping (ICMP echo request) com payload grande
    msg = bytearray(b"\x08\x00\x00\x00" + 5000*b"uhul"+b"not")
    msg[2:4] = struct.pack('!H', calc_checksum(msg))
    send_fd.sendto(msg, (dest_addr, 0))

    asyncio.get_event_loop().call_later(1, send_ping, send_fd)


def separa_cabecalho_payload(binario):
  if not int(binario[0]>>4) == 4:
      return None, None
  ihl = binario[0] & 0xf0
  return binario[:ihl*4], binario[ihl*4:]

def calc_checksum(segment):
    if len(segment) % 2 == 1:
        # se for ímpar, faz padding à direita
        segment += b'\x00'
    checksum = 0
    for i in range(0, len(segment), 2):
        x, = struct.unpack('!H', segment[i:i+2])
        checksum += x
        while checksum > 0xffff:
            checksum = (checksum & 0xffff) + 1
    checksum = ~checksum
    return checksum & 0xffff


def desmonta_cabecalho(cabecalho):
    versao_ihl, \
    dscp_ecn, \
    total_lenght, \
    identification, \
    flags_fragment, \
    time_to_live, \
    protocol,  \
    checksum, \
    source, \
    destination = struct.unpack('!BBHHHBBHII', cabecalho[:20])
    return versao_ihl, dscp_ecn, total_lenght, identification, flags_fragment, time_to_live, \
    protocol, checksum, source, destination


def raw_recv(recv_fd):
    packet = recv_fd.recv(70000)
    cabecalho, payload = separa_cabecalho_payload(packet)
    if cabecalho == None:
        pass

    #print(payload)
    _, _, _, identification, flags_fragment, _, \
    _, _, source, destination = desmonta_cabecalho(cabecalho)
    fragment = flags_fragment & 0x1fff
    flags = flags_fragment >> 13

    tripla = (source, destination, identification)

    if not tripla in conexoes.keys():
        conexoes[tripla] = [set(), b"", None, 0, threading.Timer(60, delete, [tripla])]
        #start timer    
        conexoes[tripla][4].start()

    if fragment in conexoes[tripla][0]:
        pass

    conexoes[tripla][0].add(fragment)
    conexoes[tripla][3] += len(payload)    

    if len(conexoes[tripla][1]) > fragment:
        conexoes[tripla][1] += b'\xff' * (fragment-len(conexoes[tripla][0])) + payload
    else:
        #metodo 1
        #for i in range(len(payload)):
        #     conexoes[tripla][1][fragment+i] = payload[i]
        
        #metodo2
        conexoes[tripla][1] = conexoes[tripla][1][:fragment] + payload + conexoes[tripla][1][:fragment+len(payload)]

    

    if flags & 1 == 0:
        conexoes[tripla][2] = fragment+len(payload)
    
    if conexoes[tripla][3] == conexoes[tripla][2]:
        print(conexoes[tripla][1])
        # para o timer
        conexoes[tripla][4].cancel()
        del conexoes[tripla]
    


#if _name_ == '_main_':
    ## Ver http://man7.org/linux/man-pages/man7/raw.7.html
    #send_fd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    ## Para receber existem duas abordagens. A primeira é a da etapa anterior
    ## do trabalho, de colocar socket.IPPROTO_TCP, socket.IPPROTO_UDP ou
    ## socket.IPPROTO_ICMP. Assim ele filtra só datagramas IP que contenham um
    ## segmento TCP, UDP ou mensagem ICMP, respectivamente, e permite que esses
    ## datagramas sejam recebidos. No entanto, essa abordagem faz com que o
    ## próprio sistema operacional realize boa parte do trabalho da camada IP,
    ## como remontar datagramas fragmentados. Para que essa questão fique a
    ## cargo do nosso programa, é necessário uma outra abordagem: usar um socket
    ## de camada de enlace, porém pedir para que as informações de camada de
    ## enlace não sejam apresentadas a nós, como abaixo. Esse socket também
    ## poderia ser usado para enviar pacotes, mas somente se eles forem quadros,
    ## ou seja, se incluírem cabeçalhos da camada de enlace.
    ## Ver http://man7.org/linux/man-pages/man7/packet.7.html
    #recv_fd = socket.socket(socket.AF_PACKET, socket.SOCK_DGRAM, socket.htons(ETH_P_IP))

    #loop = asyncio.get_event_loop()
    #loop.add_reader(recv_fd, raw_recv, recv_fd)
    #asyncio.get_event_loop().call_later(1, send_ping, send_fd)
    #loop.run_forever()
