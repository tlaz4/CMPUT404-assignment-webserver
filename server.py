#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        parsedRequest = self.parseRequest(self.data)
        
        response = self.respond(parsedRequest)
        self.request.sendall(bytearray(response,'utf-8'))

    # get the requested file, check if the file is a directory so we can handle accordingly
    # also make sure we are in www for security purposes
    def checkFile(self, name):
        path = "./www" + name

        if not self.isInRoot(path):
            return None

        if os.path.isdir(path):
            if not path.endswith("/"):
                print("redirect incoming")
                return "301"

            else:
                path += "index.html"
        
        return self.getFile(path)
        

    # simply open file unles IO error
    def getFile(self, path):
        try:
            file = open(path, 'r')
            return file.read()

        except IOError:
            return None

    # parse all headers and their content, technically not necessary since we only need the request type
    # and the location, but for functional sake lets do it
    # turn request headers into dictionaries
    def parseRequest(self, data):
        parsedRequest = {}

        parsed = data.decode().split("\r\n")
        
        parsedRequest["request"] = parsed[0]
        for i in range(1, len(parsed)):
            obj = parsed[i].split(":")
            parsedRequest[obj[0]] = obj[1]

        return parsedRequest

    # Author: unutbu
    #https://stackoverflow.com/questions/3220755/how-to-find-the-target-files-fullabsolute-path-of-the-symbolic-link-or-soft-l
    # make sure www is in file path
    def isInRoot(self, path):
        if "www" not in os.path.realpath(path):
            return False
        else:
            return True

    # get file type to send mime type
    def getFileType(self, file):
        if "." in file:
            return file.split(".")[1]
        else:
            return "html"

    # respond to request accordingly
    # is function modular enough? consider future refactoring
    def respond(self, request):
        okResponse = "HTTP/1.1 200 OK\r\n"
        movedResponse = "HTTP/1.1 301 Moved Permanently\r\n"
        notFoundResponse = "HTTP/1.1 404 Not Found\r\n"
        notAllowedResponse = "HTTP/1.1 405 Method Not Allowed\r\n"

        # check if get is in in request, if so, serve requested file
        if "GET" in request["request"]:
            file = request["request"].split(" ")[1]
            fileContent = self.checkFile(file)

            # if file doesnt equal None, it must exist, so it might be a 301 or a 200
            if fileContent != None:

                # file has been moved, serve accordingly with moved location
                if fileContent == "301":
                    location = "http://127.0.0.1:8080" + file +"/" + "\r\n"
                    return movedResponse + "Location: {}\r\n".format(location) 

                # file exists, send a 200 response with requested file
                else:
                    mimeType = "Content-Type: text/{}\r\n".format(self.getFileType(file))
                    return okResponse + mimeType + "\r\n" + fileContent

            # file doesnt exist, send 404
            else:
                return notFoundResponse + "\r\n"

        # method isnt allowed, send 405
        else:
            return notAllowedResponse + "\r\n"






        





if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
