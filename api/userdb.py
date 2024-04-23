import os
import pymysql
from pymysql import converters
from pymysql.cursors import DictCursor
from fastapi import HTTPException, status

class UserDBConnector:
	def __init__(self) -> None:
		self.host		= os.environ["DB_HOST"]
		self.user		= os.environ["DB_USER"]
		self.password	= os.environ["DB_PASS"]
		self.database	= os.environ["DB_NAME"]
		self.port		= int(os.environ["DB_PORT"])
		self.conversions = converters.conversions
		self.conversions[pymysql.FIELD_TYPE.BIT] = (
			lambda x: False if x == b'\x00' else True
		)

	def get_connection(self):
		connection = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.database,
			cursorclass=DictCursor,
			conv=self.conversions
		)
		return connection
	
	def query_get(self, sql, param):
		try:
			connection = self.get_connection()
			with connection:
				with connection.cursor() as cursor:
					cursor.execute(sql, param)
					return cursor.fetchall()
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Database error: " + str(e)
			)
	
	def query_put(self, sql, param):
		try:
			connection = self.get_connection()
			with connection:
				with connection.cursor() as cursor:
					cursor.execute(sql, param)
					connection.commit()
					return cursor.lastrowid
		except Exception as e:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Database error: " + str(e)
			)