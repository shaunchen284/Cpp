## 解释代码的文件，不外用

#!coding=utf-8
import threading
import socket
import struct
import os
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 创建了一个套接字对象 s socket.AF_INET 表示使用 IPv4 地址，
        # socket.SOCK_STREAM 表示使用 TCP 协议来传输数据
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设置套接字的选项，以便重用本地地址（IP 和端口）。这通常用于开发阶段，
        # 以确保即使之前的连接未正常关闭，也可以重新启动服务器而不会遇到 "地址已在使用" 的错误
        
        # 绑定端口为9001
        # 同一网络的不同主机
        # s.bind(('192.168.11.250', 9001))
        # 同一网络同一主机
        s.bind(('127.0.0.1', 8001))
        # 127.0.0.1 表示只接受来自同一台机器的连接。
        # 端口号 9001 是随意选择的，可以更改为其他未被占用的端口
        # 设置监听数
        s.listen(1) # 参数 10 指定了套接字的最大等待连接数
        # 参数 10 表示最多可以有 10 个客户端的连接请求在内部队列中等待服务器来处理（接受或拒绝）。
        # 如果第 11 个客户端尝试连接，而队列已满，则该客户端的连接请求可能会被拒绝或者超时。
    except socket.error as msg:
        # 捕获 socket.error 异常的语句。如果在创建套接字、设置套接字选项、
        # 绑定到地址或监听端口时出现任何问题，都会抛出 socket.error
        print(msg)
        os.sys.exit(1)
        # 使程序在遇到异常时终止执行,os.sys.exit(1) 调用用于停止程序运行，
        # 并且向操作系统返回一个退出代码（在这里是 1），表明程序是由于错误而非正常结束的。
        # 退出代码 1 通常用于指示程序因错误而终止
    print('等待连接...')

    while 1:
        
        # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
        conn, addr = s.accept()
        print('客户端地址为： {0}'.format(addr)) 
        conn.send('hi, Welcome to the server!'.encode('utf-8'))
        # 每当接受到一个新的连接，
        #它会从 accept() 方法返回一个新的套接字对象 conn 用于和客户端通信，
        # 以及客户端的地址 addr。
        # 接收数据
        t = threading.Thread(target=deal_data, args=(conn, addr))
        # target=deal_data：这表示要在新线程中运行的函数
        t.start()
        # 调用了 start() 方法，线程就会开始执行 target 参数指定的函数，
        # 也就是 deal_data 函数



