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

    def __init__(self):
        self.port = 80

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #Status code should be the integer following HTTP/1.1.
        return int(data.split("\r\n")[0].split(" ")[1])

    def get_headers(self,data):
        #find the start index of the body
        body_start = data.find("\r\n\r\n") 
        #find index of empty line
        empty_line = data.find("\r\n") 
        #Header is the body to the empty line
        headers = data[body_start:empty_line] 
        return headers

    def get_body(self, data):
        #find index of start of body
        body_start = data.find("\r\n\r\n") 
        #Splice response accordingly
        body = data[body_start:] 
        return body
    
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

    def url_parser(self, url):
        
        #Use urllib to parse url 
        parsedURL = urllib.parse.urlparse(url)
        #get path if not path return  index
        path = parsedURL.path
        if not path:
           path = "/"
        #get port if not port return 80
        port = parsedURL.port
        if not port:
            port =  80
        #get host if not host return path and index 
        hostname = parsedURL.hostname
        if not hostname:
            hostname = parsedURL.path
            path = "/"
        #Store parsed elements in dict and return dict
        parsed_elements = {"path" : path, "port": port, "hostname" : hostname}
        return parsed_elements          

    def GET(self, url, args=None):
        #fetch parsed url
        parsed_elements = self.url_parser(url)
        #connect on port with host
        self.connect(parsed_elements["hostname"], parsed_elements["port"])
        #base request 
        request = f'GET {parsed_elements["path"]} HTTP/1.0\r\nHost: {parsed_elements["hostname"]}:{parsed_elements["port"]}\r\nConnection: Close\r\n\r\n'
        self.sendall(request)
        receivedMessage = self.recvall(self.socket)
        self.close()

        code = self.get_code(receivedMessage)
        body = self.get_body(receivedMessage)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #fetch parsed url
        parsed_elements = self.url_parser(url)
        #connect to port on host
        self.connect(parsed_elements["hostname"], parsed_elements["port"])
        #base post request
        request = f'POST {parsed_elements["path"]} HTTP/1.0\r\nHost: {parsed_elements["hostname"]}:{parsed_elements["port"]}\r\nConnection: Close\r\n'
        #if the request has arguments find the arguments 
        if args:
            foundArgs = self.find_args(args)
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f'Content-Length: {len(foundArgs.encode("utf-8"))}\r\n\r\n'
            request += foundArgs + '\r\n'
        #if no arguments return base request  
        elif args == None:
            request += "Content-Length: 0\r\n"
        request += '\r\n'
        self.sendall(request)
        receivedMessage = self.recvall(self.socket)
        self.close()

        code = self.get_code(receivedMessage)
        body = self.get_body(receivedMessage)
        return HTTPResponse(code, body)

    #find_args method finds arguments and stores them accordingly
    def find_args(self, args):
        foundArgs = ""
        for key in args:
            val = args[key]
            foundArgs += key + '=' + val + '&'
        return foundArgs[0:len(foundArgs)-1]


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