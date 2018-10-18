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

FLAGS_FIN = 1
FLAGS_SYN = 2
FLAGS_RST = 4
FLAGS_ACK = 16


end = '127.0.0.1'
port_servidor = 7080
port_cliente = 7500

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
    return struct.pack('!HHIIHHHH', src_port, dst_port, seq_n ,ack_no, (5<<12)|FLAGS_ACK|flag,1024, 0, 0)

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
    
    
    if port_remt == port_servidor :
        if port_dest != port_cliente:
            return
        
        if (flags & FLAGS_SYN) == FLAGS_SYN:
            print('%s:%d -> %s:%d  (seq=%d) Segmento SYN reconhecido' % (end_remt,port_remt,end_dest,port_dest,seq_n))
            complete_ack = create_synack(port_cliente,port_servidor,ack_n + 1,seq_n + 1, 0)
            a = create_checksum(complete_ack,end,end)
            fd.sendto(a,(end,port_cliente))
            return "SYN recebido"
        
            #fd.sendto(create_checksum(create_synack(port_remt, port_dest, seq_n + 1, ack_n + 1 ,0),end_remt, end_dest),(end_remt,port_remt))
        
        if (flags & FLAGS_FIN) == FLAGS_FIN:
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

fd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
estabelecer_conexao(fd)
encerrar_conexao(fd)
    
    

#loop = asyncio.get_event_loop()
#loop.add_reader(fd, raw_recv, fd)
#loop.run_forever()
    
    
    
    
