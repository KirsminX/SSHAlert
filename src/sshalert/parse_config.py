import rtoml
import os
import log
import sys
import pytz
import re
from typing import Union, Optional
log = log.Log()


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
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

        self.validate()

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

    def validate(self):
        errors = []

        # SSHServer 验证
        if not isinstance(self.config.get('SSHServer', {}).get('ServerName'), str):
            errors.append("`ServerName` 的值必须为字符串！")
        if 'Port' in self.config.get('SSHServer', {}):
            port = self.config['SSHServer']['Port']
            if not (isinstance(port, int) and 1 <= port <= 65535):
                errors.append("`Port` 的值必须为整数，1-65535！")

        # Database 验证
        db_path = self.config.get('Database', {}).get('Path')
        if db_path and not os.path.isfile(db_path):
            errors.append("`[Database].Path` 此数据库文件不存在！ ")

        # Time 验证
        time_zone = self.config.get('Time', {}).get('TimeZone')
        if time_zone and time_zone not in pytz.all_timezones:
            errors.append("`[Time].TimeZone` 必须为有效的时区字符串！")

        # Setting 验证
        setting = self.config.get('Setting', {})
        auto_update = setting.get('AutoUpdate')
        if auto_update is not None and not isinstance(auto_update, bool):
            errors.append("`[Setting].AutoUpdate` 必须为布尔值！")

        update_address = setting.get('UpdateAddress')
        if update_address is not None:
            if not (isinstance(update_address, list) and len(update_address) > 0):
                errors.append("`[Setting].UpdateAddress` 必须为非空字符串列表！")
            else:
                url_pattern = re.compile(r'https?://\S+\.txt$')
                for url in update_address:
                    if not url_pattern.match(url):
                        errors.append(f"`[Setting].UpdateAddress` 无效的更新地址: {url}！")

        interval = setting.get('Interval')
        if interval is not None:
            if not (isinstance(interval, int) and interval > 2):
                errors.append("`[Setting].Interval` 必须为大于 2 的整数！")

        if errors:
            log.error("配置文件验证失败！以下是错误信息:")
            for error in errors:
                log.error(f"- {error}")
            sys.exit(1)


# 默认配置文件
DEFAULT_CONFIG = """# SSH Alert 配置文件

[SSHServer]
# 主机名（默认「Debian Server」）
ServerName = "Debian Server"
# 端口（默认「22」，不建议修改）
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
# 更新间隔（默认「600」，单位：时，大于 2 的正整数）
Interval = 600"""
