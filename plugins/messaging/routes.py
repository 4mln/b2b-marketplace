"""
Messaging and Chat System API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from app.db.session import get_session, get_db_sync
from plugins.auth.routes import get_current_user
from plugins.auth.models import User
from . import crud, schemas
from .models import ChatRoom, Message, ChatParticipant

router = APIRouter(prefix="/messaging", tags=["messaging"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def send_to_chat_room(self, message: str, chat_room_id: int, exclude_user: int = None):
        # Get all participants in the chat room
        # This would need to be implemented with database access
        pass

manager = ConnectionManager()


# Chat Room Routes
@router.post("/chats", response_model=schemas.ChatRoomOut)
async def create_chat_room(
    chat_data: schemas.ChatRoomCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Create a new chat room"""
    if current_user.id not in chat_data.participant_ids:
        chat_data.participant_ids.append(current_user.id)
    
    chat_room = await crud.create_chat_room(db, chat_data, current_user.id)
    
    # Convert to response model
    participants = await crud.get_participants(db, chat_room.id)
    return schemas.ChatRoomOut(
        id=chat_room.id,
        name=chat_room.name,
        chat_type=chat_room.chat_type,
        created_by=chat_room.created_by,
        created_at=chat_room.created_at,
        updated_at=chat_room.updated_at,
        is_active=chat_room.is_active,
        participant_count=len(participants),
        last_message=None,
        unread_count=0
    )


@router.get("/chats", response_model=schemas.ChatListResponse)
async def get_user_chats(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get all chat rooms for the current user"""
    chats = await crud.get_user_chats(db, current_user.id, skip, limit)
    
    chat_responses = []
    for chat in chats:
        participants = await crud.get_participants(db, chat.id)
        unread_count = await crud.get_unread_count(db, chat.id, current_user.id)
        
        # Get last message
        last_message = None
        if chat.messages:
            last_msg = chat.messages[0]  # Already ordered by desc
            last_message = {
                "id": last_msg.id,
                "content": last_msg.content,
                "sender_id": last_msg.sender_id,
                "created_at": last_msg.created_at
            }
        
        chat_responses.append(schemas.ChatRoomOut(
            id=chat.id,
            name=chat.name,
            chat_type=chat.chat_type,
            created_by=chat.created_by,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_active=chat.is_active,
            participant_count=len(participants),
            last_message=last_message,
            unread_count=unread_count
        ))
    
    return schemas.ChatListResponse(
        chats=chat_responses,
        total=len(chat_responses),
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/chats/{chat_room_id}", response_model=schemas.ChatRoomOut)
async def get_chat_room(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get a specific chat room"""
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, chat_room.id)
    unread_count = await crud.get_unread_count(db, chat_room.id, current_user.id)
    
    return schemas.ChatRoomOut(
        id=chat_room.id,
        name=chat_room.name,
        chat_type=chat_room.chat_type,
        created_by=chat_room.created_by,
        created_at=chat_room.created_at,
        updated_at=chat_room.updated_at,
        is_active=chat_room.is_active,
        participant_count=len(participants),
        last_message=None,
        unread_count=unread_count
    )


