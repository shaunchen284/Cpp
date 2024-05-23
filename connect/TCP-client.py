import socket
import os
import sys
import struct

def recv_file(conn, filepath, filesize):
    recvd_size = 0
    with open(filepath, 'wb') as fp:
        # 只有收到第二个文件时，第一个收到的文件才会写入内容，否则只有0kb大小
        # 因为没有使用with...格式，文件不能及时关闭
        while recvd_size < filesize:
            if filesize - recvd_size > 1024:
                data = conn.recv(1024)
            else:
                data = conn.recv(filesize - recvd_size)
            recvd_size += len(data)
            fp.write(data)

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 8001))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024))    # 打印连接成功消息

    while True:
        filepath = input("请输入文件路径：\n")  # 获取文件路径
        if filepath == 'exit':  # 如果输入exit，则退出循环
            break
        if os.path.isfile(filepath):  # 判断是否为文件
            # 发送文件名和文件大小信息
            filesize = os.path.getsize(filepath)
            fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), filesize)
            s.send(fhead)
            
            # 发送文件数据
            with open(filepath, 'rb') as fp:
                while True:
                    data = fp.read(1024)
                    if not data:
                        print('{0} 数据传输完成...'.format(os.path.basename(filepath)))
                        break
                    s.send(data)

            # 接收处理之后的数据
            print("开始接收服务端返回的数据...")
            # fileinfo_size = struct.calcsize('128sl')
            # buf = s.recv(fileinfo_size)

            # if buf:
            #     filename, filesize = struct.unpack('128sl', buf)
            #     fn = filename.strip(b'\00').decode()
            #     print('数据名为 {0}, 数据大小为 {1}'.format(fn, filesize))
            #     recv_file(s, './' + fn, filesize)
            #     print("文件接收完成。")

    s.close()  # 关闭连接

if __name__ == '__main__':
    socket_client()
