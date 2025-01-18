# 基于 Alpine 镜像制作的最小系统
FROM alpine:latest
LABEL authors="KirsminX"

# 使用中科大镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# 安装基本依赖 OpenSSH 和 bash
RUN apk update --update && \
    apk add --no-cache openssh bash \

# 生成随机密码，设置为用户密码，保存到 /Data/Password
RUN mkdir -p /Data && \
    head -c 1024 /dev/urandom | base64 > /Data/Password \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo "root:$(cat /Data/Password)" | chpasswd \

# 暴露 22 Port
EXPOSE 22

# 写入启动脚本
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]