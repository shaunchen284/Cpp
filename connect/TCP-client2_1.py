# 增加了接受服务端文件的代码
import socket
import os
import sys

def recv_file(s):
    # 概括：接收文件名长度、文件名和文件大小，然后接收文件内容
    
    # 接收文件名长度
    file_name_length_bytes = s.recv(2)
    file_name_length = int.from_bytes(file_name_length_bytes, byteorder='big')
    
    # 接收文件名
    file_name_bytes = s.recv(file_name_length)
    file_name = file_name_bytes.decode('utf-8')
    
    # 接收文件大小
    file_size_bytes = s.recv(8)
    file_size = int.from_bytes(file_size_bytes, byteorder='big')
    
    print(f'数据名为 {file_name}, 数据大小为 {file_size}')
    
    # 接收文件内容
    recvd_size = 0
    with open(file_name, 'wb') as fp:
        while recvd_size < file_size:
            data = s.recv(1024)
            if not data:
                break
            recvd_size += len(data)
            fp.write(data)
        print("文件接收完成。")

def send_file(s, filepath):
    file_name = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    
    # 发送文件名长度
    file_name_encoded = file_name.encode('utf-8')
    s.send(len(file_name_encoded).to_bytes(2, byteorder='big'))
    
    # 发送文件名
    s.send(file_name_encoded)
    
    # 发送文件大小
    s.send(file_size.to_bytes(8, byteorder='big'))
    
    # 发送文件数据
    with open(filepath, 'rb') as fp:
        print('开始向服务器发送数据...')
        while True:
            data = fp.read(1024)
            if not data:
                print('{0} 数据传输完成...'.format(file_name))
                break
            s.send(data)
        print("开始接收服务端返回的数据...")
        recv_file(s)

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.11.200', 9002))  # 修改为服务端的IP地址和端口号
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    
    while True:
        filepath = input("请输入文件路径：\n")
        if filepath == 'exit':
            break
        if os.path.isfile(filepath):
            send_file(s, filepath)

    s.close()

if __name__ == '__main__':
    socket_client()
