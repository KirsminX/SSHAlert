import docker
"""
Docker Images 管理
- 方法
* todo!()
- 抛出错误
* DockerNotRunning              Docker 未运行/安装/响应
"""

class DockerNotRunning(Exception):
    def __init__(self):
        pass

class Docker:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = super().__new__(cls)
        return cls.__instance__

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception:
            raise DockerNotRunning()


if __name__ == '__main__':
    try:
        docker = Docker()
    except DockerNotRunning:
        print("Docker is not running.")