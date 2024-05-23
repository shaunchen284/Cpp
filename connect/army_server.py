import socket
import os
import threading

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.bind(('192.168.11.200', 9002))
        s.bind(('127.0.0.1', 8001))
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
    except Exception as e:
        print("处理过程中出现异常: ", e)
    finally:
        conn.close()
        print('连接已关闭。')

if __name__ == '__main__':
    socket_service()