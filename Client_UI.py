from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
import socket
import threading
import logging
logging.basicConfig(filename="client_log.log", level=logging.INFO)

HEADER = 64 
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_CMD = "!QUIT"
SEND_CMD = "!SEND"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)


class ClientGui(QMainWindow):
    def __init__(self):
        logging.info("Loading UI")
        super(ClientGui,self).__init__()
        uic.loadUi('client.ui',self)
        self.show()
        self.Disconnect_button.hide()
        self.connected = False
        self.run_client()

    
    def connect_client(self):
        try:
            logging.info("Trying to connect client...")
            self.my_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.my_client.connect(ADDR)
            self.connected = True
            mb = QMessageBox()
            mb.setWindowTitle('Connected!')
            mb.setText('You succesfully connected to the server!')
            mb.setStandardButtons(QMessageBox.StandardButton.Ok)
            res = mb.exec()
            new_thread = threading.Thread(target=self.receive_message,args=())
            new_thread.start()
            self.Connect_button.hide()
            self.Disconnect_button.show()
            self.show()
        except Exception as e:
            logging.error("Error: {}".format(e))
            mb = QMessageBox()
            mb.setWindowTitle('Error!')
            mb.setText('Unable to connect to server: {}'.format(e))
            mb.setStandardButtons(QMessageBox.StandardButton.Ok)
            res = mb.exec()

    def check_for_command(self):
        logging.info("Checking if command is acceptable")
        if self.message[0:5] == SEND_CMD:
            self.message = self.message[6:len(self.message)]
        elif self.message[0:5] == DISCONNECT_CMD:
            self.message = self.message[0:5]
            self.disconnect_requested = True
            logging.info("Requesting disconnect from server")
        elif self.message[0] == "!":
            return False
        else:
            self.message = self.message
        return True
    
    def send_message(self):
        self.disconnect_requested = False
        if self.connected:
            try:
                if self.check_for_command():
                    msg = self.message
                    msg = msg.encode(FORMAT) ##encode to byte
                    message_length = len(msg) ##find # of bytes
                    send_length = str(message_length).encode(FORMAT)
                    send_length += b' ' * (HEADER-len(send_length)) ##pad to make it 64
                    self.my_client.send(send_length)
                    self.my_client.send(msg)
                    if self.disconnect_requested:
                            mb = QMessageBox()
                            mb.setText('You succesfully disconnected from the server!')
                            mb.setStandardButtons(QMessageBox.StandardButton.Ok)
                            res = mb.exec()
                            self.Connect_button.show()
                            self.Disconnect_button.hide()
                            self.show()
                            self.connected = False
                            logging.info("Client disconnected from server")
                    else:
                        self.chat_messages_textEdit.append("Me: "+self.message)
                else:
                    logging.info("User put an invalid command")
                    mb = QMessageBox()
                    mb.setWindowTitle('Error!')
                    mb.setText('Invalid command!')
                    mb.setStandardButtons(QMessageBox.StandardButton.Ok)
                    res = mb.exec()
                    
            except Exception as e:
                mb = QMessageBox()
                mb.setWindowTitle('Error!')
                mb.setText('Unable to send message: {}'.format(e))
                mb.setStandardButtons(QMessageBox.StandardButton.Ok)
                res = mb.exec()
                logging.error("Client was unable to send a message: {}".format(e))
        else:
            mb = QMessageBox()
            mb.setWindowTitle('Error!')
            mb.setText('Not connected to the server!')
            # mb.setIcon(QMessageBox.Warning) # Warning, Critical, Information, Question
            mb.setStandardButtons(QMessageBox.StandardButton.Ok)
            res = mb.exec()
            logging.error("Client attempted to send message while disconnected")
            
        self.textEdit.clear()
            
    def disconnect_client(self):
        logging.info("Disconnecting client....")
        self.message = DISCONNECT_CMD
        self.send_message()


    def receive_message(self):
        while self.connected:
            length_of_message = self.my_client.recv(HEADER).decode(FORMAT)
            if length_of_message:
                logging.info("New message was received from the server")
                message = self.my_client.recv(int(length_of_message)).decode(FORMAT)
                self.chat_messages_textEdit.append(message)
                

    def new_message(self):
        logging.info("User is typing a message")
        self.message = self.textEdit.toPlainText()
        if len(self.message) > 0:
            if self.message[-1] == "\n" and not self.message.isspace():
                self.message = self.message[0:len(self.message)-1] ## get rid of whitespace
                self.send_message() ##send message when there's things written + enter is hit

    
    def run_client(self):
        logging.info("Running UI")
        self.Disconnect_button.clicked.connect(self.disconnect_client)
        self.Connect_button.clicked.connect(self.connect_client)
        self.message = ""
        self.chat_message = ""
        self.textEdit.textChanged.connect(self.new_message)
        self.SEND_button.clicked.connect(self.send_message)

            
    


app = QApplication([])
window = ClientGui()
app.exec()
