import socket
import os
import time

#自定义一个文件打开函数，上传文件时调用该函数打开client中的文件 
def file_deal(file_name):
    try:
        files = open(file_name, 'rb')
        mes = files.read()
    except:
        print("the file is not existing!")#文件不存在则返回错误提示
    else:
        files.close()
        return mes

address = ('192.168.159.135', 5555)
#创建一个socket以连接服务器 socket=socket.socket(family,type)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#使用socket的connect方法连接服务器 socket.connect((host,port))
s.connect(address)  
#客户和服务器通过send和recv方法通信
print('The connection has been established,if you want to transport strings to the server,please input "string";if you want to transport files to the server,please input "file" ;if you want to stop the connection,please input "exit"')
mode = input("input the mode ： ").strip() #字符传输和文件传输模式选择
s.sendall(mode.encode())#将模式选择报告给服务器，以便服务器创建一个新线程做好传输准备
#字符串传输
if mode=="string":
    print("strings transfer mode:")
    while True:   #支持多次输入，直到输入exit结束对话
        inp = input("Please enter the information you want to send ： ").strip()
        if not inp:     # 防止输入空信息，导致异常退出
            continue
        s.sendall(inp.encode())   #将信息传给服务器

        if inp == "exit":   # 如果输入的是‘exit’，表示断开连接
            server_reply = s.recv(1024).decode()   #接收服务器发送来的“Byebye”消息
            print("server_reply:%s"% server_reply)
            print("Communication End!")
            break
        server_reply = s.recv(1024).decode()   #接收服务器发来的"消息已收到"
        print("server_reply:%s"% server_reply) #输出
    s.close()    #跳出循环后关闭连接
#文件传输
elif mode=="file":
    print("file transfer mode:")
    while True:
        print('if you want to upload files,please input "upload";if you want to download files,please input "download"')
        mode_choose = input("download or upload ： ").strip()   #选择上传还是下载文件
        s.sendall(mode_choose.encode())    #将该选择报告给服务器，以便服务器做好传输准备
        if mode_choose == "exit":   # 如果输入的是‘exit’，表示断开连接
            time.sleep(1)
            server_reply = s.recv(1024).decode()    #接收服务器发送来的“Byebye”消息
            print("server_reply:%s"% server_reply)
            print("Communication End!")
            break
        #文件下载
        elif mode_choose=="download":
            buffersize=int(input('请输入一次能够接收的数据量'))   #可以自定义一次接收的字节数
            file_name = input("请输入要下载的文件路径及文件名:")  #输入要下载的服务器中的文件路径及文件名
            s.sendall(file_name.encode())       #将文件路径及文件名发送给服务器
            name=file_name.split("/")[-1]       #在文件路径中提取出文件名
            message=s.recv(1024).decode()       #服务器收到文件名后进行文件检查，若文件状态正常可以发送，则返回正常信息；若文件打开出错，则返回"the file not exist!"   
            print(message)
            if message=="the file not exist!":#若出错，进行下一次文件传输
                print("error!")
                continue
            else:     #若文件状态正常，则开始传输过程
                filesize = int(s.recv(1024))   #返回文件的大小
                print ("filesize:")
                print (filesize)
                path=input("请输入你要保存该文件的路径")   #自定义文件保存路径
                try:
                    new_file=open(path,'wb')    #新建一个文件并打开
                except:
                    print("file path error!")
                    continue
                restsize = filesize   #传输之前剩余字节数等于文件全部字节数
                print ("正在接收文件... ")
                while True:
                    if restsize > buffersize:   #若剩余字节数大于一次接收字节数，则接收量为buffersize
                        filedata = s.recv(buffersize)
                    else:
                        filedata = s.recv(restsize)   #若剩余字节数小于一次接收字节数，则接收量为restsize
                    if not filedata: break       #如果读出的内容为空，则跳出循环，这里和下面“if restsize == 0”语句实际意义是一样的，多加一个判断确保程序不会出现死循环
                    new_file.write(filedata)    #将读入的字符写入文件
                    restsize = restsize-len(filedata)    #更新剩余字节数
                    if restsize == 0:         #剩余字节数为0时跳出循环
                        break
                s.sendall('From client:Thank you,I have received your file!'.encode())#接收完毕后给服务器发送一个确认消息
                print("file has downloaded:%s"% name)
                new_file.close()#关闭文件
        #文件上传
        elif mode_choose=="upload":
            file_name = input("请输入要上传的文件路径及文件名:")
            s.sendall(file_name.encode())   #将文件名发送给服务器
            mes = file_deal(file_name)       #在client上找到并打开指定文件     
            if mes:    #如果文件存在且能够正常打开
                s.sendall('From client:wait a moment,file is sending now'.encode())   #告诉服务器文件可以上传，发一个确认消息
                time.sleep(1)
                s.sendall(str(os.path.getsize(file_name)).encode())   #发送文件大小
                time.sleep(1)
                s.send(mes)     #发送文件
                print('the file is already sent!')
                message=s.recv(1024).decode()     #接收服务器返回的文件收到信息并输出
                print(message)
            else:
                s.send('error!'.encode()) #如果不能正常上传，向服务器报告错误信息
        else:
            print("输入错误，请重试！")
    s.close()#关闭连接
#结束对话
elif mode=="exit":
    print("Communication End!")
    s.close()
#输入错误
else:
    print("输入错误，请重试！")
    s.close()