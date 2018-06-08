#coding:utf-8
import socket
import threading
import os
import time
#自定义文件打开函数，与client中相同
def file_deal(file_name):
    try:
        files = open(file_name, "rb")
        mes = files.read()
    except:
        print("the file is not existing!")
    else:
        files.close()
        return mes

#字符串传输通信函数
def link_handler_string(link, client):
    print("strings transfer mode:")       
    while True:
        client_data = link.recv(1024)    #接收client发送来的消息
        if client_data == "exit":     #如果client发来的消息是exit，则跳出循环，结束对话
            print("End communication with %s:%s ..." % (client[0], client[1]))
            time.sleep(10)   #设计时间延迟，模拟阻塞
            link.sendall('Byebye!')   #发送再见消息
            break
        print("Clients from  %s:%s  send a message to you:%s" % (client[0], client[1], client_data))    #输出client发送来的消息
        time.sleep(10)    #设计时间延迟，模拟阻塞
        link.sendall('The server has received your message')      #收到消息后回复一个确认消息
    link.close()

#文件传输通信函数
def link_handler_file(link, client):
    print("file transfer mode")
    while True:
        mode_choose=link.recv(1024)#接收client发来的指令，是退出，下载还是上传
        if mode_choose=="exit":    #如果client发来的消息是exit，则跳出循环，结束对话
            print("End communication with %s:%s ..." % (client[0], client[1]))
            link.sendall('Byebye!')
            break
        #文件下载
        elif mode_choose=="download":
            file_path = link.recv(1024)    #client传来文件名及路径
            print("Clients from  %s:%s  want to download file %s" % (client[0], client[1],file_path))
            mes = file_deal(file_path)     #尝试在server上打开文件
            file_name=file_path.split("/")[-1]        #在路径中用切片的方式获取文件名
            if mes:#若可以正常发送
                link.send('From server:wait a moment,file is sending now')   #告诉client文件可以发送
                time.sleep(1)
                link.send(str(os.path.getsize(file_path)))   #发送文件大小
                time.sleep(1)
                link.send(mes)   #发送文件
                print("the file is already sent!")
                message=link.recv(1024)  #接收client发来的“文件已收到”信息
                print(message)
            else:#若文件不存在，则将错误信息告诉client
                link.sendall("the file not exist!")               
                continue
        #文件上传
        elif mode_choose=="upload":
            file_path = link.recv(1024)  #接收文件路径及文件名
            file_name=file_path.split("/")[-1]  #在路径中用切片的方式获取文件名
            message=link.recv(1024)   #client告诉server文件能否正常发送，根据这个信息，决定执行下面if还是else中的操作
            print(message)
            if message=="error!":   #如果文件出错，则输出错误信息
                print("error!")
                continue
            else:   #若文件正常，则上传
                filesize = link.recv(1024)    #接收文件大小
                print("Clients from  %s:%s  send a file to you：%s" % (client[0], client[1], file_name))
                print ("filesize:")
                print (filesize)
                buffersize=int(raw_input("Please input the size of data that can be received at one time"))    #自定义一次接收的size
                file_new=raw_input('please input the file path that you want to put this file in:')    #自定义文件路径                                           
                try:
                    new_file=open(file_new,"wb")
                except:
                    print("file path error!")
                    continue
                restsize = int(filesize)      #该循环过程与client.py中下载文件的过程完全相同，只是文件传输的方向发生了改变。
                print ("receiving file... ")
                while True:
                    if restsize > buffersize:
                        filedata = link.recv(buffersize)
                    else:
                        filedata = link.recv(restsize)
                    if not filedata: break
                    new_file.write(filedata)
                    restsize = restsize-len(filedata)
                    if restsize == 0:
                        break
                link.sendall("The Server has already received your file")   #告诉client文件已经成功接收
                print("file  %s  has received"% file_name)
                new_file.close()    #关闭文件
    print("the above transfer ended")
    link.close()   #断开连接


address = ('192.168.159.135', 5555)
sk = socket.socket()   #创建socket对象 
sk.bind(address)       #将socket绑定（指派）到指定地址上，socket.bind(address)
sk.listen(5)           #绑定后，准备好套接字，以便接受连接请求。socket.listen(backlog)。backlog指定了最多连接数，至少为1，接到连接请求后，这些请求必须排队，如果队列已满，则拒绝请求。

print('start socket service,wait for clients to get connection...')

while True:   #循环处理client发出的请求
    conn, address = sk.accept()    #服务器套接字通过socket的accept方法等待客户请求一个连接
    print("The server starts to receive requests from %s:%s ...." % (address[0], address[1]))
    mode=conn.recv(1024)     #接收client发来的指令，是传输字符串、传输文件还是退出。并新建相应的线程完成通信。
    if mode=="string":
        print("string transporting")
        t = threading.Thread(target=link_handler_string, args=(conn, address))
        t.start()
    elif mode=="file":
        print("file transporting")
        t = threading.Thread(target=link_handler_file, args=(conn, address))
        t.start()
    elif mode=="exit":
        print("End communication with %s:%s ..." % (address[0], address[1]))
    else:
        print("input error!")
   
