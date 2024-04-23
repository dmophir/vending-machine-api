import os
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import JWTError, jwt

from models import TokenData, User
from userdb import UserDBConnector

user_db = UserDBConnector()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

credentials_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail='Could not validate credentials',
	headers={'WWW-Authenticate': 'Bearer'}
)

user_not_found_exception = HTTPException(
	status_code=status.HTTP_404_NOT_FOUND,
	detail='User not found'
)

class AuthProvider:
	ALGORITHM = 'HS256'
	ACCESS_TOKEN_EXPIRE_MINUTES = 10
	REFRESH_TOKEN_EXPIRE_HOURS = 1
	PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

	def __init__(self) -> None:
		self.SECRET_KEY = os.environ['JWT_SECRET']
		if not self.SECRET_KEY:
			raise EnvironmentError("JWT_SECRET environment variable not found")
		
	def verify_password(self, plain_pass, hashed_pass):
		return self.PWD_CONTEXT.verify(plain_pass, hashed_pass)
	
	def get_password_hash(self, password):
		return self.PWD_CONTEXT.hash(password)
	
	def authenticate_user(self, username, plain_pass):
		user = self.get_user(username)
		if not user:
			raise user_not_found_exception
		if not self.verify_password(plain_pass, user['password_hash']):
			raise credentials_exception
		return user
	
	def get_user(self, username):
		user = user_db.query_get(
			'SELECT * FROM user WHERE username = %s',
			[username]
		)
		if not len(user):
			raise user_not_found_exception
		return user[0]
	
	async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
		user = None
		try:
			payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
			username = payload.get('sub')
			if username is None:
				raise credentials_exception
			token_data = TokenData(username=username)
		except JWTError:
			raise credentials_exception
		user = self.get_user(username=token_data.username)
		if user is None:
			raise credentials_exception
		return user
	
	def create_access_token(self, data, expires: timedelta | None = None):
		to_encode = data.copy()
		if expires:
			expiration = datetime.now() + expires
		else:
			expiration = datetime.now() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
		to_encode.update({'exp': expiration})
		encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
		return encoded_jwt
	
	def encode_token(self, username):
		payload = {
			'exp': datetime.now() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
			'iat': datetime.now(),
			'scope': 'access_token',
			'sub': username
		}
		return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
		
	def refresh_token(self, refresh_token):
		try:
			payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=self.ALGORITHM)
			if payload['scope'] == 'refresh_token':
				username = payload['sub']
				new_token = self.encode_token(username)
				return new_token
			raise credentials_exception
		except Exception as e:
			raise credentials_exception
	
	def encode_refresh_token(self, username):
		payload = {
			'exp': datetime.now() + timedelta(hours=self.REFRESH_TOKEN_EXPIRE_HOURS),
			'iat': datetime.now(),
			'scope': 'refresh_token',
			'sub': username
		}
		return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)