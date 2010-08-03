#!/usr/bin/env python
import socket
import os
import subprocess
import select
import sys
import time

sockfile = os.path.expanduser("~/.muxpd.sock")

class ChangeRequestDelegated(Exception): pass

class Muxpd(object):
    def __init__(self, newhost=None, newport=None):
        oldhost, oldport = None, None
        self.socatp = None

        # first: try to connect to a currently running daemon
        if os.path.exists(sockfile):
            try:
                csock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                csock.connect(sockfile)
                csock.send("change %s %s" % (newhost, newport))
                oldhost, oldport = csock.recv(1024).split(" ")
                csock.close()
                raise ChangeRequestDelegated()
            except socket.error:
                os.remove(sockfile)
        
        connected = False
        while not connected:
            try:
                self.ctrls = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.ctrls.bind(sockfile)
                connected = True
            except Exception, e:
                print e
                time.sleep(0.5)

        self.ctrls.listen(1)

        if oldhost and not newhost: 
            self.host = oldhost
        else: 
            self.host = newhost
        if oldport and not newport:
            self.port = oldport
        else:
            self.port = newport

        # next. start socat
        self.start_socat()

    def start_socat(self):
        if self.socatp:
            self.socatp.terminate()
        opts = ["socat", "tcp-listen:6600,reuseaddr,fork,forever", "tcp-connect:%s:%s" % (self.host, self.port)]
        self.socatp = subprocess.Popen(opts)
        print opts

    def loop(self):
        die = False
        while not die:
            rlist, wlist, xlist = select.select([self.ctrls], [], [])
            if rlist:
                (sock, addr) = self.ctrls.accept()
                sock.send("%s %s" % (self.host, self.port))
                
                data = sock.recv(1024)
                if data.startswith("die"):
                    die = True
                elif data.startswith("change"):
                    _, self.host, self.port = data.split(" ")
                    self.port = int(self.port)
                    self.start_socat()

                sock.close()
        
        print "dieing"
        os.remove(sockfile)
        self.socatp.terminate()
        time.sleep(1)
        self.socatp.kill()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        host = "localhost"
        port = 6601
    else:
        if ":" in sys.argv[-1]:
            host, port = sys.argv[-1].split(":")
        else:
            host, port = sys.argv[-1], 6600
    
    try:
        mux = Muxpd(host, port)
        mux.loop()
    except ChangeRequestDelegated:
        pass
