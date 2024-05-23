from ARGO_TCP_client import Socket_Client
filepath = r'C:\Users\lenovo\Desktop\319485\test\39-319485-001.txt'
addr = ('127.0.0.1', 8001)
s = Socket_Client(filepath=filepath,addr=addr)