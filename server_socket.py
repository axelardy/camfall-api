from server_script.socket_logic import show_client, server_socket,flask_server
import threading

if __name__ == "__main__":
	flask_thread = threading.Thread(target=flask_server)
	flask_thread.start()
	while True:

		client_socket,addr = server_socket.accept()
		thread = threading.Thread(target=show_client, args=(addr,client_socket))
		thread.start()
		print("TOTAL CLIENTS ",threading.active_count() - 1)
	