def deal_data(conn, addr):
    # print('客户端地址为： {0}'.format(addr)) 
    # {0} 表示使用参数列表中的第一个参数，这里只有addr一个参数，可以去掉0
    # conn.send('hi, Welcome to the server!'.encode('utf-8'))
    # 向客户端发送一条欢迎消息 
    # send() 方法只接受字节流作为参数，所以在发送之前，需要将字符串编码成字节流。
    # 因此，使用了 .encode('utf-8') 来将字符串编码成 UTF-8 字节流
    try:
        while True:
            # 循环会一直执行，直到客户端断开连接或发生异常
            # 接收文件信息
            fileinfo_size = struct.calcsize('128sl')
            # struct.calcsize是计算给定格式字符串所需的字节数的函数
            # 128s' 表示一个长度为 128 的字符串,l' 表示一个 long 类型的整数
            # 128s 占用 128 个字节，l 占用一个 long 类型的整数所需的字节数（通常为 4 个字节）。
            # 因此，'128sl' 总共占用 128 + 4 = 132 个字节。
            # struct.calcsize('128sl') 的返回值是 132，表示给定格式字符串所需的字节数为 132 字节
            # 用于指定接收文件信息的缓冲区的大小，以确保能够完整地接收文件信息
            buf = conn.recv(fileinfo_size)
            # conn.recv() 方法会一直等待直到数据到达
            # 从连接对象 conn 接收一段指定大小的数据，用来解析客户端发送的文件信息
            if buf: # 接收到了文件信息，buf 不为空
                filename, filesize = struct.unpack('128sl', buf)
                # 解析接收到的文件信息 最大长度为 128 字节
                # 得到文件名 filename 和文件大小 filesize
                fn = filename.strip(b'\00').decode()
                # strip() 方法去除文件名中的空字节（\00）。在网络传输中，
                # 有时会出现空字节来填充字符串的末尾，因此需要将其去除
                # decode()：将处理后的字节流解码成字符串形式，默认使用 UTF-8 编码
                print('数据名为 {0}, 数据大小为 {1}'.format(fn, filesize))
                recvd_size = 0
                # 记录已经接收到的文件数据的大小。初始值为 0，表示还未接收到任何数据。
                with open('C:/Users/lenovo/Desktop/nc_data/' + fn, 'wb') as fp: # 创建名为fn的文件，将数据data分批写入
                    # fn 是文件名 'wb'以二进制写入
                    print('开始接收客户端数据...')
                    while recvd_size < filesize:
                    # 持续接收客户端发送的数据，直到接收到的数据大小等于文件大小 filesize
                        if filesize - recvd_size > 1024:
                            data = conn.recv(1024)
                            # 如果剩余待接收数据大小大于 1024 字节，则每次接收 1024 字节的数据；
                            # 否则，只接收剩余大小的数据
                            # 接收到的数据通过 conn.recv() 方法从连接对象 conn 中读取
                        else:
                            data = conn.recv(filesize - recvd_size)
                        if not data: 
                        ### 正式因为缺少这个判断，才导致有bug，连接会不正常的关闭
                            break
                        recvd_size += len(data) # 追踪已接收到的总数据量
                        fp.write(data) # 写入数据
                        # fp 是通过 open() 函数返回的文件对象，它提供了写入数据的方法
                    print('客户端数据接收完成...')
                # 接收文件数据并将其写入到服务器端的文件中。
                # 在这里，服务器根据接收到的文件大小循环接收数据，并将数据写入到文件中


                # # 文件接收完成后，将文件发送回客户端
                # with open('C:/Users/lenovo/Desktop/nc_data/' + fn, 'rb') as fp: # 这里fn表示接收到的原来的文件
                #     file_path = os.path.join('./', fn).replace('\\', '/')
                #     file_path = 'C:/Users/lenovo/Desktop/nc_data/' + fn
                #     # 将当前目录 './' 与文件名 fn 连接起来，形成完整的文件路径
                #     # .replace('\\', '/') 将路径中的反斜杠 \ 替换为正斜杠 /，以确保路径格式的统一性
                #     # 反斜杠 \ 替换为正斜杠 /,反斜杠 \ 在Python中是转义字符
                #     fhead = struct.pack('128sl', os.path.basename(file_path).encode('utf-8'), os.stat(file_path).st_size)
                #     # 将文件信息打包成一个二进制字符串 fhead。'128sl' 是格式字符串，指定了两个字段的格式：
                #     # 前者是文件名编码为 UTF-8 字节流，并取文件路径的最后一个组件（即文件名）
                #     # 后者是获取文件大小，返回的是一个 long 类型的整数
                #     # 这样，fhead 中就包含了文件名和文件大小的信息
                #     conn.send(fhead) # 发送打包好的文件头信息 fhead
                #     print('向客户端发送数据...')
                #     while True:
                #         data = fp.read(1024) # 从打开的文件中读取最多 1024 字节的数据
                #         if not data:
                #             print('{0} 数据传输完成...'.format(os.path.basename(file_path)))
                #             break # 如果读取到的数据为空，表示文件已经读取完毕，循环会终止
                #         conn.send(data)
            else:
                # 如果接收到的buf为空，说明客户端已关闭连接
                break
    except Exception as e:
        print("处理过程中出现异常: ", e)
    finally:
        conn.close()
        print('连接已关闭。')
        print('监听中……')
        # 循环没有结束条件,一直运行直到客户端主动断开连接或发生错误
    # 在 try 块中捕获了可能发生的异常，并在 finally 块中关闭连接对象 conn。
    # 这确保了无论发生了什么错误，连接都会被正确地关闭


socket_service()

# 下面代码基本一样，只是输出位置不一样
# import threading
# import socket
# import struct
# import os

# def socket_service():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind(('127.0.0.1', 8001))
#         s.listen(1)
#     except socket.error as msg:
#         print(msg)
#         os.sys.exit(1)

#     print('等待连接...')

#     while True:
#         conn, addr = s.accept()
#         print('客户端地址为： {0}'.format(addr)) 
#         conn.send('hi, Welcome to the server!'.encode('utf-8'))
        
#         t = threading.Thread(target=deal_data, args=(conn, addr))
#         t.start()

# def deal_data(conn, addr):
#     try:
#         while True:
#             fileinfo_size = struct.calcsize('128sl')
#             buf = conn.recv(fileinfo_size)
#             if buf:
#                 filename, filesize = struct.unpack('128sl', buf)
#                 fn = filename.strip(b'\00').decode()
#                 print('数据名为 {0}, 数据大小为 {1}'.format(fn, filesize))
#                 recvd_size = 0
#                 with open('C:/Users/lenovo/Desktop/nc_data/' + fn, 'wb') as fp:
#                     print('开始接收客户端数据...')
#                     while recvd_size < filesize:
#                         if filesize - recvd_size > 1024:
#                             data = conn.recv(1024)
#                         else:
#                             data = conn.recv(filesize - recvd_size)
#                         if not data:
#                             break
#                         recvd_size += len(data)
#                         fp.write(data)
#                     print('客户端数据接收完成...')
#             else:
#                 break
#     except Exception as e:
#         print("处理过程中出现异常: ", e)
#     finally:
#         conn.close()
#         print('连接已关闭。')

# socket_service()
