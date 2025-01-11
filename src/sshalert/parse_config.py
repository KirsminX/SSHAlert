import rtoml
import os
import log
import sys
from typing import Union, Optional
log = log.Log()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, 'config'):
            return

        self.PATH = "Config.toml"
        self.config = None

        if not os.path.exists(self.PATH):
            self.config = rtoml.loads(DEFAULT_CONFIG)
            self.__save__()
            log.info("配置文件不存在，已创建默认配置文件！")
        else:
            self.__load__()

    def __load__(self):
        try:
            with open(self.PATH, "r") as f:
                self.config = rtoml.load(f)
        except Exception as e:
            log.error(f"加载配置文件失败：{e}")
            sys.exit(1)

    def __save__(self):
        try:
            with open(self.PATH, "w") as f:
                rtoml.dump(self.config, f)
        except Exception as e:
            log.error(f"保存配置文件失败：{e}")
            sys.exit(1)

    def get(self, table: Optional[str] = None,
            key: Optional[str] = None) -> Union[dict, str]:
        try:
            if table is None:
                return self.config
            if key is None:
                return self.config[table]
            return self.config[table][key]
        except KeyError as e:
            log.error(f"获取配置项失败：{e}")
            return {}


# 默认配置文件
DEFAULT_CONFIG = """# SSH Alert 配置文件

[SSHServer]
# 主机名（默认「Debian Server」）
ServerName = "Debian Server"
# 端口（默认「22。」不建议修改）
Port = 22

[Database]
# SQLite3 数据库路径（默认「Database.db」）
Path = "Database.db"

[Time]
# 时区（默认「Asia/Shanghai」。如需修改请确保时区 Pytz 支持
TimeZone = "Asia/Shanghai"

[Setting]
# 是否自动更新（默认「true」）
AutoUpdate = true
# 更新服务器（默认「」。默认使用第一个，当第一个无法使用时，会按照顺序尝试）
UpdateAddress = ["",""]
# 更新间隔（默认「600」，单位：时）
Interval = 600"""
