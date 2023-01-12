import socket
import cv2
import pickle
import struct
from cv2 import aruco
import numpy as np
marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
param_markers = aruco.DetectorParameters_create()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
print("host name", host_name)
host_ip = socket.gethostbyname(host_name)
print('HOST IP:', host_ip)
port = 9999
socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen(5)
print("LISTENING AT:", socket_address)
while True:
    client_socket, addr = server_socket.accept()
    print('GOT CONNECTION FROM:', addr)
    if client_socket:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            ret, frame = vid.read()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            marker_corners, marker_IDs, reject = aruco.detectMarkers(
            gray_frame, marker_dict, parameters=param_markers
            )
            if marker_corners:
                for ids, corners in zip(marker_IDs, marker_corners):
                    cv2.polylines(
                        frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA
                    )
                    corners = corners.reshape(4, 2)
                    corners = corners.astype(int)
                    top_right = corners[0].ravel()
                    top_left = corners[1].ravel()
                    bottom_right = corners[2].ravel()
                    bottom_left = corners[3].ravel()
                    cv2.putText(
                        frame,
                        f"id: {ids[0]}",
                        top_right,
                        cv2.FONT_HERSHEY_PLAIN,
                        1.3,
                        (200, 100, 0),
                        2,
                        cv2.LINE_AA,
                    )
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a)) + a
            client_socket.sendall(message)
            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                 client_socket.close()
