#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------
# File Name          :calnetmask.py
# Date               :2022/06/07 17:11:06
# Author             :Charseki.Chen
# Email              :chenshengkai@vip.qq.com
# Version            :V1.0.0
# Description        :Calculate the network address, broadcast address, and maximum available address of the IP address based on the mask.
# --------------------------------------------------
import sys
import argparse
import re
parser = argparse.ArgumentParser(description="calulate ipaddress")#描述
parser.add_argument("-ip",type=str,help="ipaddress")#参数 ip
parser.add_argument("-mask",type=int,nargs='?',const=1,default=24,help="ip mask") #如果参数只有一个ip，则默认掩码为24
args = parser.parse_args()

class Ipaddress():
    def __init__(self):
        self.ipaddress = args.ip
        self.mask = args.mask
    #最大主机数和最大可用主机数
    def max_hosts(self):
        Max_hosts = 2**(32 - self.mask) #最大主机数
        Max_avail_hosts = Max_hosts - 2 #最大可用主机数
        return Max_hosts,Max_avail_hosts

    #十进制转换为二进制，返回ip地址的二进制数组，子网掩码的二进制数组,子网掩码的取反数组
    def decimal_to_binary(self):
        ip_binary = []
        for number in self.ipaddress.split('.'):
            n=''.join([str((int(number)>>a&0x1))for a in range(7,-1,-1)]) #将ip每位转换为二进制存储
            ip_binary.append(n)
        mask_str = '1'*self.mask+'0'*(32 - self.mask) #网络地址掩码二进制
        mask_binary = re.findall(r'.{8}',mask_str) #将二进制掩码每8位分隔开
        reverse_mask_str = '0'*self.mask+'1'*(32 - self.mask)
        reverse_mask_binary = re.findall(r'.{8}',reverse_mask_str)

        return ip_binary,mask_binary,reverse_mask_binary

    #参数为网络地址的二进制表示，转换为十进制
    def cal_network_address(self,ipmaskstr):
        ip_lis = []
        ipmask = re.findall(r'.{8}',ipmaskstr)
        for i in ipmask:
            ip_lis.append(str(int(i,2))) #将二进制转换为十进制存储
        return '.'.join(ip_lis)


if __name__=='__main__':

    cal = Ipaddress()
    #可用地址数
    _,Max_avail_hosts = cal.max_hosts()

    ip_binary,mask_binary,reverse_mask_binary= cal.decimal_to_binary()

    #ip地址的二进制表示
    ip_binary = ''.join(ip_binary)

    #子网掩码的二进制表示
    mask_binary = ''.join(mask_binary)

    #子网掩码取反的二进制表示
    reverse_mask_binary = ''.join(reverse_mask_binary)

    #网络地址的二进制表示
    net_mask = ''.join([str(int(n[0])&int(n[1])) for n in zip(ip_binary,mask_binary)])

    #广播地址的二进制表示
    broadcast_mask = ''.join([str(int(n[0])|int(n[1])) for n in zip(net_mask,reverse_mask_binary)])

    network_address = cal.cal_network_address(net_mask) #网络地址

    broadcast_address = cal.cal_network_address(broadcast_mask)

    first_address = '.'.join(network_address.split('.')[:3])+'.'+str(int(network_address.split('.')[3])+1)

    last_address = '.'.join(broadcast_address.split('.')[:3])+'.'+str(int(broadcast_address.split('.')[3])-1)
    print('========IP信息如下=======')
    print('{} {}'.format('可用地址   |',Max_avail_hosts))
    print('-----------|-------------')
    print('{} {}'.format('网络地址   |',network_address))
    print('-----------|-------------')
    print('{} {}'.format('广播地址   |',broadcast_address))
    print('-----------|-------------')
    print('{} {}'.format('第一可用   |',first_address))
    print('-----------|-------------')
    print('{} {}'.format('最后可用   |',last_address))
    print('-----------|-------------')