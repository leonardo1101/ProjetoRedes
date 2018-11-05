#!/usr/bin/python3
#
# Antes de usar, execute o seguinte comando para evitar que o Linux feche
# as conexões TCP abertas por este programa:
#
# sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP
# 


import asyncio
import socket
import os
import sys
import queue
import struct

FLAGS_FIN = 1
FLAGS_SYN = 2
FLAGS_RST = 4
FLAGS_ACK = 16


end = '127.0.0.1'
port_servidor = 7080
port_cliente = 7500

dados = 32 * b"Who are you ?"
tamanho = 16

contador = 0

comecaEnviarPacote = False

connectionNumber = (end,port_cliente,end,port_servidor)

class Conexao:
    def __init__(self, id_conexao):
        self.id_conexao = id_conexao
        self.seq_no = 0
        self.ack_no = 0
        
    def setSeq(self,seq):
        self.seq_no = seq
    
    def setACK(self,ack):
        self.ack_no = ack

conexao = Conexao(connectionNumber)


def addr2str(addr):
    return '%d.%d.%d.%d' % tuple(int(x) for x in addr)

def str2addr(addr):
    return bytes(int(x) for x in addr.split('.'))

def set_checksum(segmento):
    checksum = 0
    for j in range(0, len(segmento), 2):
        x, = struct.unpack('!H',segmento[j:j+2])
        checksum += x
        while checksum > 0xffff:
            checksum = (checksum & 0xffff) + 1

    #Como é um servidor basta apenas negar
    checksum = (~checksum) & 0xffff
    
    return checksum

def create_synack(src_port, dst_port,seq_n, ack_no, flag):
    return struct.pack('!HHIIHHHH', src_port, dst_port, seq_n ,ack_no, (5<<12)|flag,1024, 0, 0)

def create_checksum(segmento, end_remt, end_dest):
    addr = str2addr(end_remt) + str2addr(end_dest) + struct.pack('!HH', 0x0006, len(segmento))
    seg = bytearray(segmento)
    seg[16:18] = b'\x00\x00'
    seg[16:18] = struct.pack('!H', set_checksum(addr + segmento))
    return bytes(seg)

def extract_addrs_segment(packet):
    version = packet[0] >> 4
    size_header = packet[0] & 0xf
    assert version == 4
    end_remt = addr2str(packet[12:16])
    end_dest = addr2str(packet[16:20])
    segmento = packet[ 4 * size_header:]
    return  end_remt,end_dest,segmento

def raw_recv(fd):
    pacote = fd.recv(12000)
    end_remt, end_dest, segmento = extract_addrs_segment(pacote)
    port_remt, port_dest, seq_n, ack_n, flags, window_size, checksum, urg_ptr = struct.unpack('!HHIIHHHH', segmento[:20])
    flags = flags & 511
    
    if port_remt == port_servidor :
        if port_dest != port_cliente:
            return
        
        if flags == FLAGS_SYN:
            print('%s:%d -> %s:%d  (seq=%d) Segmento SYN reconhecido' % (end_remt,port_remt,end_dest,port_dest,seq_n))
            conexao.setSeq(ack_n)
            conexao.setACK(seq_n + 1)
            return "SYN recebido"
        elif flags == FLAGS_FIN:
            print('%s:%d -> %s:%d  (seq=%d) Segmento FIN reconhecido' % (end_remt,port_remt,end_dest,port_dest,seq_n))
            return "FIN recebido"
           
def estabelecer_conexao(fd):
    syn = create_synack(port_cliente,port_servidor,0,0, FLAGS_SYN)
    a = create_checksum(syn,end,end)
    fd.sendto(a,(end,port_cliente))
    recebido = ""
    while(recebido != "SYN recebido" ):
        recebido = raw_recv(fd)
    print("Conexao Estabelecida")
    
 
def encerrar_conexao(fd):
    fin = create_synack(port_cliente,port_servidor,0,0, FLAGS_FIN)
    a = create_checksum(fin,end,end)
    fd.sendto(a,(end,port_cliente))
    recebido = ""
    while(recebido != "FIN recebido" ):
        recebido = raw_recv(fd)
    #Esperar30 segundos
    print("Conexao Encerrada")

def enviar_pacote(data):
    
    send_base = conexao.seq_no
    fd.settimeout(0.1)
    pacotes_enviados = 0
    contador = 0
    while(data != b""):
        contador = contador + 1
                        
        if(contador > 50):
            contador = 0
            conexao.seq_no = send_base
            pacotes_enviados = 0

        
        if(pacotes_enviados < 5):
            payload = data[conexao.seq_no:conexao.seq_no+tamanho]
            segment = struct.pack('!HHIIHHHH', port_cliente , port_servidor, conexao.seq_no,
                                conexao.ack_no, (5<<12)|FLAGS_ACK,
                                1024, 0, 0) + payload
            
            print('%s:%d -> %s:%d  (seq=%d) Segmento ACK enviado' % (end,port_cliente,end,port_servidor,conexao.seq_no))
            conexao.seq_no = (conexao.seq_no + len(payload)) & 0xffffffff
            segment = create_checksum(segment, end, end)
            fd.sendto(segment,(end,port_cliente))
            pacotes_enviados = pacotes_enviados + 1
            
        try:
            pacote = fd.recv(12000)
            end_remt, end_dest, segmento = extract_addrs_segment(pacote)
            port_remt, port_dest, seq_n, ack_n, flags, window_size, checksum, urg_ptr = struct.unpack('!HHIIHHHH', segmento[:20])
            flags = flags & 511
            if port_remt == port_servidor and port_dest == port_cliente :
                if flags == FLAGS_ACK :
                    print('%s:%d -> %s:%d  (ack=%d) Segmento ACK chegou' % (end,port_cliente,end,port_servidor,ack_n-1))
                    if(ack_n > send_base):
                        print('Ack %d e send_base %d' %(ack_n,send_base))
                        if(ack_n == send_base + tamanho):
                            send_base =ack_n
                            pacotes_enviados= pacotes_enviados - 1
                        else:
                            conexao.seq_no = send_base  
                    
                    
        except:
            pass

    
        
        
        


fd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

estabelecer_conexao(fd)
enviar_pacote(dados)
encerrar_conexao(fd)
    
    

#loop = asyncio.get_event_loop()
#loop.add_reader(fd, raw_recv, fd)
#loop.run_forever()
    
    
    
    
