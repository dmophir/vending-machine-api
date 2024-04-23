from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import Token, User, ItemID, Item, Coin, Purchase
from security import AuthProvider, credentials_exception, user_db

auth_handler = AuthProvider()

DEPOSIT = {
	'value': int(0)
}

insufficient_funds_exception = HTTPException(
	status_code=status.HTTP_402_PAYMENT_REQUIRED,
	detail='Insufficient funds'
)


app = FastAPI()		

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
	user = auth_handler.authenticate_user(form_data.username, form_data.password)
	if not user:
		raise credentials_exception
	access_token = auth_handler.create_access_token(data={"sub": user['username']})
	return Token(access_token=access_token, token_type="bearer")

@app.get("/items")
async def get_items(item: Item | None = None):
	if item is None:
		items = user_db.query_get(
			'SELECT item.productId, item.price FROM item',
			[]
		)
		return items
	else:
		user_db.query_get(
			'SELECT item.productId, item.price FROM item WHERE item.productId = %s',
			[item.productId]
		)

@app.put("/items")
async def put_item(item: Item, _: Annotated[User, Depends(auth_handler.get_current_user)]):
	row = user_db.query_get(
		'SELECT * FROM item WHERE item.productId = %s',
		[item.productId]
	)
	if len(row):
		rowID = user_db.query_put(
			'UPDATE item SET price = %s WHERE item.productId = %s',
			[item.price, item.productId]
		)
		updatedRow = user_db.query_get(
			'SELECT * FROM item WHERE item.id = %s',
			[rowID]
		)
		return Item(**updatedRow[0])
	else:
		rowID = user_db.query_put(
			'INSERT INTO item (productID, price) VALUES (%s, %s)',
			[item.productId, item.price]
		)
		newRow = user_db.query_get(
			'SELECT * FROM item WHERE item.id = %s',
			[rowID]
		)
		return Item(**newRow[0])

@app.delete("/items")
async def delete_item(item: ItemID, _: Annotated[User, Depends(auth_handler.get_current_user)]):
	rowID = user_db.query_put(
		'DELETE FROM item WHERE item.productId = %s',
		[item.productId]
	)
	return rowID

@app.post("/deposit")
async def insert_coin(coin: Coin):
	DEPOSIT['value'] += coin.value
	return {'deposit': '%.2f' % (float(DEPOSIT['value']) / 100)}

@app.get("/deposit")
async def get_coins():
	return {'deposit': '%.2f' % (float(DEPOSIT['value']) / 100)}

@app.get("/reset")
async def reset_deposit():
	DEPOSIT['value'] = 0

@app.post("/buy")
async def buy_items(order: list[Purchase]):
	wallet = DEPOSIT['value']
	resp = {
		'items': [],
		'change': {
			100: 0,
			50: 0,
			20: 0,
			10: 0,
			5: 0
		}
	}

	for purchase in order:
		item = user_db.query_get(
			'SELECT item.productId, item.price FROM item WHERE item.productId = %s',
			[purchase.productId]
		)[0]
		cost = int(item['price'] * 100) * purchase.quantity
		if cost <= wallet:
			wallet -= cost
			resp['items'].append(purchase)
		else:
			raise insufficient_funds_exception
	
	if wallet:
		for coin in resp['change'].keys():
			if not wallet:
				break
			resp['change'][coin] = wallet // coin
			wallet -= coin * resp['change'][coin]

	DEPOSIT['value'] = 0
	return resp