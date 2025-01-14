import sqlite3
import os
from contextlib import contextmanager
from enum import Enum
from validator import DataValidator
from typing import Union


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
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.path = path
        self.TABLE_SCHEMA = """CREATE TABLE Data (
                    Number INTEGER PRIMARY KEY AUTOINCREMENT,
                    Count INTEGER,
                    Date TEXT,
                    Time TEXT,
                    IP TEXT,
                    UserName TEXT,
                    Way TEXT,
                    Password TEXT,
                    Version TEXT,
                    SessionID TEXT,
                    Location TEXT
                );"""

        try:
            self._init_database(fix_by_force)
        except Exception:
            Database.__instance__ = None
            raise

    @contextmanager
    def _get_cursor(self):
        """创建数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.path)
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            conn.close()

    def _init_database(self, fix_by_force):
        """初始化数据库"""
        with self._get_cursor() as cursor:
            if fix_by_force:
                cursor.execute("DROP TABLE IF EXISTS Data")
                cursor.execute(self.TABLE_SCHEMA)
                return

            if not os.path.exists(self.path):
                cursor.execute(self.TABLE_SCHEMA)
                return

            # 检查表是否存在
            cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='Data'")
            Result = cursor.fetchone()

            if not Result:
                cursor.execute(self.TABLE_SCHEMA)
            elif ' '.join(Result[0].split()) != ' '.join(self.TABLE_SCHEMA.split()):
                raise TableNotMatch()

    def delete(self, **kwargs) -> Union[int, tuple[bool, str]]:
        """
        根据条件删除记录
        返回：成功时返回删除的记录数，失败时返回(False, 错误信息)
        """
        with self._get_cursor() as cursor:
            # 将传入的键转换为正确的大小写
            field_mapping = {
                'ip': 'IP',
                'password': 'Password',
                'version': 'Version',
                'session_id': 'SessionID',
                'location': 'Location',
                'date': 'Date',
                'time': 'Time',
                'username': 'UserName',
                'way': 'Way',
                'count': 'Count',
                'number': 'Number'
            }

            conditions = []
            values = []

            # 构建删除条件
            for key, value in kwargs.items():
                formatted_key = field_mapping.get(key.lower(), key)
                conditions.append(f"{formatted_key} = ?")
                values.append(value)

            # 构建SQL删除语句
            # 警告 IDE 不要警告我 :)
            # noinspection SqlWithoutWhere
            query = "DELETE FROM Data"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            else:
                # noinspection SqlWithoutWhere
                cursor.execute("DELETE FROM Data")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='Data'")
                return False, "删除操作必须指定至少一个条件"

            try:
                cursor.execute(query, values)
                return cursor.rowcount
            except sqlite3.Error as e:
                return False, f"数据库错误: {str(e)}"

    def insert(self, **kwargs) -> Union[int, tuple[bool, str]]:
        """
        插入一条记录
        返回：成功时返回记录ID，失败时返回(False, 错误信息)
        """
        # 数据验证
        validator = DataValidator()
        is_valid, message = validator.validate_record(kwargs)
        if not is_valid:
            return False, message

        with self._get_cursor() as cursor:
            # 准备插入数据
            # 将传入的键转换为正确的大小写
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
                'way': 'Way'
            }

            for key, value in kwargs.items():
                formatted_key = field_mapping.get(key.lower(), key)
                formatted_kwargs[formatted_key] = value

            fields = list(formatted_kwargs.keys())
            values = list(formatted_kwargs.values())
            placeholders = ['?'] * len(fields)

            # 构建SQL插入语句
            query = f"""
                INSERT INTO Data ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
            """

            try:
                cursor.execute(query, values)
                return cursor.lastrowid
            except sqlite3.Error as e:
                return False, f"数据库错误: {str(e)}"

    def get(self, **kwargs):
        """
        根据传入的参数获取数据库记录
        """
        with self._get_cursor() as cursor:
            conditions = []
            values = []

            # 构建查询条件
            for key, value in kwargs.items():
                try:
                    field = Way[key.upper()].value
                    conditions.append(f"{field} = ?")
                    values.append(value)
                except KeyError:
                    raise ValueError(f"无效的查询字段: {key}")

            # 构建SQL查询
            query = "SELECT * FROM Data"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, values)
            return cursor.fetchall()


"""Tester"""
if __name__ == '__main__':
    import random
    from datetime import datetime, timedelta
    from typing import List

    def generate_sample_data(count: int = 100) -> List[dict]:
        """生成随机测试数据"""
        samples = []

        # 定义随机数据池
        ips = [
            "192.168.1.1", "192.168.27.233", "192.168.82.161",
            "192.168.100.54", "192.168.55.89", "192.168.3.201"
        ]
        passwords = [
            "password123", "admin123", "root123",
            "test123", "user123", "system123"
        ]
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0", "2.1.0"]
        locations = ["北京", "上海", "广州", "深圳", "杭州", "成都"]
        usernames = [
            "admin", "root", "test_user",
            "system_user", "guest", "default_user"
        ]
        ways = ["GET", "POST", "PUT", "DELETE"]

        # 设置日期范围
        start_date = datetime(2024, 12, 1)

        for _ in range(count):
            # 随机生成时间
            random_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            sample = {
                "ip": random.choice(ips),
                "password": random.choice(passwords),
                "version": random.choice(versions),
                "session_id": f"sess_{random.randint(10000, 99999)}",
                "location": random.choice(locations),
                "date": random_date.strftime("%Y-%m-%d"),
                "time": random_date.strftime("%H:%M"),  # 使用 HH:MM 格式
                "username": random.choice(usernames),
                "way": random.choice(ways),
                "count": random.randint(1, 100),
                "number": random.randint(1000, 9999)
            }
            samples.append(sample)

        return samples

    def test_database():
        """测试数据库所有功能"""
        db = Database(fix_by_force=True)
        print("开始测试数据库功能...")

        # 生成测试数据
        print("\n1. 生成100条随机测试数据")
        test_data = generate_sample_data(100)
        print(f"生成完成: {len(test_data)} 条数据")
        print("样例数据:", test_data[0])  # 打印第一条数据作为样例

        # 测试插入
        print("\n2. 测试数据插入")
        success_count = 0
        for i, data in enumerate(test_data):
            result = db.insert(**data)
            if isinstance(result, int):
                success_count += 1
            else:
                print(f"插入第 {i + 1} 条数据失败: {result[1]}")  # 打印具体错误信息
                print(f"失败数据: {data}")
                break  # 在第一次失败时停止，以查看具体问题
        print(f"成功插入: {success_count}/100 条数据")

        # 测试删除
        print("\n3. 测试数据删除")
        # 3.1 删除特定IP的记录
        test_ip = test_data[0]["ip"]
        result = db.delete(ip=test_ip)
        if isinstance(result, int):
            print(f"成功删除IP为 {test_ip} 的记录: {result} 条")
        else:
            print(f"删除IP记录失败: {result[1]}")

        # 3.2 删除特定日期和方式的记录
        test_date = test_data[1]["date"]
        test_way = test_data[1]["way"]
        result = db.delete(date=test_date, way=test_way)
        if isinstance(result, int):
            print(f"成功删除日期为 {test_date} 且方式为 {test_way} 的记录: {result} 条")
        else:
            print(f"删除日期和方式记录失败: {result[1]}")

        # 3.3 测试无条件删除（应该失败）
        result = db.delete()
        if not isinstance(result, int):
            print("无条件删除被正确阻止:", result[1])
        else:
            print("警告：无条件删除未被阻止！")

        print("\n测试完成!")

    # 运行测试
    test_database()
