# 实现了即使客户端发送时文件时地址随机，但仍然发送回客户端的固定地址

import socket
import os
import threading
import struct

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('192.168.11.200', 9002))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        os.sys.exit(1)
    print('等待连接...')

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()

def deal_data(conn, addr):
    print('客户端地址为： {0}'.format(addr)) 
    try:
        # 读取文件名长度信息
        file_name_length = conn.recv(2)
        file_name_length = int.from_bytes(file_name_length, byteorder='big')

        # 读取文件名
        file_name = conn.recv(file_name_length).decode('utf-8')
        print('数据名为 {0}'.format(file_name))

        # 读取文件大小信息
        file_size_bytes = conn.recv(8)
        file_size = int.from_bytes(file_size_bytes, byteorder='big')
        print('数据大小为 {0}'.format(file_size))

        recvd_size = 0
        file_path = 'D:/recept/' + file_name
        with open(file_path, 'wb') as fp:
            print('开始接收客户端数据...')
            while recvd_size < file_size:
                data = conn.recv(1024)
                if not data:
                    break
                recvd_size += len(data)
                fp.write(data)
            print('客户端数据接收完成...')

        # 数据接收完毕后，将数据发送回客户端到固定IP和端口
        send_file_to_specific_client(file_path)

    except Exception as e:
        print("处理过程中出现异常: ", e)
    finally:
        conn.close()
        print('连接已关闭。')

def send_file_to_specific_client(file_path):
    client_ip = '192.168.11.250'
    client_port = 9999
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((client_ip, client_port))

        with open(file_path, 'rb') as fp:
            file_name = os.path.basename(file_path)
            file_size = os.stat(file_path).st_size

            file_name_encoded = file_name.encode('utf-8')
            s.send(len(file_name_encoded).to_bytes(2, byteorder='big'))
            s.send(file_name_encoded)
            s.send(file_size.to_bytes(8, byteorder='big'))

            print('开始向客户端发送数据...')
            while True:
                data = fp.read(1024)
                if not data:
                    break
                s.send(data)
            print('数据传输完成：{0}'.format(file_name))
    except Exception as e:
        print("在发送文件过程中发生错误: ", e)
    finally:
        s.close()
        print('文件发送操作完成。')

if __name__ == '__main__':
    socket_service()
