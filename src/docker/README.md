# Docker 镜像

该镜像基于 [Dockerfile](https://github.com/docker-library/python/blob/master/3.6/alpine/Dockerfile) 构建。

## 编译

1. 克隆仓库
2. 进入此目录
3. 执行以下命令构建镜像
```bash
export DOCKER_REGISTRY_MIRROR=https://registry.docker-cn.com
docker buildx build --platform linux/amd64,linux/arm64 -t ssh-alert-server:latest --push .
```

## Timeout？

中国大陆用户由于 GreatFirewall 问题，无法使用 Docker Hub。你需要使用 VPN / 代理访问，或者使用镜像站。

鉴于各大高校陆续关闭 Docker Hub 的镜像，建议使用以下方法进行编译：

```bash
# 设置 1ms.run 镜像（感谢 毫秒镜像 支持）
echo '{"registry-mirrors": ["https://docker.1ms.run"]}' | sudo tee /etc/docker/daemon.json > /dev/null
systemctl daemon-reload
systemctl restart docker
# 拉取镜像
# 每日仅 2 GB 额度，故建议先拉取镜像
docker pull 
```