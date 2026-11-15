
import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443


def receive_messages(client):
    """Receive messages from the server."""

    reader = client.makefile("r", encoding="utf-8")

    try:
        while True:
            message = reader.readline()

            if not message:
                print("[CLIENT] Disconnected from server")
                break

            print(message.strip())

    except OSError:
        print("[CLIENT] Connection closed")


def start_client():
    username = input("Username: ").strip()

    if not username or "\n" in username:
        print("Invalid username")
        return

    try:
        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.connect((SERVER_HOST, SERVER_PORT))

        print(f"[CLIENT] Connected to {SERVER_HOST}:{SERVER_PORT}")

        client.sendall(f"{username}\n".encode("utf-8"))

        threading.Thread(
            target=receive_messages,
            args=(client,),
            daemon=True
        ).start()

        print("Type /quit to leave the chatroom.")

        while True:
            message = input()

            client.sendall(f"{message}\n".encode("utf-8"))

            if message == "/quit":
                break

        client.close()

    except OSError as error:
        print(f"[CONNECTION ERROR] {error}")


if __name__ == "__main__":
    start_client()