@router.patch("/chats/{chat_room_id}", response_model=schemas.ChatRoomOut)
async def update_chat_room(
    chat_room_id: int,
    update_data: schemas.ChatRoomUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Update chat room details"""
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    # Check if user is admin for group chats
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can update group chats")
    
    updated_chat = await crud.update_chat_room(db, chat_room_id, update_data.dict(exclude_unset=True))
    if not updated_chat:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, updated_chat.id)
    unread_count = await crud.get_unread_count(db, updated_chat.id, current_user.id)
    
    return schemas.ChatRoomOut(
        id=updated_chat.id,
        name=updated_chat.name,
        chat_type=updated_chat.chat_type,
        created_by=updated_chat.created_by,
        created_at=updated_chat.created_at,
        updated_at=updated_chat.updated_at,
        is_active=updated_chat.is_active,
        participant_count=len(participants),
        last_message=None,
        unread_count=unread_count
    )


# Message Routes
@router.post("/chats/{chat_room_id}/messages", response_model=schemas.MessageOut)
async def send_message(
    chat_room_id: int,
    message_data: schemas.MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Send a message to a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    message_data.chat_room_id = chat_room_id
    message = await crud.create_message(db, message_data, current_user.id)
    
    # Convert to response model
    return schemas.MessageOut(
        id=message.id,
        chat_room_id=message.chat_room_id,
        sender_id=message.sender_id,
        content=message.content,
        message_type=message.message_type,
        metadata=message.metadata,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        sender_name=current_user.business_name or current_user.email,
        sender_avatar=current_user.business_photo,
        read_by=[]
    )


@router.get("/chats/{chat_room_id}/messages", response_model=schemas.MessageListResponse)
async def get_messages(
    chat_room_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get messages from a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    messages = await crud.get_messages(db, chat_room_id, current_user.id, skip, limit)
    
    message_responses = []
    for message in messages:
        # Get read status
        read_by = []
        for read_status in message.read_status:
            read_by.append(read_status.user_id)
        
        message_responses.append(schemas.MessageOut(
            id=message.id,
            chat_room_id=message.chat_room_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            metadata=message.metadata,
            reply_to_id=message.reply_to_id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            sender_name=message.sender.business_name or message.sender.email,
            sender_avatar=message.sender.business_photo,
            read_by=read_by
        ))
    
    return schemas.MessageListResponse(
        messages=message_responses,
        total=len(message_responses),
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(message_responses) == limit
    )


@router.put("/messages/{message_id}", response_model=schemas.MessageOut)
async def update_message(
    message_id: int,
    update_data: schemas.MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Update a message"""
    message = await crud.update_message(db, message_id, current_user.id, update_data.content)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    return schemas.MessageOut(
        id=message.id,
        chat_room_id=message.chat_room_id,
        sender_id=message.sender_id,
        content=message.content,
        message_type=message.message_type,
        metadata=message.metadata,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        sender_name=current_user.business_name or current_user.email,
        sender_avatar=current_user.business_photo,
        read_by=[]
    )


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Delete a message"""
    success = await crud.delete_message(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    return {"message": "Message deleted successfully"}


@router.post("/chats/{chat_room_id}/read")
async def mark_chat_read(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Mark all messages in a chat as read"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    await crud.mark_chat_read(db, chat_room_id, current_user.id)
    return {"message": "Chat marked as read"}


# Participant Routes
@router.get("/chats/{chat_room_id}/participants", response_model=schemas.ParticipantListResponse)
async def get_participants(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get all participants in a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, chat_room_id)
    
    participant_responses = []
    for participant in participants:
        participant_responses.append(schemas.ChatParticipantOut(
            id=participant.id,
            chat_room_id=participant.chat_room_id,
            user_id=participant.user_id,
            is_admin=participant.is_admin,
            joined_at=participant.joined_at,
            left_at=participant.left_at,
            last_read_at=participant.last_read_at,
            user_name=participant.user.business_name or participant.user.email,
            user_avatar=participant.user.business_photo,
            user_online=False  # TODO: Implement online status
        ))
    
    return schemas.ParticipantListResponse(
        participants=participant_responses,
        total=len(participant_responses)
    )


@router.post("/chats/{chat_room_id}/participants")
async def add_participant(
    chat_room_id: int,
    participant_data: schemas.ChatParticipantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Add a participant to a chat room"""
    # Verify user is admin for group chats
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can add participants")
    
    new_participant = await crud.add_participant(
        db, chat_room_id, participant_data.user_id, participant_data.is_admin
    )
    
    return {"message": "Participant added successfully", "participant_id": new_participant.id}


@router.delete("/chats/{chat_room_id}/participants/{user_id}")
async def remove_participant(
    chat_room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Remove a participant from a chat room"""
    # Verify user is admin or removing themselves
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if user_id != current_user.id:
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can remove participants")
    
    success = await crud.remove_participant(db, chat_room_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return {"message": "Participant removed successfully"}


# Invitation Routes
@router.post("/chats/{chat_room_id}/invitations")
async def create_invitation(
    chat_room_id: int,
    invitation_data: schemas.ChatInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Create an invitation to join a chat room"""
    # Verify user is admin for group chats
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can create invitations")
    
    invitation = await crud.create_invitation(
        db, chat_room_id, current_user.id, invitation_data.invited_user_id
    )
    
    return {"message": "Invitation created successfully", "invitation_id": invitation.id}


@router.get("/invitations", response_model=schemas.InvitationListResponse)
async def get_user_invitations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get invitations for the current user"""
    invitations = await crud.get_user_invitations(db, current_user.id, skip, limit)
    
    invitation_responses = []
    for invitation in invitations:
        invitation_responses.append(schemas.ChatInvitationOut(
            id=invitation.id,
            chat_room_id=invitation.chat_room_id,
            invited_by=invitation.invited_by,
            invited_user_id=invitation.invited_user_id,
            status=invitation.status,
            created_at=invitation.created_at,
            responded_at=invitation.responded_at,
            chat_room_name=invitation.chat_room.name or f"Chat {invitation.chat_room.id}",
            inviter_name=invitation.inviter.business_name or invitation.inviter.email,
            invited_user_name=current_user.business_name or current_user.email
        ))
    
    return schemas.InvitationListResponse(
        invitations=invitation_responses,
        total=len(invitation_responses),
        page=skip // limit + 1,
        page_size=limit
    )


@router.put("/invitations/{invitation_id}")
async def respond_to_invitation(
    invitation_id: int,
    response_data: schemas.ChatInvitationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Respond to a chat invitation"""
    invitation = await crud.respond_to_invitation(
        db, invitation_id, current_user.id, response_data.status
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    return {"message": f"Invitation {response_data.status} successfully"}


# WebSocket Routes
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            # This would need to be implemented based on your requirements
            await manager.send_personal_message(f"You wrote: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)



@router.get("/rooms", response_model=List[schemas.ChatRoomWithParticipants])
async def get_user_chat_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get all chat rooms for the current user"""
    chats = await crud.get_user_chats(db, current_user.id, skip, limit)
    
    chat_responses = []
    for chat in chats:
        participants = await crud.get_participants(db, chat.id)
        unread_count = await crud.get_unread_count(db, chat.id, current_user.id)
        
        # Get last message
        last_message = None
        if chat.messages:
            last_msg = chat.messages[0]  # Already ordered by desc
            last_message = {
                "id": last_msg.id,
                "content": last_msg.content,
                "sender_id": last_msg.sender_id,
                "created_at": last_msg.created_at
            }
        
        chat_responses.append(schemas.ChatRoomOut(
            id=chat.id,
            name=chat.name,
            chat_type=chat.chat_type,
            created_by=chat.created_by,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_active=chat.is_active,
            participant_count=len(participants),
            last_message=last_message,
            unread_count=unread_count
        ))
    
    return schemas.ChatListResponse(
        chats=chat_responses,
        total=len(chat_responses),
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/rooms/{room_id}", response_model=schemas.ChatRoomWithParticipants)
async def get_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get a specific chat room"""
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, chat_room.id)
    unread_count = await crud.get_unread_count(db, chat_room.id, current_user.id)
    
    return schemas.ChatRoomOut(
        id=chat_room.id,
        name=chat_room.name,
        chat_type=chat_room.chat_type,
        created_by=chat_room.created_by,
        created_at=chat_room.created_at,
        updated_at=chat_room.updated_at,
        is_active=chat_room.is_active,
        participant_count=len(participants),
        last_message=None,
        unread_count=unread_count
    )


@router.put("/rooms/{room_id}", response_model=schemas.ChatRoomWithParticipants)
async def update_chat_room(
    room_id: int,
    chat_data: schemas.ChatRoomUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Update chat room details"""
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    # Check if user is admin for group chats
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can update group chats")
    
    updated_chat = await crud.update_chat_room(db, chat_room_id, update_data.dict(exclude_unset=True))
    if not updated_chat:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, updated_chat.id)
    unread_count = await crud.get_unread_count(db, updated_chat.id, current_user.id)
    
    return schemas.ChatRoomOut(
        id=updated_chat.id,
        name=updated_chat.name,
        chat_type=updated_chat.chat_type,
        created_by=updated_chat.created_by,
        created_at=updated_chat.created_at,
        updated_at=updated_chat.updated_at,
        is_active=updated_chat.is_active,
        participant_count=len(participants),
        last_message=None,
        unread_count=unread_count
    )


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Delete a chat room"""
    success = await crud.delete_chat_room(db, room_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    return {"message": "Chat deleted successfully"}


@router.post("/rooms/{room_id}/participants", response_model=schemas.ChatParticipantResponse)
async def add_participant_to_room(
    room_id: int,
    participant_data: schemas.ChatParticipantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Add a participant to a chat room"""
    # Verify user is admin for group chats
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can add participants")
    
    new_participant = await crud.add_participant(
        db, chat_room_id, participant_data.user_id, participant_data.is_admin
    )
    
    return {"message": "Participant added successfully", "participant_id": new_participant.id}


@router.delete("/rooms/{room_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant_from_room(
    room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Remove a participant from a chat room"""
    # Verify user is admin or removing themselves
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if user_id != current_user.id:
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can remove participants")
    
    success = await crud.remove_participant(db, chat_room_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return {"message": "Participant removed successfully"}


@router.get("/rooms/{room_id}/messages", response_model=List[schemas.MessageResponse])
async def get_chat_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get messages from a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    messages = await crud.get_messages(db, chat_room_id, current_user.id, skip, limit)
    
    message_responses = []
    for message in messages:
        # Get read status
        read_by = []
        for read_status in message.read_status:
            read_by.append(read_status.user_id)
        
        message_responses.append(schemas.MessageOut(
            id=message.id,
            chat_room_id=message.chat_room_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            metadata=message.metadata,
            reply_to_id=message.reply_to_id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            sender_name=message.sender.business_name or message.sender.email,
            sender_avatar=message.sender.business_photo,
            read_by=read_by
        ))
    
    return schemas.MessageListResponse(
        messages=message_responses,
        total=len(message_responses),
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(message_responses) == limit
    )


@router.post("/rooms/{room_id}/messages", response_model=schemas.MessageResponse)
async def create_message(
    room_id: int,
    message: schemas.MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Send a message to a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    message_data.chat_room_id = chat_room_id
    message = await crud.create_message(db, message_data, current_user.id)
    
    # Convert to response model
    return schemas.MessageOut(
        id=message.id,
        chat_room_id=message.chat_room_id,
        sender_id=message.sender_id,
        content=message.content,
        message_type=message.message_type,
        metadata=message.metadata,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        sender_name=current_user.business_name or current_user.email,
        sender_avatar=current_user.business_photo,
        read_by=[]
    )


@router.put("/messages/{message_id}", response_model=schemas.MessageResponse)
async def update_message(
    message_id: int,
    message_data: schemas.MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Update a message"""
    message = await crud.update_message(db, message_id, current_user.id, update_data.content)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    return schemas.MessageOut(
        id=message.id,
        chat_room_id=message.chat_room_id,
        sender_id=message.sender_id,
        content=message.content,
        message_type=message.message_type,
        metadata=message.metadata,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        sender_name=current_user.business_name or current_user.email,
        sender_avatar=current_user.business_photo,
        read_by=[]
    )


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Delete a message"""
    success = await crud.delete_message(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    return {"message": "Message deleted successfully"}


@router.post("/chats/{chat_room_id}/read")
async def mark_chat_read(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Mark all messages in a chat as read"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    await crud.mark_chat_read(db, chat_room_id, current_user.id)
    return {"message": "Chat marked as read"}


# Participant Routes
@router.get("/chats/{chat_room_id}/participants", response_model=schemas.ParticipantListResponse)
async def get_participants(
    chat_room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get all participants in a chat room"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    participants = await crud.get_participants(db, chat_room_id)
    
    participant_responses = []
    for participant in participants:
        participant_responses.append(schemas.ChatParticipantOut(
            id=participant.id,
            chat_room_id=participant.chat_room_id,
            user_id=participant.user_id,
            is_admin=participant.is_admin,
            joined_at=participant.joined_at,
            left_at=participant.left_at,
            last_read_at=participant.last_read_at,
            user_name=participant.user.business_name or participant.user.email,
            user_avatar=participant.user.business_photo,
            user_online=False  # TODO: Implement online status
        ))
    
    return schemas.ParticipantListResponse(
        participants=participant_responses,
        total=len(participant_responses)
    )


@router.post("/chats/{chat_room_id}/participants")
async def add_participant(
    chat_room_id: int,
    participant_data: schemas.ChatParticipantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Add a participant to a chat room"""
    # Verify user is admin for group chats
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can add participants")
    
    new_participant = await crud.add_participant(
        db, chat_room_id, participant_data.user_id, participant_data.is_admin
    )
    
    return {"message": "Participant added successfully", "participant_id": new_participant.id}


@router.delete("/chats/{chat_room_id}/participants/{user_id}")
async def remove_participant(
    chat_room_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Remove a participant from a chat room"""
    # Verify user is admin or removing themselves
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if user_id != current_user.id:
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can remove participants")
    
    success = await crud.remove_participant(db, chat_room_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return {"message": "Participant removed successfully"}


# Invitation Routes
@router.post("/chats/{chat_room_id}/invitations")
async def create_invitation(
    chat_room_id: int,
    invitation_data: schemas.ChatInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Create an invitation to join a chat room"""
    # Verify user is admin for group chats
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if chat_room.chat_type == "group":
        participant = db.query(ChatParticipant).filter(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        ).first()
        if not participant:
            raise HTTPException(status_code=403, detail="Only admins can create invitations")
    
    invitation = await crud.create_invitation(
        db, chat_room_id, current_user.id, invitation_data.invited_user_id
    )
    
    return {"message": "Invitation created successfully", "invitation_id": invitation.id}


@router.get("/invitations", response_model=schemas.InvitationListResponse)
async def get_user_invitations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get invitations for the current user"""
    invitations = await crud.get_user_invitations(db, current_user.id, skip, limit)
    
    invitation_responses = []
    for invitation in invitations:
        invitation_responses.append(schemas.ChatInvitationOut(
            id=invitation.id,
            chat_room_id=invitation.chat_room_id,
            invited_by=invitation.invited_by,
            invited_user_id=invitation.invited_user_id,
            status=invitation.status,
            created_at=invitation.created_at,
            responded_at=invitation.responded_at,
            chat_room_name=invitation.chat_room.name or f"Chat {invitation.chat_room.id}",
            inviter_name=invitation.inviter.business_name or invitation.inviter.email,
            invited_user_name=current_user.business_name or current_user.email
        ))
    
    return schemas.InvitationListResponse(
        invitations=invitation_responses,
        total=len(invitation_responses),
        page=skip // limit + 1,
        page_size=limit
    )


@router.put("/invitations/{invitation_id}")
async def respond_to_invitation(
    invitation_id: int,
    response_data: schemas.ChatInvitationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Respond to a chat invitation"""
    invitation = await crud.respond_to_invitation(
        db, invitation_id, current_user.id, response_data.status
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    return {"message": f"Invitation {response_data.status} successfully"}


# WebSocket Routes
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            # This would need to be implemented based on your requirements
            await manager.send_personal_message(f"You wrote: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)



@router.get("/unread", response_model=schemas.UnreadMessagesResponse)
async def get_unread_message_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Get all chat rooms for the current user"""
    chats = await crud.get_user_chats(db, current_user.id, skip, limit)
    
    chat_responses = []
    for chat in chats:
        participants = await crud.get_participants(db, chat.id)
        unread_count = await crud.get_unread_count(db, chat.id, current_user.id)
        
        # Get last message
        last_message = None
        if chat.messages:
            last_msg = chat.messages[0]  # Already ordered by desc
            last_message = {
                "id": last_msg.id,
                "content": last_msg.content,
                "sender_id": last_msg.sender_id,
                "created_at": last_msg.created_at
            }
        
        chat_responses.append(schemas.ChatRoomOut(
            id=chat.id,
            name=chat.name,
            chat_type=chat.chat_type,
            created_by=chat.created_by,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_active=chat.is_active,
            participant_count=len(participants),
            last_message=last_message,
            unread_count=unread_count
        ))
    
    return schemas.ChatListResponse(
        chats=chat_responses,
        total=len(chat_responses),
        page=skip // limit + 1,
        page_size=limit
    )


@router.post("/messages/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Mark all messages in a chat as read"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    await crud.mark_chat_read(db, chat_room_id, current_user.id)
    return {"message": "Chat marked as read"}


@router.post("/rooms/{room_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_room_messages_as_read(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    """Mark all messages in a chat as read"""
    # Verify user is participant
    chat_room = await crud.get_chat_room(db, chat_room_id, current_user.id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    await crud.mark_chat_read(db, chat_room_id, current_user.id)
    return {"message": "Chat marked as read"}


