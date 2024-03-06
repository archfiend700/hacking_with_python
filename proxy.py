print("""\
....................................................................................................
....................................:-===--:........................................................
..................................:============:....................................................
.................................:-===============-.................................................
.................................:-==========+=======:..........:...................................
.................................::====================---::..:.....................................
.................................:.-=========--=----------..-=++-...................................
..................................:.=====-------=-------===:.=**....................................
...................................:.====--------=-===-------::=....................................
....................................-.-==------==--=----------=-....................................
.....................................-.--===------------------+-:...................................
......................................-:-=------------=-------=-::..................................
.......................................:-:-----------------------::.................................
.........................................=----------------=------:::................................
..........................................:=----++++=---------:---:::...............................
...........................................%==---++===+-=--+-:-=--=:::..............................
..........................................:=:*+=---=======-::::--=-=:::.............................
..........................................::.+%#*=-----------==-=====-:.............................
..........................................*#%=**##*+=------::::--:=-::::............................
..........................................=*%##*###*=++=-----:--=-::::::............................
............................................+****##+...:++=-----::::::-.............................
............................................+=*****+.......-+*+===-===..............................
............................................-=+****++...............................................
............................................===****++...............................................
..........................................-----=****+...............................................
......................................:---=======***+++-............................................
......................................:==========+**#+++++=.........................................
.......................................=++*########*********+.......................................
.......................................-+++==--::::.................................................

""")



import sys
import socket
import threading

#Boolean short circuit method for representing hex values alongside character strings (hexa) in a neat table output
#this allows us to see real time communication that passes through the proxy
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, lenght=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), lenght):
        word = str(src[i:i+lenght])

        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = lenght*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

# buffer for receiving and accumulating data from the socket
def receive_from(connection):
    buffer = b""
    connection.settimeout(5) #increase if necessary, this proxy is quite aggressive
    try:
        while True:
            data = connection.recv(4096) #loop to continuously read data into the buffer with a simple if statement to
                                            # break in case no data is received(timeout or closed session)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer  #buffer returns a string to the caller (remote or local)

#modifying our packets
def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer

#Proxy handler
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))   #We start off with a connection to a remote host

    if receive_first:  #Initiation check and data request if boolean returns true
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer) #Dumping the contents of a packet and handing the output to the next function

    remote_buffer = response_handler(remote_buffer) #Sending the received buffer to our local client
    if len(remote_buffer):
        print("[<==]Sending %d bytes to localhost" % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:  #While true/data is received, the proxy logic keeps looping to read data, process it and send it
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost" % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>]Sent to remote")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==]Received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==]Sent to localhost")


        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.") #when there's no more data to process, all sockets close
            break


def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem to bind on: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        sys.exit(0)


    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        #Prints out local connection info
        line = "> Received incoming from %s:%d" % (addr[0], addr[1])
        print(line)
        #starting a communication thread to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host,
            remote_port, receive_first))
        proxy_thread.start()


        def main():
            if len(sys.argv[1:]) != 5:
                print("Usage example: ./earz.py [localhost] [localport] [remotehost] [remoteport] True")
                sys.exit(0)
            local_host = sys.argv[1]
            local_port = int(sys.argv[2])



        remote_host = sys.argv[3]
        remote_port = int(sys.argv[4])

        receive_first = sys.argv[5]

        if "True" in receive_first:
            receive_first = True
        else:
            receive_first = False

        server_loop(local_host, local_port,
                    remote_host, remote_port, receive_first)

        if __name__ == '__main__':
            main()


