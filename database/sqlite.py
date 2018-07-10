import sqlite3
import time


class Database:
    def __init__(self, database):
        try:
            self.db_conn = sqlite3.connect(database)
            self.cursor = self.db_conn.cursor()
        except Exception as e:
            print("Failed to connect to DB " + database + ":", e)
            raise

    def createTable(self, table_name, columns):
        """
        Create database table
        :param table_name: name of the table
        :param column_list: list of columns
        :return:
        """
        query = "CREATE TABLE IF NOT EXISTS " + table_name + " (" + columns + ")"
        try:
            self.cursor.execute(query)
        except Exception as e:
            print("Cannot create table: ", e)
            raise


    def insertRecord(self, table_name, data):
        """
        Insert record if not exists, return new records
        :param table_name: table name
        :param data: data in column lists
        :return:
        """
        columns = ', '.join(data.keys())
        placeholders = ':' + ', :'.join(data.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, columns, placeholders)
        try:
            self.cursor.execute(query, data)
            self.db_conn.commit()
        except Exception as e:
            print("Insert into DB failed: ", e)
            raise

    def getLastInserted(self, table_name):
        """
        Gets last inserted row from table
        :param table_name: table name
        :return:
        """
        query = "SELECT * FROM %s WHERE ROWID = (SELECT MAX(ROWID) FROM %s)" % (table_name, table_name)
        try:
            query_result = self.cursor.execute(query)
            result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in query_result]
        except Exception as e:
            print("Can not get last inserted value: ", e)
            raise
        return result[0]

    def getDataNHoursBack(self, table_name, number_of_hours):
        """
        Get data N hours back from a given table
        :param table_name: name of the table
               number_of_daysL: number of days back
        :return:
        """
        since = int(self.getNow() - number_of_hours * 60 * 60)

        query = "SELECT * FROM %s WHERE timestamp > %s" % (table_name, str(since))
        try:
            query_result = self.cursor.execute(query)
            result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in query_result]
        except Exception as e:
            print("Failed to fetch the data: ", e)
            raise

        return result

    def getAllData(self, table_name):
        """
        Gets last inserted row from table
        :param table_name: table name
        :return:
        """
        query = "SELECT * FROM %s" % (table_name)
        try:
            query_result = self.cursor.execute(query)
            result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in query_result]
        except Exception as e:
            print("Can not get last inserted value: ", e)
            raise
        return result

    def getNow(self):
        """
        Returns now in unix timestamp
        :return:
        """
        now = time.time()
        return now

    def closeConnection(self):
        self.db_conn.close()
