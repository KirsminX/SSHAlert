#!/bin/sh

# 启动SSH服务
/etc/init.d/sshd start

# 获取登录信息
IP=$(hostname -I | awk '{print $1}')
PASSWORD=$(cat /Data/Password)
USERNAME="root"
TIME=$(date)
SESSIONID=$(cat /proc/sys/kernel/random/boot_id)

# 将登录信息写入/Data/LoggingInformation
echo "IP: $IP, Password: $PASSWORD, Username: $USERNAME, Time: $TIME, SessionID: $SESSIONID" > /Data/LoggingInformation

# 保持容器运行
tail -f /dev/null