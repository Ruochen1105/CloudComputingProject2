"""
Manage AWS RDS
"""
import pymysql

import local_config


class db_object():
    def __init__(self):
        self._host = local_config.host
        self._port = local_config.port
        self._user = local_config.user
        self._password = local_config.password
        self._database = local_config.database

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
        print(cur.fetchall())


    def create_one(self, image, longitude, latitude, accident):
        cur = self._connection.cursor()
        cur.execute(f"""
            INSERT INTO accident (image, longitude, latitude, accident) VALUES ({image}, {longitude}, {latitude}, {int(accident)});
        """)


if __name__ == "__main__":
    my_db_object = db_object()
    my_db_object.show_schema()

