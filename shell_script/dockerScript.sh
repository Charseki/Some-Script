#!/bin/bash
# Filename ：dockerScript.sh
# Author   ：Charseki.Chen
# Email    ：charseki.chen@dbappsecurity.com.cn

yesnoinput()
{
    while :
    do
        read ANSWER
        case $ANSWER in
        "yes"|"YES")
            return 0
            ;;
        "no"|"NO")
            return 1
            ;;
        *)
            echo -n "[WARNING] Unknown input. "
            ;;
        esac
        printf "Please input [yes..no]: "
    done
}

iptablesconfig()
{
    iptables -P INPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -P OUTPUT ACCEPT

    iptables -F
    iptables -X
    iptables -Z

    iptables-save >/etc/sysconfig/iptables

    touch /etc/rc.d/rc.local
    chmod 755 /etc/rc.d/rc.local
    sed -i /iptables/d /etc/rc.d/rc.local
    echo "iptables-restore < /etc/sysconfig/iptables" >>/etc/rc.d/rc.local

    sed -i 's/SELINUX=.*$/SELINUX=disabled/g' /etc/sysconfig/selinux &>/dev/null    #centos7
    sed -i 's/SELINUX=.*$/SELINUX=disabled/g' /etc/selinux/config &>/dev/null       #centos6

    setenforce 0 &>/dev/null
    systemctl stop firewalld &>/dev/null
    systemctl disable firewalld &>/dev/null
}

systemconfig()
{
    #修改系统语言 需要为英文
    sed -i 's/^LANG=.*$/LANG="en_US.UTF-8"/g' /etc/locale.conf

    #修改时区相差八小时问题
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

    #ssh登陆慢
    sed -i '/^UseDNS/d' /etc/ssh/sshd_config
    sed -i '/^#UseDNS/a\UseDNS no' /etc/ssh/sshd_config
    sed -i '/^GSSAPIAuthentication/d' /etc/ssh/sshd_config
    sed -i '/^#GSSAPIAuthentication/a\GSSAPIAuthentication no' /etc/ssh/sshd_config
    systemctl enable sshd
    systemctl restart sshd

    #配置DNS服务器
    echo "nameserver 114.114.114.114"  >/etc/resolv.conf

    #修改history相关属性
    mkdir -p /etc/profile.d

    echo "
PS1='\[\033[01;35m\][\u@\h \w]\\\$ \[\033[00m\]'
HISTSIZE=1000000

mkdir -p /root/.history
HISTFILE=/root/.history/history_\`echo \$SSH_CLIENT | cut -d' ' -f1\`
HISTTIMEFORMAT=\"[%F %T] \"
export HISTTIMEFORMAT
export PROMPT_COMMAND=\"history -a\"

export LANG=en_US.UTF-8
export LESSCHARSET=UTF-8

" >/etc/profile.d/private.sh

    source /etc/profile.d/private.sh

}

vimconfig()
{
    touch ~/.vimrc

    echo "
\"\"Charseki.Chen  Setting
set nocompatible
set backspace=indent,eol,start
set tabstop
set cursorline
set autoindent
\"\"set backup
syntax on
set hlsearch
filetype plugin on
set ruler
set ts=4
set sw=4
set shiftwidth=4
set softtabstop=4
set nu
set autoindent
\"\"set textwidth=200
set noexpandtab
set encoding=utf-8
set fileencoding=utf-8
set fileencodings=ucs-bom,utf-8,chinese
set modeline
set t_vb=
" > ~/.vimrc

}

dockerconfig()
{
    sed -i 's!cachedir=.*$!cachedir=/opt/yum/!g' /etc/yum.conf
    sed -i 's/^keepcache=.*$/keepcache=1/g' /etc/yum.conf
    sed -i 's/^gpgcheck=.*$/gpgcheck=0/g' /etc/yum.conf
    sed -i 's/^plugins=.*$/plugins=0/g' /etc/yum.conf
    sed -i 's/^enabled=.*$/enabled=0/g' /etc/yum/pluginconf.d/fastestmirror.conf

    mkdir -p /etc/yum.repos.d/
    rm -rf /etc/yum.repos.d/*

    echo "
[base]
name=Base
baseurl=https://mirrors.aliyun.com/centos/7/os/x86_64/
enabled=1

[epel]
name=epel
baseurl=https://mirrors.aliyun.com/epel/7/x86_64/
enabled=1

[extra]
name=extra
baseurl=https://mirrors.aliyun.com/centos/7/extras/x86_64/
enabled=0

[docker]
name=docker
baseurl=https://mirrors.aliyun.com/docker-ce/linux/centos/7/x86_64/stable/
enabled=0
" >/etc/yum.repos.d/CentOS-Base.repo
    yum clean all && yum makecache
    yum -y install vim yum-utils device-mapper-persistent-data lvm2 wget
    # 安装docker环境依赖
    yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    yum makecache fast
    wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
    yum  -y install epel-release container-selinux docker-ce # 安装最新的contain-selinux
    mkdir -p /data/docker && mkdir -p /etc/docker
    touch /etc/docker/daemon.json
    echo -n "{\"registry-mirrors\": [\"https://isj3n34q.mirror.aliyuncs.com\"]}" > /etc/docker/daemon.json
    systemctl start docker
    systemctl enable docker
    # 拉取镜像 upload-labs 
    docker pull c0ny1/upload-labs && docker run -d --name upload_lab -p 1111:80 c0ny1/upload-labs:latest
    # 拉取镜像 dvwa
    docker pull vulnerables/web-dvwa && docker run -d -p 2222:80 vulnerables/web-dvwa && echo -n "Congratulations on your successful installation !"
}

echo -n "[INFO] Make sure you run the script to install the Docker environment now ? [yes/no]: "
yesnoinput

if [ "$?" -ne 0 ]; then
    echo "Exit script!"
    exit 1
fi

iptablesconfig
systemconfig
vimconfig
dockerconfig
