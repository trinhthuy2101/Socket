import socket
import os
import mimetypes


htmlsource="./htmlsource/"
down_source="./download/"
PORT=8080
HOST =socket.gethostbyname(socket.gethostname())


#hanlde get-request from client 
def handle_get(request,client):
    #handle path to file
    file=request.split('\r\n')[0].split()[1]
    file=file.split('?')[0]
    path_to_html=htmlsource+'index.html'
    if file=='/files.html':
        path_to_html=htmlsource+'files.html'
    f=open(path_to_html, 'rb')
    #handle HTTP message and data 
    content=f.read()
    status_line='HTTP/1.1 200 OK\r\n'
    Content_Type=mimetypes.guess_type(path_to_html)[0]
    Headers='Connection: close\r\n'
    Headers+='Content-Length: %s\r\nContent-Type: %s\r\n\r\n'%(str(len(content)),Content_Type)
    response=(status_line+Headers).encode()+content
    #handle multimedia data
    if file!='/':
        file_format=file.split('/')[1].split('.')[1]
        if file_format!='html':
            response=handle_chunk(file,client)
    #return last response
    return response

#handle multimedia data (Chunked Transfer Encoding)
def handle_chunk(file,client):
    #handle path to multimedia file
    filename=file.split('/')[1].split('.')[0]
    file_format=file.split('/')[1].split('.')[1]
    path_to_file=down_source+filename+'.'+file_format
    #chunk__header
    Headers='HTTP/1.1 200 OK\r\n'   
    Content_Type=mimetypes.guess_type(path_to_file)[0]
    Headers+='Content_Type: %s\r\n'%(Content_Type)+'Transfer-Encoding: chunked\r\n\r\n'
    Headers=Headers.encode()
    client.send(Headers)
    #chunk
    chunk_size=1024
    f=open(path_to_file, 'rb')
    chunk_data=f.read(chunk_size)
    while chunk_data:
        chunk_dec=len(chunk_data)
        chunk_hex=hex(len(chunk_data)).replace("0x","")
        chunk=chunk_hex.encode()+b"""\r\n"""+chunk_data+b"""\r\n"""
        chunk=(chunk_hex+'\r\n').encode()+chunk_data+('\r\n').encode()
        client.send(chunk)
        chunk_data=f.read(chunk_size)
    response='0\r\n\r\n'
    response=response.encode()
    return response

#handle authentication then post info.html or 404.html
def handle_post(request):
    #handle path to htmlfile needed
   payload=request.split('\r\n\r\n')[1] #there's a blank line between headers and payload
   username=payload.split('&')[0].split('username=')[1]
   password=payload.split('&')[1].split('password=')[1] 
   if username=='admin'and password=='admin':
       path_to_html=htmlsource+'info.html'
   else:
       path_to_html=htmlsource +'404.html' 
    #handle HTTP message
   f=open(path_to_html, 'rb')
   content=f.read() 
   status_line='HTTP/1.1 301 Moved Permenantly\r\n'
   Content_Type=mimetypes.guess_type(path_to_html)[0]
   Headers='Content-Length: %s\r\nContent-Type: %s\r\n\r\n'%(str(len(content)),Content_Type)
   response=(status_line+Headers).encode()+content
   return response


#handle request from client
def handle_request(client):
    request=client.recv(1024)
    request=request.decode('utf-8')
    method=request.split('\r\n')[0].split()[0]
    if (method=='GET'):
        response=handle_get(request,client)
    else:
        response=handle_post(request)
    client.sendall(response)
    
    
#set up socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)
print('Host:',HOST)
print('Serving on port ',PORT)

#accept and start exchanging
while True:
    client, address=s.accept()
    print("Connected by: ",address)
    request=handle_request(client)
    client.close()
s.close()
