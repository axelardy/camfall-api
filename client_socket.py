
# Welcome to PyShine
# lets make the client code
# In this code client is sending video to server
import socket,cv2, pickle,struct
import pyshine as ps # pip install pyshine
import imutils # pip install imutils
import time

camera = True
if camera == True:
	vid = cv2.VideoCapture(0)
else:
	vid = cv2.VideoCapture('test.mp4')
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '169.254.83.107' # Here according to your server ip write the address

port = 9999
client_socket.connect((host_ip,port))

if client_socket: 
	start_time = time.time()
	total_bytes_sent = 0
	last_print_time = start_time

	while (vid.isOpened()):
		try:
			img, frame = vid.read()
			frame = imutils.resize(frame,width=720)

			# more efficient solution
			result, buffer = cv2.imencode('.jpg', frame)
			buffer = buffer.tobytes()
			message = struct.pack("Q",len(buffer))+buffer
		

			client_socket.sendall(message)
			total_bytes_sent += len(message)

			cv2.imshow(f"TO: {host_ip}",frame)
			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				client_socket.close()

			current_time = time.time()
			if current_time - last_print_time >= 1:
				total_time_elapsed = current_time - start_time
				average_bytes_per_second = total_bytes_sent / total_time_elapsed
				print(f"\rAverage bytes sent per second: {average_bytes_per_second*8/1000000} mbps", end='')
				last_print_time = current_time
		except:
			print('VIDEO FINISHED!')
			break

