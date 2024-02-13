from server_script.socket_logic import *
import threading

while True:
	client_socket,addr = server_socket.accept()
	thread = threading.Thread(target=show_client, args=(addr,client_socket))
	thread.start()
	print("TOTAL CLIENTS ",threading.active_count() - 1)
	