#!coding=utf-8
import threading
import socket
import struct
import os
from csv_processor import CSVProcessor
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('192.168.11.250', 9999))
        s.listen(10) # 参数 10 指定了套接字的最大等待连接数
    except socket.error as msg:
        print(msg)
        os.sys.exit(1)
    print('等待连接...')

    while 1:
        # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        # target=deal_data：这表示要在新线程中运行的函数
        t.start()

def deal_data(conn, addr):
    print('客户端地址为： {0}'.format(addr)) 
    conn.send('hi, Welcome to the server!'.encode('utf-8'))
    # 向客户端发送一条欢迎消息 
    # send() 方法只接受字节流作为参数，所以在发送之前，需要将字符串编码成字节流。
    # 因此，使用了 .encode('utf-8') 来将字符串编码成 UTF-8 字节流
    try:
        while True:
            fileinfo_size = struct.calcsize('128sl')
            buf = conn.recv(fileinfo_size)
            # 从连接对象 conn 接收一段指定大小的数据，用来解析客户端发送的文件信息
            if buf: # 接收到了文件信息，buf 不为空
                filename, filesize = struct.unpack('128sl', buf)
                fn = filename.strip(b'\00').decode()
                # strip() 方法去除文件名中的空字节（\00）。
                # decode()：将处理后的字节流解码成字符串形式，默认使用 UTF-8 编码
                print('数据名为 {0}, 数据大小为 {1}'.format(fn, filesize))
                recvd_size = 0
                with open('C:/Users/lenovo/Desktop/任务帧数据接收/' + fn, 'wb') as fp: # 创建名为fn的文件，将数据data分批写入
                    print('开始接收客户端数据...')
                    while recvd_size < filesize:
                        if filesize - recvd_size > 1024:
                            data = conn.recv(1024)
                        else:
                            data = conn.recv(filesize - recvd_size)
                        recvd_size += len(data) # 追踪已接收到的总数据量
                        fp.write(data) # 写入数据
                    print('客户端数据接收完成...')

                # 处理csv生成nc
                File_path = 'C:/Users/lenovo/Desktop/任务帧数据接收/' + fn
                TIME,df = CSVProcessor.process_csv(file_path=File_path)
                new_path = 'C:/Users/lenovo/Desktop/nc_data'
                nc_path = CSVProcessor.nc_generate(df,TIME,new_path=new_path)
                print('csv格式转换为nc格式')
                   
                # 文件接收完成后，将文件发送回客户端
                with open(nc_path, 'rb') as fp: # 这里fn表示接收到的原来的文件 
                    file_path = nc_path
                    fhead = struct.pack('128sl', os.path.basename(file_path).encode('utf-8'), os.stat(file_path).st_size)
                    # fhead 中包含了文件名和文件大小的信息
                    conn.send(fhead) # 发送打包好的文件头信息 fhead
                    print('向客户端发送数据...')
                    while True:
                        data = fp.read(1024) # 从打开的文件中读取最多 1024 字节的数据
                        if not data:
                            print('{0} 数据传输完成...'.format(os.path.basename(file_path)))
                            break # 如果读取到的数据为空，表示文件已经读取完毕，循环会终止
                        conn.send(data)
            else:
                # 如果接收到的buf为空，说明客户端已关闭连接
                break
    except Exception as e:
        print("处理过程中出现异常: ", e)
    finally:
        conn.close()
        print('连接已关闭。')
        # 循环没有结束条件,一直运行直到客户端主动断开连接或发生错误
    # 在 try 块中捕获了可能发生的异常，并在 finally 块中关闭连接对象 conn。
    # 这确保了无论发生了什么错误，连接都会被正确地关闭


socket_service()
