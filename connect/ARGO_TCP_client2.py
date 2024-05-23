import socket
import os
import sys
import time
class Socket_Client():
    
    def socket_client(self, filepath, ip_address, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip_address, port))
            print("Connected to server.")
        except socket.error as msg:
            print(msg)
            sys.exit(1)

        try:
            if os.path.isfile(filepath):  # 判断是否为文件
                # 发送文件名长度
                file_name = os.path.basename(filepath)
                file_name_length = len(file_name)
                s.send(file_name_length.to_bytes(2, byteorder='big'))
                
                # 发送文件名
                file_name_encoded = file_name.encode('utf-8')
                s.send(file_name_encoded)
                
                # 发送文件大小
                file_size = os.path.getsize(filepath)
                s.send(file_size.to_bytes(8, byteorder='big'))

                # 发送文件数据
                with open(filepath, 'rb') as fp:
                    while True:
                        data = fp.read(1024)
                        if not data:
                            print('{0} 数据传输完成...'.format(file_name))
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
