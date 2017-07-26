#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import cgi

import argparse

import threading
import datetime


from http.server import BaseHTTPRequestHandler, HTTPServer


# HTTPRequestHandler class
class RequestHandlerClass(BaseHTTPRequestHandler):


    def do_HEAD(self):
            '''
            Handle a HEAD request.
            '''
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

    def WriteToLog(self,Logger,level,message):
        some_rlock = threading.RLock()
        dFile = datetime.datetime.now().strftime("%B_%d_%Y")
        filename = './Logs/' + Logger+dFile + '.log'

        if os.path.exists(filename):
            append_write = 'a' 
        else:
            append_write = 'w' 
        d = datetime.datetime.now().strftime("[%B/%d/%Y  %I:%M:%p]")
        strmsg = "{0:s} {1:s} - {2:s}".format(d,level,message)

        with some_rlock:
            highscore = open(filename,append_write)
            highscore.write(strmsg + '\n')
            highscore.close()



    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}
            loggerData = (postvars[b'logger'][0]).decode('utf-8')
            levelData = (postvars[b'levelname'][0]).decode('utf-8')
            messageData = (postvars[b'message'][0]).decode('utf-8')
            
            self.WriteToLog(loggerData,levelData,messageData)         
            

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.writeStr("{'status':'OK'}")
        except ValueError:  
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            self.writeStr("{'status':'Error'}")   
          


    def writeStr(self,message):
        self.wfile.write(bytes(message, "utf8"))

    def sendErrorPage(self):
       
        self.send_response(500)  
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.writeStr('<html>')
        self.writeStr('  <head>')
        self.writeStr('  <link rel="stylesheet" type="text/css" href="/css/main.css" media="screen" />')
        self.writeStr('    <title>Server Access Error</title>')
        self.writeStr('  </head>')
        self.writeStr('  <body class="main_bg">')
        self.writeStr('    <p class="error"><strong>Server access error.</strong></p>')
        self.writeStr('    <p class="errmsg">%r</p>' % (repr(self.path)))
        self.writeStr('  </body>')
        self.writeStr('</html>')

    def err(msg):
       '''
       Report an error message and exit.
       '''
       print('ERROR: %s' % (msg))
       sys.exit(1)



    def do_GET(self):
            '''
            Handle a GET request.
            '''

            content_type = {
                        '.css': 'text/css',
                        '.gif': 'image/gif',
                        '.htm': 'text/html',
                        '.html': 'text/html',
                        '.jpeg': 'image/jpeg',
                        '.jpg': 'image/jpg',
                        '.js': 'text/javascript',
                        '.png': 'image/png',
                        '.text': 'text/plain',
                        '.txt': 'text/plain',
                        '.json':'application/json',
                        '.ico': 'image/vnd.microsoft.icon',
                    }

          

                # Get the file path.
            path =  self.path
            
            
            
            if len(path) < 3:
               try:
                 f = open("index.html", "r")
                 self.do_HEAD()
                 self.wfile.write(bytes(f.read(), "utf8"))
                 return
               except:
                   self.sendErrorPage()
            
            
            _, ext = os.path.splitext(path)
            
            if len(ext) == 0 :
                path +=  ".html";
            
            
            dirpath = ''
            sp = path.split('/')[:-1]
            for dirf in sp:
                dirpath = dirpath  + dirf + '/'
                
            dirpath = "." + dirpath  
            path = "." + path
                
              
                       
            if os.path.exists(dirpath) and os.path.isfile(path):

                _, ext = os.path.splitext(path)
                ext = ext.lower()

                if ext in content_type:
                    try:
                        with open(path, mode='rb')  as ifp:
                            self.send_response(200)  # OK
                            self.send_header('Content-type', content_type[ext])
                            self.end_headers()
                            va = ifp.read()
                            self.wfile.write(va)
                    except Error:
                        print("not open file: "+ path + ' ' + Error)
                        self.sendErrorPage()

                else:
                    self.sendErrorPage()
            else:
               self.sendErrorPage()


def run():
       
         server_address = ('127.0.0.1', 8081)
         httpd = HTTPServer(server_address, RequestHandlerClass)
         print('running server...')
         httpd.serve_forever()
         httpd.server_close()
         print('server stopping')


if __name__ == "__main__":
     run()
