#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse
# imoprt URL parse? from urlparse import urlparse


def help():
    print "httpclient.py [GET/POST] [URL]\n"


class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    # couldn't get the other way to work... tyring this way
    def connect(self, host, port=80):

        if(not port):
            port = 80
        try:
            # could not get the .bind and .listen to work. This did work.
            sock = socket.create_connection((host, port), 10)
        # Creation caused exception. Print it and exit()
        except socket.error as err:
            print 'Failed to create socket'
            print 'Code: ' + str(err[0]) + ' Message: ' + err[1]
            sys.exit()
        return sock

    def disconnect(self, sock):
        try:
            sock.close()
        except:
            print("Failed to close socket")

    def set_headers(self, command, host, port, path, args):
        header = command + " " + path + " HTTP/1.1\r\nHost: " + host + "\r\n"
        header = header + "Connection: close\r\n"
        # header = header + "User-Agent: ????\r\n"
        header = header + "Accept-Encoding: */*\r\n"
        if(command is "POST"):
            # encode the body and finish the header, then add the body
            if args:
                body = urllib.urlencode(args, True)
                length = str(len(body))
            else:
                length = "0"
                body = ""
            header = header + "Content-type: "
            header = header + "application/x-www-form-urlencoded\r\n"
            header = header + "Content-length: " + length + "\r\n\r\n"
            header = header + body
        header = header + "\r\n"

        return header

    def get_code(self, data):
        # split the data to get the code. Stop at 5, any more is unnecessary
        if not data:
            return 500
        code = data.split(" ", 3)[1]
        return code

    def get_body(self, data):
        if not data:
            return ""
        # split the data to get the code. Stop at 3, any more is unnecessary
        body = data.split("\r\n\r\n", 3)[1] + "\r\n"
        return body

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
        return str(buffer)

    def GET(self, url, args=None):
        # parse out the components of the URL
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port
        path = parsed.path

        # Create the socket
        sock = self.connect(host, port)

        # Build the header
        header = self.set_headers("GET", host, port, path, args)

        # Send the header through the socket
        sock.sendall(header)

        # Receive the response
        received = self.recvall(sock)
        # Receive the code and body
        code = self.get_code(received)
        body = self.get_body(received)

        req = HTTPRequest(code, body)
        self.disconnect(sock)
        return req

    def POST(self, url, args=None):
        # parse out the components of the URL
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port
        path = parsed.path

        # Create the socket
        sock = self.connect(host, port)

        # Build the header
        header = self.set_headers("POST", host, port, path, args)

        # Send the header through the socket
        sock.sendall(header)

        # Receive the response
        received = self.recvall(sock)
        # Receive the code and body
        code = self.get_code(received)
        body = self.get_body(received)

        req = HTTPRequest(code, body)
        self.disconnect(sock)
        return req

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print("client commads [1] and [2]")
        print client.command(sys.argv[1], sys.argv[2])
    else:
        print("client commads [1]")
        print client.command(command, sys.argv[1])
