import socket
import os
import sys
import struct
import time
class Socket_Client():
    
    def socket_client(self,filepath, ip_address, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip_address, port))
            print("Connected to server.")
        except socket.error as msg:
            print(msg)
            sys.exit(1)


        try:
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
                    # 添加延时等待，等待一段时间再关闭连接
                    # 否则还没发送完就关闭连接了
                    time.sleep(1) # 所以这个值可以变大，以免报错
        except Exception as e:
            print("发送文件时出现错误:", e)
        finally:
            s.close()  # 关闭连接
if __name__ == '__main__':
    filepath = r'C:\Users\lenovo\Desktop\319485\39-319485-011.txt'
    ip_address = '127.0.0.1'
    port = 8001
    s = Socket_Client()
    s.socket_client(filepath, ip_address, port)
