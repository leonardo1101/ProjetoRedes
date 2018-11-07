#!/usr/bin/python3
#
# Antes de usar, execute o seguinte comando para evitar que o Linux feche
# as conexões TCP abertas por este programa:
#
# sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP
# 

import asyncio
import socket
import struct
import signal
from contextlib import contextmanager
import time
import os

FLAGS_FIN = 1
FLAGS_SYN = 2
FLAGS_RST = 4
FLAGS_ACK = 16


end = '127.0.0.1'
port_servidor = 7080
port_cliente = 7500
InicialSeqNumber = 0
tamanho = 16


class Conexao:
    def __init__(self, id_conexao, seq_no, ack_no):
        self.id_conexao = id_conexao
        self.seq_no = seq_no
        self.ack_no = ack_no
        self.data = b""
        self.rcv_buffer = 1024
        self.lastByteRcvd = 0
        self.lastByteRead = 0
        
conexoes = {}

NextSeqNum = InicialSeqNumber
SendBase = InicialSeqNumber

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
    packet = fd.recv(12000)
    end_remt, end_dest, segmento = extract_addrs_segment(packet)
    port_remt, port_dest, seq_n, ack_n, flags, window_size, checksum, urg_ptr = struct.unpack('!HHIIHHHH', segmento[:20])
    
    if port_remt == port_cliente :

        flags = flags & 511
        seg_check = set_checksum(segmento)
        if port_dest != port_servidor:
            return
        
        connectionNumber = (end_remt,port_remt,end_dest,port_dest)
        
        if flags == FLAGS_SYN :
            
            
            conexao = Conexao(id_conexao=connectionNumber,seq_no = 0 , ack_no=seq_n + 1)
            conexoes[connectionNumber] = conexao
            
            
            print('%s:%d -> %s:%d  (seq=%d) Segmento SYN - conexão estabelecida' % (end_remt,port_remt,end_dest,port_dest,conexao.seq_no))
            
            fd.sendto(create_checksum(create_synack(port_servidor, port_cliente, conexao.seq_no, conexao.ack_no, FLAGS_SYN),end_remt, end_dest),(end_remt,port_remt))
            
        elif connectionNumber in conexoes:
            conexao = conexoes[connectionNumber]
            if flags == FLAGS_ACK : 
                if(seg_check+checksum & 0xffff and seq_n == conexao.ack_no ):
                    print('%s:%d -> %s:%d  (seq=%d) Segmento ACK recebido' % (end_remt,port_remt,end_dest,port_dest,seq_n))
                    conexao.data += segmento[4*(flags>>12):]
                    fd.sendto(create_checksum(create_synack(port_servidor, port_cliente, conexao.seq_no, seq_n + tamanho, FLAGS_ACK),end_remt, end_dest),(end_remt,port_remt))
                    conexao.ack_no+=tamanho
                    conexao.seq_no += 1
                
            elif flags == FLAGS_FIN:
                del conexoes[connectionNumber]
                print('%s:%d -> %s:%d  (seq=%d) Segmento FIN - conexão encerrada' % (end_remt,port_remt,end_dest,port_dest,seq_n))
                fd.sendto(create_checksum(create_synack(port_servidor, port_cliente, 0, seq_n + 1,FLAGS_FIN),end_remt, end_dest),(end_remt,port_remt))
        
        else:
            return


fd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
loop = asyncio.get_event_loop()
loop.add_reader(fd, raw_recv, fd)
loop.run_forever()
    
    
    
    
