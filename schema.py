from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class userSchema(BaseModel):

    index: Optional[int]
    id : str
    password : str
    name : str
    status_msg : Optional[str]
    profile_url : Optional[str]

    class Config:
        orm_mode = True

class friendSchema(BaseModel):

    index: Optional[int]
    user_id : str
    friend_id : str
    friend_name : str

    class Config:
        orm_mode = True


class ChatContentInput(BaseModel):
    id: str
    username: str
    contents: str
    create_date: datetime  # 이 부분이 datetime으로 변환됨
    roomnumber: int
    contenttype: str = None
