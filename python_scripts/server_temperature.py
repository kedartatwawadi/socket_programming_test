import socket
import threading

HEADER = 4
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        print(f"[{addr}] {msg}")

    conn.close()
    print(f"[{addr}] Connection Closed")


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}: {PORT}")
    while True:
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}", flush=True)
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print("[STARTING] server is starting...")
start()
