"""
Manage AWS RDS
"""
import os

import pymysql

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class db_object():
    def __init__(self):
        self._host = os.getenv("host")
        self._port = int(os.getenv("port"))
        self._user = os.getenv("user")
        self._password = os.getenv("password")
        self._database = os.getenv("database")

        self._connection = pymysql.Connection(host=self._host, port=self._port, user=self._user, password=self._password, database=self._database)


    def create_db(self):
        cur = self._connection.cursor()
        cur.execute("""
            CREATE TABLE accident (
                image VARCHAR(40),
                longitude FLOAT,
                latitude FLOAT,
                accident BIT
            );
        """)


    def show_schema(self):
        cur = self._connection.cursor()
        cur.execute("DESCRIBE accident;")
        print(cur.fetchall())


    def fetch_all(self):
        cur = self._connection.cursor()
        cur.execute("SELECT * FROM accident;")
        return cur.fetchall()


    def create_one(self, image, longitude, latitude, accident):
        cur = self._connection.cursor()
        cur.execute(f"""
            INSERT INTO accident (image, longitude, latitude, accident) VALUES ('{image}', {longitude}, {latitude}, {accident});
        """)
        self._connection.commit()


if __name__ == "__main__":
    my_db_object = db_object()
    my_db_object.show_schema()
    print(my_db_object.fetch_all())
