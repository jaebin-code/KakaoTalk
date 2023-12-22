from sqlalchemy import Column, Integer, String, Text, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    index = Column(Integer, primary_key=True)
    id = Column(String, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status_msg = Column(Text, nullable=True)
    profile_url = Column(Text, nullable=True)


class Friend(Base):
    __tablename__ = "friends"

    index = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id',ondelete="CASCADE"), nullable=False )
    friend_id = Column(String, nullable=False)
    friend_name = Column(String, nullable=False)

    # User 테이블과의 관계 설정
    user = relationship("User")

class ChatRoom(Base):
    __tablename__ = "chat_room"
    index = Column(Integer, primary_key=True, index=True)
    roomtype = Column(String, index=True)
    roomName = Column(String)
    lastmessage = Column(String)
    lastmessagetime = Column(DateTime)
    

class ChatContent(Base):
    __tablename__ = "chat_content"
    index = Column(Integer, primary_key=True, index=True)
    id = Column(String)
    username = Column(String)
    contents = Column(String)
    contenttype = Column(String)
    create_date = Column(DateTime)
    roomnumber = Column(Integer, ForeignKey("chat_room.index"))

class ChatParticipant(Base):
    __tablename__ = "chat_participant"
    index = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    roomnumber = Column(Integer, ForeignKey("chat_room.index"))