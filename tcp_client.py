import socket


sample_target = ("ingenious.framer.ai")  # replace with a specific host
sample_port = 80     # probably want to leave this in when targeting a web server, or use an sslhandler/wrapper

my_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET indicates a standard IPv4 is in use; SOCK_STREAM indicated a TCP client

my_client.connect((sample_target, sample_port)) # .connect function imported from socket to connect to the server

my_client.send(b"GET / HTTP/1.1\r\nHost: evil.corp\r\n\r\n") #sending data, specifically a GET request to grab information about the sample_target server

response = my_client.recv(4096) #receiving data

print(response.decode())

my_client.close()
