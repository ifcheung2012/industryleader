# from uvicorn import run
# from fastapi import FastAPI,Depends
# app = FastAPI()

# @app.get('/')
# async def read_root():
#     return {"hello":"world"}

# if __name__ == "__main__":
#     run(app,host="0.0.0.0",port = 5555)

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name = 'yo yo'
    birth: Optional[datetime] = None
    friends: List[int] = []


external_data = {
    'id': '123',
    'birth': '2019-06-01 12:22',
    'friends': [1, 2, '3'],
}
user = User(**external_data)
print(user.dict())  # dict() 函数将对象转化成字典
