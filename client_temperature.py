import socket
import time

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
SERVER = "192.168.1.65"
ADDR = (SERVER, PORT)
ID = "0001"


def send(msg):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"Connected to {ADDR}")
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(f"Msg sent to {ADDR}")


def main():
    print("starting client...")
    for i in range(10):
        time.sleep(2)  # send msg every 2 seconds
        msg = f"{ID}, {i}, test"
        print(f"sending msg to server...{i}")
        send(msg)


main()
