#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------
# File Name          :portbind.py
# Date               :2022/05/31 09:50:42
# Author             :Charseki.Chen
# Email              :charseki.chen@dbappsecurity.com.cn
# Version            :V1.0.0
# Description        :A script used to control the source port and the number of packets sent
# --------------------------------------------------
"""
$python portbind.py -rhost 10.20.192.252 -rport 80 -lhost 10.11.37.226 -lport 12345 -count 10

[i] Remote target IP: 10.20.192.252
[i] Remote target PORT: 80
[i] Local IP: 10.11.37.226
[i] Local PORT: 12345
[i] Send Count: 10
"""

import sys
import socket
import argparse
import http.client

GREEN = '\033[92m'
PINK = '\033[95m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'


def banner():
    """[banner]"""
    banner = PINK + '''
__________                   __   __________ .__             .___
\______   \  ____  _______ _/  |_ \______   \|__|  ____    __| _/
 |     ___/ /  _ \ \_  __ \\   __\ |    |  _/|  | /    \  / __ | 
 |    |    (  <_> ) |  | \/ |  |   |    |   \|  ||   |  \/ /_/ | 
 |____|     \____/  |__|    |__|   |______  /|__||___|  /\____ | 
                                          \/          \/      \/  
                                                                V1.0.0
Date    :     2022/05/31
Author  :     Charseki.Chen
E-mail  :     charseki.chen@dbappsecurity.com.cn\n''' + ENDC
    print(banner)


class PortBind:
    def __init__(self, rhost, rport, lhost, lport, count, path=None):
        self.path = path
        self.rhost = rhost
        self.rport = rport
        self.lhost = lhost
        self.lport = lport
        self.count = count

    def Send(self):
        """[portbind]"""
        myHttpConn = http.client.HTTPConnection(self.rhost,
                                                self.rport,
                                                source_address=(self.lhost,
                                                                self.lport))
        myHttpConn.debuglevel = 0
        for _ in range(self.count):
            uri_path = "/admin/{}".format(
                self.path) if self.path else "/admin"
            n = _ + 1
            myHttpConn.request("GET", uri_path)
            myHttpResp = myHttpConn.getresponse()
            if 0 == myHttpConn.debuglevel:
                try:
                    print(
                        GREEN +
                        '[{}] --------------- Response Body ---------------\n{}[{}] --------------- Response Body ---------------'
                        .format(n,
                                myHttpResp.read().decode(), n) + ENDC)
                except:
                    print(RED + "[*] An unknown error occured !" + ENDC)
                finally:
                    print(
                        YELLOW +
                        "[*] The Http connection will be closed after some time !"
                        + ENDC)
        myHttpConn.close()


class Validate:

    # Check if IP is valid
    def CheckIP(self, IP):
        self.IP = IP

        ip = self.IP.split('.')
        if len(ip) != 4:
            return False
        for tmp in ip:
            if not tmp.isdigit():
                return False
            i = int(tmp)
            if i < 0 or i > 255:
                return False
        return True

    # Check if PORT is valid
    def Port(self, PORT):
        self.PORT = PORT

        if int(self.PORT) < 1 or int(self.PORT) > 65535:
            return False
        else:
            return True

    # Check if HOST is valid
    def Host(self, HOST):
        self.HOST = HOST

        try:
            # Check valid IP
            socket.inet_aton(
                self.HOST
            )  # Will generate exeption if we try with DNS or invalid IP
            # Now we check if it is correct typed IP
            if self.CheckIP(self.HOST):
                return self.HOST
            else:
                return False
        except socket.error as e:
            # Else check valid DNS name, and use the IP address
            try:
                self.HOST = socket.gethostbyname(self.HOST)
                return self.HOST
            except socket.error as e:
                return False


if __name__ == "__main__":

    banner()
    INFO = '\nA script used to control the source port and the number of packets sent\n'
    try:
        arg_parser = argparse.ArgumentParser(prog=sys.argv[0],
                                             description=YELLOW +
                                             '[*] {}'.format(INFO) + ENDC)
        # 入参调度
        if len(sys.argv) == 1:
            arg_parser.print_help()
            exit()
        arg_parser.add_argument('-rhost',
                                required=True,
                                help='Remote Target Address (IP)')
        arg_parser.add_argument('-rport',
                                required=True,
                                help='Remote Target Port')
        arg_parser.add_argument('-lhost',
                                required=True,
                                help='Local Address (IP)')
        arg_parser.add_argument('-lport', required=True, help='Local Port')
        arg_parser.add_argument('-count', required=True, help='Send Count')
        arg_parser.add_argument('--path',
                                required=False,
                                default=None,
                                help='URI Path')
        args = arg_parser.parse_args()
        print(args)
    except Exception as e:
        print(INFO, RED + "\nError: {}\n".format(str(e)) + ENDC)
        sys.exit(1)

#
# Validation done, start print out stuff to the user
#
    if args.rport:
        rport = int(args.rport)

    if args.rhost:
        rhost = args.rhost

    if args.lport:
        lport = int(args.lport)

    if args.lhost:
        lhost = args.lhost

    if args.count:
        count = int(args.count)

    # Check if RPORT is valid
    if not Validate().Port(rport):
        print(RED +
              "[!] Please Enter Valid RPORT - Choose Between 1 And 65535" +
              ENDC)
        sys.exit(1)

    # Check if LPORT is valid
    if not Validate().Port(lport):
        print(RED +
              "[!] Please Enter Valid LPORT - Choose Between 1 And 65535" +
              ENDC)
        sys.exit(1)

    # Check if RHOST is valid IP
    rhost = Validate().Host(rhost)
    if not rhost:
        print(
            RED +
            "[!] Please Enter Valid RHOST - Choose Between 0.0.0.0 And 255.255.255.255"
            + ENDC)
        sys.exit(1)

    # Check if LHOST is valid IP
    lhost = Validate().Host(lhost)
    if not lhost:
        print(
            RED +
            "[!] Please Enter Valid LHOST - Choose Between 0.0.0.0 And 255.255.255.255"
            + ENDC)
        sys.exit(1)
    #
    # Use PortBind
    #
    PortBind(rhost, rport, lhost, lport, count, args.path).Send()

# [EOF]