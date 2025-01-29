import os
import sys
from contextlib import asynccontextmanager
from enum import Enum
from typing import Union

import aiosqlite

from validator import DataValidator
from log import Log
log = Log()


class TableNotMatch(Exception):
    pass


class Way(Enum):
    """获取方式的枚举类"""
    IP = "IP"
    PASSWORD = "Password"
    VERSION = "Version"
    SESSION_ID = "SessionID"
    LOCATION = "Location"
    DATE = "Date"
    TIME = "Time"
    COUNT = "Count"

    @classmethod
    def get_error_message(cls, way):
        """获取对应字段缺失的错误信息"""
        messages = {
            cls.IP: "未传入 IP 地址！",
            cls.PASSWORD: "未传入密码！",
            cls.VERSION: "未传入版本号！",
            cls.SESSION_ID: "未传入会话 ID！",
            cls.LOCATION: "未传入地区！",
            cls.DATE: "未传入日期！",
            cls.TIME: "未传入时间！",
            cls.COUNT: "未传入攻击次数！"
        }
        return messages.get(way, "未知字段！")


class Database:
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance__ is None:
            cls.__instance__ = super().__new__(cls)
        return cls.__instance__

    def __init__(self, fix_by_force=False, path="Database.db"):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.path = path
        self.fix_by_force = fix_by_force
        self._ready = False

        self.TABLE_SCHEMA = """CREATE TABLE Data (
                    Number INTEGER PRIMARY KEY AUTOINCREMENT,
                    Count INTEGER,
                    Date TEXT,
                    Time TEXT,
                    IP TEXT,
                    UserName TEXT,
                    Password TEXT,
                    Version TEXT,
                    SessionID TEXT,
                    Location TEXT
                );"""

    def __await__(self):
        """使类实例成为可等待对象"""

        async def _initialize():
            if not self._ready:
                try:
                    await self._init_database(self.fix_by_force)
                    self._ready = True
                except Exception:
                    Database.__instance__ = None
                    raise
            return self

        return _initialize().__await__()

    @asynccontextmanager
    async def _get_cursor(self):
        """创建数据库连接的异步上下文管理器"""
        async with aiosqlite.connect(self.path) as conn:
            async with conn.cursor() as cursor:
                yield cursor
                await conn.commit()

    async def _init_database(self, fix_by_force):
        """初始化数据库"""
        async with self._get_cursor() as cursor:
            if fix_by_force:
                await cursor.execute("DROP TABLE IF EXISTS Data")
                await cursor.execute(self.TABLE_SCHEMA)
                return

            if not os.path.exists(self.path):
                await cursor.execute(self.TABLE_SCHEMA)
                return

            await cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='Data'")
            Result = await cursor.fetchone()

            if not Result:
                await cursor.execute(self.TABLE_SCHEMA)
            elif ' '.join(Result[0].split()) != ' '.join(self.TABLE_SCHEMA.split()):
                raise TableNotMatch()

    async def delete(self, **kwargs) -> Union[int, tuple[bool, str]]:
        """删除记录"""
        if not self._ready:
            await self

        async with self._get_cursor() as cursor:
            field_mapping = {
                'ip': 'IP',
                'password': 'Password',
                'version': 'Version',
                'session_id': 'SessionID',
                'location': 'Location',
                'date': 'Date',
                'time': 'Time',
                'username': 'UserName',
                'count': 'Count',
                'number': 'Number'
            }

            conditions = []
            values = []

            for key, value in kwargs.items():
                formatted_key = field_mapping.get(key.lower(), key)
                conditions.append(f"{formatted_key} = ?")
                values.append(value)
            # noinspection SqlWithoutWhere
            query = "DELETE FROM Data"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            else:
                # noinspection SqlWithoutWhere
                await cursor.execute("DELETE FROM Data")
                await cursor.execute("DELETE FROM sqlite_sequence WHERE name='Data'")
                return False, "删除操作必须指定至少一个条件"

            try:
                await cursor.execute(query, values)
                return cursor.rowcount
            except aiosqlite.Error as e:
                return False, f"数据库错误: {str(e)}"

    async def insert(self, **kwargs) -> Union[int, tuple[bool, str]]:
        """插入记录"""
        if not self._ready:
            await self

        validator = DataValidator()
        is_valid, message = validator.validate_record(kwargs)
        if not is_valid:
            return False, message

        async with self._get_cursor() as cursor:
            formatted_kwargs = {}
            field_mapping = {
                'ip': 'IP',
                'password': 'Password',
                'version': 'Version',
                'session_id': 'SessionID',
                'location': 'Location',
                'date': 'Date',
                'time': 'Time',
                'username': 'UserName',
            }

            for key, value in kwargs.items():
                formatted_key = field_mapping.get(key.lower(), key)
                formatted_kwargs[formatted_key] = value

            fields = list(formatted_kwargs.keys())
            values = list(formatted_kwargs.values())
            placeholders = ['?'] * len(fields)

            query = f"""
                INSERT INTO Data ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
            """

            try:
                await cursor.execute(query, values)
                return cursor.lastrowid
            except aiosqlite.Error as e:
                return False, f"数据库错误: {str(e)}"

    async def get(self, **kwargs):
        """查询记录"""
        if not self._ready:
            await self

        async with self._get_cursor() as cursor:
            conditions = []
            values = []

            for key, value in kwargs.items():
                try:
                    conditions.append(f"{key.upper()} = ?")
                    values.append(value)
                except KeyError:
                    raise ValueError(f"无效的查询字段: {key}")

            query = "SELECT * FROM Data"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            await cursor.execute(query, values)
            return await cursor.fetchall()


async def fixer(database_path):
    log.info("是否**重置数据库**？")
    log.info("输入 Y 以 **重置数据库**，输入 N 、[Space] 或者其他值退出")
    user_input = input("[Y/N/Others]>")
    if user_input.upper() == "Y":
        log.info("正在重置数据库...")
        # noinspection PyUnusedLocal
        temp = Database(path=database_path, fix_by_force=True)
        log.info("重置数据库完成！")
        del temp
    else:
        log.error("退出 SSH Alert！")
        sys.exit(1)
