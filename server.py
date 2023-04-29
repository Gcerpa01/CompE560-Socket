import socket
import threading
import logging
logging.basicConfig(filename="server_log.log", level=logging.INFO)

HEADER = 64 
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER,PORT)
FORMAT = 'utf-8'
DISCONNECT_CMD = "!QUIT"

logging.info("Creating socket....")
myServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
myServer.bind(ADDRESS) ##address connected to socket


port_dictionary = {myServer:"RUNNING"}
ip_dictionary = {myServer:ADDRESS}

def send_info_message(msg):
    logging.info("preparing information of the message")
    message = msg.encode(FORMAT)
    message_length = len(message)
    send_info = str(message_length).encode(FORMAT)
    send_info += b' ' * (HEADER-len(send_info))
    return send_info

###Server sends new incoming messages to clients ###
def update_clients(address,connection):
    for client in port_dictionary.keys(): ##iterate through clients to send messages to
        if client != myServer and client != connection: ##not the client or the server, send it the message
            if port_dictionary.get(connection) == "!QUIT":
                message =  "*** (IP:{},Port:{}) has disconnected ***".format(str(address[0]),str(address[1]))
            else:
                message = "(IP:{},Port:{}): {}".format(str(address[0]),str(address[1]),port_dictionary.get(connection))
            message_length = send_info_message(message)
            try:
                logging.info("Server sent the message \"{}\" to all clients that are not: {}".format(message,client))
                client.send(message_length)
                client.send(message.encode(FORMAT))
            except socket.error as e:
                logging.error("There was an erorr sending a message to client: {}, error: {}".format(client,e))
                print("There was an erorr sending a message to client: {}, error: {}".format(client,e))


##Receive Messages and act appropriately##
def handle_client(address,connection):
    connected = True
    while connected:
        length_of_message = connection.recv(HEADER).decode(FORMAT)
        if length_of_message:
            logging.info("Server received a message from: {}".format(connection))
            message = connection.recv(int(length_of_message)).decode(FORMAT)
            if message == DISCONNECT_CMD:
                connected = False
            print("(IP:{}, Port:{}): {}".format(address[0],address[1],message))
            port_dictionary.update({connection:message})
            update_clients(address,connection)
            

    print("*** (IP:{}, Port:{}) disconnected from the server ***".format(address[0],address[1]))
    del port_dictionary[connection]
    del ip_dictionary[connection]
    connection.close()

###Inform others of there being a new connection###
def new_connection(address,connection):
    port_dictionary.update({connection:""})
    ip_dictionary.update({connection:address})
    message = "*** (IP:{}, Port:{}) has joined the server ***".format(address[0],address[1])
    print(message)
    logging.info(message)
    message_length = send_info_message(message)
    for client in port_dictionary.keys(): ##iterate through clients to send messages to
        if client != myServer and client != connection: ##not the client or the server, send it the message
            try:
                logging.info("Server notified clients that client: {} has joined".format(connection))
                client.send(message_length)
                client.send(message.encode(FORMAT))
            except socket.error as e:
                print("There was an erorr sending a message to client: {}, error: {}".format(client,e))
                logging.error("There was an erorr sending a message to client: {}, error: {}".format(client,e))


def start():
    myServer.listen()
    print("*** Server is running through IP: {} ***".format(SERVER))
    while True:
        try:
            connection,address = myServer.accept() ## wait for connection to store
            new_connection(address,connection)
            new_thread = threading.Thread(target=handle_client,args=(address,connection))
            new_thread.start()
        except socket.error as e:
            logging.error("There was an error accepting the connection: {}".format(e))
            print("There was an error accepting the connection: {}".format(e))
            

    

print("*** Starting Server ***")
start()