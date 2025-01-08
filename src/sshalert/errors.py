class DockerNotRunning(Exception):
    """
    当 Docker 容器未运行时，抛出此错误
    """
    def __init__(self):
        pass
