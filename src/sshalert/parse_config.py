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
        try:
            # SSHServer 验证
            assert isinstance(self.config['SSHServer']['ServerName'], str), "`ServerName` 的值必须为字符串！"
            assert 1 <= self.config['SSHServer']['Port'] <= 65535, "`Port` 的值必须为整数，1-65535！"

            # Database 验证
            assert os.path.isfile(self.config['Database']['Path']), "`[Database].Path` 此数据库文件不存在！ "

            # Time 验证
            assert self.config['Time']['TimeZone'] in pytz.all_timezones, "`[Time].TimeZone` 必须为 bool 值！"

            # Setting 验证
            assert isinstance(self.config['Setting']['AutoUpdate'], bool), "`[Setting].AutoUpdate` 必须 bool 值！"
            assert isinstance(self.config['Setting']['UpdateAddress'], list) and len(
                self.config['Setting']['UpdateAddress']) > 0, "`[Setting].UpdateAddress` 必须为字符串列表，不能为空！"
            url_pattern = re.compile(r'https?://\S+\.txt$')
            for url in self.config['Setting']['UpdateAddress']:
                assert url_pattern.match(url), f"`[Setting].UpdateAddress` 无效的更新地址: {url}！"
            assert isinstance(self.config['Setting']['Interval'], int) and self.config['Setting'][
                'Interval'] > 2, "`[Setting].Interval` 必须为整数，且大于 2！"

        except AssertionError as e:
            log.error(f"配置文件验证失败: {str(e)}")
            sys.exit(1)
        except KeyError as e:
            log.error(f"配置文件缺少必要的键: {str(e)}")
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
