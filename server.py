
import socket
import threading

HOST = "0.0.0.0"
PORT = 8443

clients = {}
clients_lock = threading.Lock()


def broadcast(message):
    """Broadcast a message to all connected clients."""

    with clients_lock:
        recipients = list(clients.keys())

    for client in recipients:
        try:
            client.sendall(message.encode("utf-8"))
        except OSError:
            disconnect(client)


def disconnect(client):
    """Remove a client from the server."""

    with clients_lock:
        username = clients.pop(client, None)

    try:
        client.close()
    except OSError:
        pass

    if username:
        print(f"[-] {username} disconnected")
        broadcast(f"[SERVER] {username} left the chat\n")


def handle_client(client, address):
    """Handle an individual client connection."""

    reader = client.makefile("r", encoding="utf-8")

    try:
        username = reader.readline().strip()

        if not username:
            return

        with clients_lock:
            clients[client] = username

        print(f"[+] {username} connected from {address}")

        broadcast(f"[SERVER] {username} joined the chat\n")

        while True:
            message = reader.readline()

            if not message:
                break

            message = message.strip()

            if not message:
                continue

            if message == "/quit":
                break

            print(f"[{username}] {message}")

            broadcast(f"[{username}] {message}\n")

    except (OSError, UnicodeError):
        pass

    finally:
        reader.close()
        disconnect(client)


def start_server():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[SERVER] Listening on {HOST}:{PORT}")

    try:
        while True:
            client, address = server.accept()

            threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()
