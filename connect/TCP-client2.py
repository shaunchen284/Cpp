# 与上一版本的差别为，修改了文件信息发送的方式：去除了使用 struct 的方法，改为发送具体的字节长度和大小信息
import socket
import os
import sys

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

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect(('192.168.11.200', 9002))  # 修改为服务端的IP地址和端口号
        s.connect(('127.0.0.1', 8001))  # 修改为服务端的IP地址和端口号
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
