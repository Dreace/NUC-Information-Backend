import pymysql

from global_config import mysql_pool


class SQLHelper(object):
    @staticmethod
    def open(cursor):
        pool = mysql_pool
        conn = pool.connection()
        cursor = conn.cursor(cursor=cursor)
        return conn, cursor

    @staticmethod
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def roll_back(conn: pymysql.connections.Connection, cursor: pymysql.cursors.Cursor):
        conn.rollback()
        cursor.close()
        conn.close()

    @classmethod
    def fetch_one(cls, sql: str, args: tuple = (), cursor=pymysql.cursors.DictCursor):
        conn, cursor = cls.open(cursor)
        try:
            cursor.execute(sql, args)
            obj = cursor.fetchone()
            cls.close(conn, cursor)
            return obj  # 这个返回是字典
        except pymysql.DatabaseError as error:
            cls.roll_back(conn, cursor)
            raise error  # 继续向外层抛出异常

    @classmethod
    def fetch_all(cls, sql: str, args: tuple = (), cursor=pymysql.cursors.DictCursor):
        conn, cursor = cls.open(cursor)
        try:
            cursor.execute(sql, args)
            obj = cursor.fetchall()
            cls.close(conn, cursor)
            return obj
        except pymysql.DatabaseError as error:
            cls.roll_back(conn, cursor)
            raise error
