import socket

def get_address():
    return socket.gethostbyname(socket.gethostname()).strip()