# 基于 Alpine 镜像制作的最小系统
FROM alpine:latest
LABEL authors="KirsminX"

# 使用中科大镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# 安装基本依赖 OpenSSH 和 bash, 并安装 wget 用于下载脚本
RUN apk update --update && \
    apk add --no-cache openssh bash wget

# 生成符合要求的随机密码，设置为用户密码，保存到 /Data/Password
RUN mkdir -p /Data && \
    head -c 16 /dev/urandom | base64 > /Data/Password && \
    echo "Generated Password:" && cat /Data/Password && \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo "Setting root password..." && \
    echo "root:$(cat /Data/Password)" | chpasswd && \
    echo "Root password set."

# 暴露 22 Port
EXPOSE 22

# 下载启动脚本
RUN wget -O /start.sh https://github.com/KirsminX/SSHAlert/raw/refs/heads/main/src/docker/start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
