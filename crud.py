from sqlalchemy.orm import Session
from sqlalchemy import and_
from model import User, Friend, ChatParticipant, ChatContent, ChatRoom
from sqlalchemy import desc
from sqlalchemy import func
import logging
from sqlalchemy.orm import joinedload
def db_register_user(db: Session, id, password, name):
    # 이미 존재하는지 확인
    existing_user = db.query(User).filter(User.id == id).first()
    if existing_user:
        return None  # 이미 존재하는 경우 None을 반환하거나 다른 방식으로 처리 가능
    else:
        db_item = User(id=id, password=password, name=name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

def db_add_friend(db: Session, user_id, friend_id):

    existing_friend = db.query(Friend).filter_by(user_id=user_id, friend_id=friend_id).first()

    if existing_friend:
        return None
    # friend_id에 해당하는 친구의 정보 조회
    friend_info = db.query(User).filter_by(id=friend_id).first()

    # friend_info가 존재하고 있다면 Friend 테이블에 추가
    if friend_info:
        friend_name = friend_info.name
        db_item = Friend(user_id=user_id, friend_id=friend_id, friend_name=friend_name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    else:
        return None  # friend_id에 해당하는 사용자가 존재하지 않을 경우 처리 (예: 예외 처리)

def db_get_friends(db: Session, user_id):
    # 주어진 user_id에 대한 친구 목록을 조회
    friends = db.query(Friend).filter_by(user_id=user_id).all()

    return friends


def find_or_create_private_chat_room(current_user: str, target_user: str, db: Session):
    # 현재 아이디와 상대방 아이디로 채팅방을 찾기
    existing_room = (
        db.query(ChatRoom)
        .join(ChatParticipant, ChatParticipant.roomnumber == ChatRoom.index)
        .filter(ChatRoom.roomtype == "single")
        .filter(ChatParticipant.username.in_([current_user, target_user]))
        .group_by(ChatRoom.index)
        .having(func.count(ChatRoom.index) == 2)
        .first()
    )

    if existing_room:
        # 이미 존재하는 방이 있는 경우 해당 방의 index를 반환
        return existing_room.index

    target_user_info = db.query(User).filter_by(id=target_user).first()

    # 새로운 방을 생성하고 참가자를 추가
    new_chat_room = ChatRoom(roomtype="single", roomName=target_user_info.name)
    db.add(new_chat_room)
    db.commit()  # 새로운 방을 데이터베이스에 저장

    # db.commit() 다음에 refresh를 호출
    db.refresh(new_chat_room)

    # 현재 사용자와 상대방을 참가자로 추가
    current_user_participant = ChatParticipant(
        username=current_user, roomnumber=new_chat_room.index
    )
    target_user_participant = ChatParticipant(
        username=target_user, roomnumber=new_chat_room.index
    )

    db.add_all([current_user_participant, target_user_participant])
    db.commit()
    db.refresh(current_user_participant)
    db.refresh(target_user_participant)
    return new_chat_room.index


def get_recent_message_type(db: Session, room_number: int) -> str:
    # 방번호에 해당하는 방의 최근 메시지를 찾습니다.
    recent_message = (
        db.query(ChatContent.contenttype)
        .filter_by(roomnumber=room_number)
        .order_by(desc(ChatContent.create_date))
        .first()
    )

    # 방의 최근 메시지가 존재하는 경우 해당 메시지의 타입을 반환합니다.
    return recent_message.contenttype if recent_message else None

def get_friend_names(db: Session, friend_ids: list):
    friend_names = []

    # 각 친구 ID에 대해 User 테이블을 조회하여 이름을 가져옵니다.
    for friend_id in friend_ids:
        user = db.query(User).filter(User.id == friend_id).first()
        if user:
            friend_names.append(user.name)


    # 가져온 친구 이름들을 쉼표로 구분된 하나의 문자열로 만듭니다.
    friend_names_str = ",".join(friend_names)
    
    return friend_names_str

def get_other_participant_name(db: Session, room_number: int, current_user_id: str) -> str:
    # 현재 사용자를 제외한 다른 참여자의 이름을 가져오기
    other_participant = (
        db.query(ChatParticipant)
        .filter(and_(ChatParticipant.roomnumber == room_number, ChatParticipant.username != current_user_id))
        .first()
    )

    if other_participant:
        # 다시 해당 사용자의 정보를 쿼리하여 이름을 가져오기
        other_user = db.query(User).filter(User.id == other_participant.username).first()

        if other_user:
            return other_user.name
        else:
            return "Unknown"
    else:
        return "Unknown"