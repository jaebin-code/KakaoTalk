from fastapi import FastAPI, Depends, Request, WebSocket, Response, Form, HTTPException, File, UploadFile, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from sqlalchemy import desc

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from sqlalchemy.orm import Session
from markupsafe import Markup

from crud import db_register_user, db_add_friend,  db_get_friends, find_or_create_private_chat_room,get_recent_message_type,get_friend_names,get_other_participant_name
from model import Base, User, Friend, ChatRoom, ChatContent, ChatParticipant
from database import SessionLocal, engine
from schema import friendSchema, ChatContentInput

from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

class NotAuthenticatedException(Exception):
    pass

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/', use_cookie=True, custom_exception=NotAuthenticatedException)

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager1 = ConnectionManager()

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    # redirect if fail to login
    return RedirectResponse(url='/')

@app.post('/token')
def login(response: Response, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = data.username
    password = data.password

    user = db.query(User).filter(User.id == username).first()

    # Check if the user exists and the password is correct
    if user is None or user.password != password:
        raise InvalidCredentialsException

    # Create an access token with the user's username as the subject
    access_token = manager.create_access_token(data={'sub': username})

    # Set the access token as a cookie in the response
    manager.set_cookie(response, access_token)

    return {'access_token': access_token}

@app.post('/register')
def register_user(response: Response, data: OAuth2PasswordRequestForm = Depends(), name: str = Form(...), db:Session = Depends(get_db)):
    username = data.username
    password = data.password

    user = db_register_user(db,username,password,name)
    if user:
        access_token = manager.create_access_token(
            data={'sub': username}
        )
        manager.set_cookie(response, access_token)
        return "User Created"
    else:
        raise HTTPException(status_code=400, detail="User registration failed. User already exists.")

# FastAPI 애플리케이션에서 등록 엔드포인트 추가
# 페이지 이동 기능
@app.get("/register_page")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/friendPage")
def friendPage(request: Request):
    return templates.TemplateResponse("friendPage.html", {"request": request})

@app.get("/chatListPage")
def chatListPage(request: Request):
    return templates.TemplateResponse("chatListPage.html", {"request": request})

@app.get("/groupPage")
def groupPage(request: Request):
    return templates.TemplateResponse("groupChat.html", {"request": request})


@app.get("/profilePage/{user_id}")
def profile_page(request: Request, user_id, db: Session = Depends(get_db), user=Depends(manager)):
    user_data = db.query(User).filter(User.id == user_id).first()

    if user_data:
        # 필요한 필드들을 가져와서 템플릿에 전달
        profile_image_path = user_data.profile_url or "/images/basicprofileimage.jpg"
        name = user_data.name

        if user_data.status_msg:
            status_msg = user_data.status_msg
        else:
            status_msg = Markup("<br>")

        return templates.TemplateResponse(
            "profilePage.html",
            {"request": request, "user_id": user_id, "profile_image_path": profile_image_path, "name": name, "status_msg": status_msg, "myid": user.id, "user_data": user_data}
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/chatroom/{room_number}")
def profile_page(request: Request, room_number, user=Depends(manager), db: Session = Depends(get_db)):
    
        return templates.TemplateResponse(
            "chatRoom.html",
            {"request": request, "room_number" : room_number, "current_user": user.id}
        )

@app.get("/")
def get_login(request: Request):
    return templates.TemplateResponse("loginPage.html", {"request": request})

@manager.user_loader()
def get_user(username: str, db: Session = None):
    if not db:
        with SessionLocal() as db:
            return db.query(User).filter(User.id == username).first()
    return db.query(User).filter(User.id == username).first()

@app.get("/get_user_info")
def get_user_info(user: User = Depends(manager)):
    return {"username": user.name,"id": user.id}

@app.post("/addFriend")
def addFriend(friendID: str = Form(...),user = Depends(manager), db: Session = Depends(get_db)):
    if(user.id == friendID):
        raise HTTPException(status_code=404, detail="Friend not found")
    result = db_add_friend(db,user.id,friendID)
    if not result:
        raise HTTPException(status_code=404, detail="Friend not found")
    return db_get_friends(db,user.id)

@app.get("/get_user_friends")
def get_user_friends(user = Depends(manager), db: Session = Depends(get_db)):
    friends = db_get_friends(db, user.id)
    if not friends:
        raise HTTPException(status_code=404, detail="User has no friends")
    return friends

@app.post("/update_status")
async def update_status(new_status: str = Form(...), db: Session = Depends(get_db), myUser = Depends(manager)):
    # 데이터베이스에서 해당 사용자 조회
    user = db.query(User).filter(User.id == myUser.id).first()
    if user:
        # 사용자의 상태 메시지 업데이트
        user.status_msg = new_status
        db.commit()
        return {"status": "Success", "message": "Status message updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.post("/update_image")
async def update_image(image: UploadFile = File(...), db: Session = Depends(get_db), myUser = Depends(manager)):
    # 이미지를 저장할 경로 생성
    image_path = f"static/images/{myUser.id}.jpg"
    save_image_path = f"/images/{myUser.id}.jpg"
    # 이미지를 서버에 저장
    with open(image_path, "wb") as image_file:
        image_file.write(image.file.read())

    # 데이터베이스에서 해당 사용자 조회
    user = db.query(User).filter(User.id == myUser.id).first()
    if user:
        # 사용자의 프로필 이미지 경로 업데이트
        user.profile_url = save_image_path
        db.commit()
        return {"status": "Success", "message": "static"+save_image_path}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.post("/update_conversationimage")
async def update_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    photo_count = db.query(ChatContent).filter_by(contenttype='photo').count()

    # 이미지를 저장할 경로 생성
    image_path = f"static/conversationImages/{photo_count+1}.jpg"
    save_image_path = f"/conversationImages/{photo_count+1}.jpg"
    # 이미지를 서버에 저장
    with open(image_path, "wb") as image_file:
        image_file.write(image.file.read())

    return {"status": "Success", "message": "static"+save_image_path}

# 개인톡
@app.post("/join_chat")
async def join_chat(
    target_user: str = Form(...), current_user = Depends(manager), db: Session = Depends(get_db)
):
    room_number = find_or_create_private_chat_room(current_user.id, target_user, db)
    return {"message": "Successfully joined private chat room", "room_number": room_number, "id" : current_user.id}

# 단체톡
@app.post("/create_chat_room")
async def create_chat_room(selected_friends: str = Form(...), db: Session = Depends(get_db), user: User = Depends(manager)):

    friends_id_list = [friend_id for friend_id in selected_friends.split(",")]
    friend_names_str = user.name+","+get_friend_names(db, selected_friends)

    new_chat_room = ChatRoom(roomtype="group", roomName=friend_names_str)
    db.add(new_chat_room)
    db.commit()  # 새로운 방을 데이터베이스에 저장

    friends_id_list.append(user.id)
    # ChatParticipant 생성
    for friend_id in friends_id_list:
        new_participant = ChatParticipant(username=friend_id, roomnumber=new_chat_room.index)
        db.add(new_participant)

    db.commit()

    return {"success": True, "message": "Chat room created successfully", "room_id": new_chat_room.index}





@app.post("/list_join_chat")
async def join_chat( room_number : int = Form(...),
    current_user = Depends(manager), db: Session = Depends(get_db)
):
    return {"message": "Successfully joined private chat room", "room_number": room_number, "id" : current_user.id}

@app.get("/get_chat")
async def get_chat(roomnumber: int, db: Session = Depends(get_db)):
    chat_contents = db.query(ChatContent).filter_by(roomnumber=roomnumber).all()

    # 채팅 내용이 없으면 404 에러 반환
    if not chat_contents:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 채팅 내용을 JSON 형식으로 변환하여 반환
    result = [
        {
            "id": chat.id,
            "contents": chat.contents,
            "create_date": chat.create_date,
            "username": chat.username,
            "contenttype" : chat.contenttype
        }
        for chat in chat_contents
    ]

    return result

@app.post("/posttalk")
async def post_talk(data: ChatContentInput, db: Session = Depends(get_db), user: User = Depends(manager)):
    new_chat = ChatContent(
        id=data.id,
        username=user.name,
        contents=data.contents,
        create_date=data.create_date,
        roomnumber=data.roomnumber,
        contenttype="text"
    )
    db.add(new_chat)
    db.commit()

    # 해당 채팅방의 채팅 내용을 반환합니다.
    roomnumber = data.roomnumber
    chat_room = db.query(ChatRoom).filter_by(index=roomnumber).first()

    if chat_room:
        chat_room.lastmessagetime = data.create_date
        chat_room.lastmessage = data.contents
        db.commit()

    chat_contents = db.query(ChatContent).filter_by(roomnumber=roomnumber).all()

    result = [
        {
            "id": chat.id,
            "contents": chat.contents,
            "create_date": chat.create_date,
            "username": chat.username,
            "contenttype" : chat.contenttype
        }
        for chat in chat_contents
    ]

    return {"success": True, "message": "Chat posted successfully", "talk": result}

@app.post("/postphoto")
async def post_photo(data: ChatContentInput, db: Session = Depends(get_db), user: User = Depends(manager)):
    new_chat = ChatContent(
        id=data.id,
        username=user.name,
        contents=data.contents,
        create_date=data.create_date,
        roomnumber=data.roomnumber,
        contenttype="photo"
    )
    db.add(new_chat)
    db.commit()

    # 해당 채팅방의 채팅 내용을 반환합니다.
    roomnumber = data.roomnumber
    chat_room = db.query(ChatRoom).filter_by(index=roomnumber).first()

    if chat_room:
        chat_room.lastmessagetime = data.create_date
        chat_room.lastmessage = data.contents
        db.commit()

    chat_contents = db.query(ChatContent).filter_by(roomnumber=roomnumber).all()

    result = [
        {
            "id": chat.id,
            "contents": chat.contents,
            "create_date": chat.create_date,
            "username": chat.username,
            "contenttype" : chat.contenttype
        }
        for chat in chat_contents
    ]

    return {"success": True, "message": "Chat posted successfully", "talk": result}

@app.get("/get_chat_lists")
async def get_chat_lists(user: User = Depends(manager), db: Session = Depends(get_db)):
    # 현재 사용자와 관련된 채팅 방을 가져오기
    chat_rooms = (
        db.query(ChatRoom)
        .join(ChatParticipant, ChatRoom.index == ChatParticipant.roomnumber)
        .filter(ChatParticipant.username == user.id)
        .order_by(desc(ChatRoom.lastmessagetime))
        .all()
    )

    # 가져온 채팅 방 정보를 반환
    result = [
        {
            "name" : chat.roomName if chat.roomtype == "group" else get_other_participant_name(db, chat.index, user.id),
            "lastmessage": chat.lastmessage,
            "roomnumber" : chat.index,
            "message_type": get_recent_message_type(db, chat.index)
        }
        for chat in chat_rooms
    ]

    return result










# webSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager1.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager1.broadcast(f"{data}")
    except Exception as e:
        pass
    finally:
        await manager1.disconnect(websocket)

@app.get("/client")
async def client(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
                                      
def run():
    import uvicorn
    uvicorn.run(app)

if __name__ == "__main__":
    run()            