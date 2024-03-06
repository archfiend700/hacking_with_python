import socket

sample_host = "127.0.0.1" #obviously change this
sample_port = 699 #and change that

my_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #changing the socket type to the Datagram protocol

my_client.sendto(b"RAAAAAH",(sample_host,sample_port)) #we skipped the connect part of the TCP session, since UDP is a connectionless protocol

data, addr = my_client.recvfrom(4096)

print(data.decode())
my_client.close()