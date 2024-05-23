import socket
import os
import sys
import time

def send_file(s, filepath):
    try:
        s.connect(('127.0.0.1', 8001))  # 连接服务端
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    
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
        # 添加延时等待，等待一段时间再关闭连接
        # 否则还没发送完就关闭连接了
        time.sleep(1) # 根据实际情况调整等待时间

    # 发送完文件后关闭连接
    s.close()

def socket_client():
    while True:
        filepath = input("请输入文件路径：\n")
        if filepath == 'exit':
            break
        if os.path.isfile(filepath):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_file(s, filepath)

if __name__ == '__main__':
    socket_client()
