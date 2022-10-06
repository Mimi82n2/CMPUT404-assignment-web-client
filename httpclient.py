#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Return the response code
        # (second item in the first line)
        return int(data.split('\n')[0].split(' ')[1])

    def get_headers(self,data):
        # Ignore the content
        headers = data.split('\r\n\r\n')[0]
        headers = headers.split('\r\n')
        #Remove first status code line
        del headers[0]
        head_dic = {}
        for header in headers:
            key,val = header.split(":",1)
            head_dic[key] = val
        return head_dic

    def get_body(self, data):
        # Return the body
        # Body is separated by two \r\n
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Retrieve info from the url and connect
        port = 80
        path = '/'
        urlparts = urllib.parse.urlparse(url)
        host = urlparts.hostname
        if urlparts.port:
            port = urlparts.port
        if urlparts.path:
            path = urlparts.path
        if path[-1] != '/':
            path+='/'
        if not host:
            host,path = path.split('/',1)
        self.connect(host,port)

        # Create a request to be sent to the server
        request = (
            "GET {} HTTP/1.1\r\n"
            "Host: {}:{}\r\n"
            "Connection: close\r\n"
            "Accept: */*\r\n\r\n"
        ).format(path, host, port)
        self.sendall(request)

        # Get response from server and return it
        recv = self.recvall(self.socket)
        code = self.get_code(recv)
        body = self.get_body(recv)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Retrieve info from the url and connect
        port = 80
        path = '/'
        urlparts = urllib.parse.urlparse(url)
        host = urlparts.hostname
        if urlparts.port:
            port = urlparts.port
        if urlparts.path:
            path = urlparts.path
        if path[-1] != '/':
            path+='/'
        if not host:
            host,path = path.split('/',1)
        self.connect(host,port)

        # Prepare and send the request
        content = ""
        contentType = ""
        contentLength = 0
        if args:
            content = urllib.parse.urlencode(args)
            contentType = "Content-Type: application/x-www-form-urlencoded\r\n"
            contentLength = len(content)
        request = (
            "POST {} HTTP/1.1\r\n"
            "Host: {}:{}\r\n"
            "Connection: close\r\n"
            "Accept: */*\r\n"
            "{}"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}"
        ).format(path, host, port, contentType, contentLength, content)
        self.sendall(request)

        # Retrieve the response and return its code and body
        recv = self.recvall(self.socket)
        code = self.get_code(recv)
        body = self.get_body(recv)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)

    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
