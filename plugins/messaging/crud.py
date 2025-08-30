"""
Messaging and Chat System CRUD Operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import (
    ChatRoom, ChatParticipant, Message, MessageReadStatus, 
    ChatInvitation
)
from .schemas import ChatRoomCreate, MessageCreate, ChatParticipantCreate


# Chat Room CRUD
async def create_chat_room(db: Session, chat_data: ChatRoomCreate, creator_id: int) -> ChatRoom:
    """Create a new chat room with participants"""
    # Create chat room
    chat_room = ChatRoom(
        name=chat_data.name,
        chat_type=chat_data.chat_type,
        created_by=creator_id
    )
    db.add(chat_room)
    db.flush()  # Get the ID
    
    # Add participants
    participants = []
    for user_id in chat_data.participant_ids:
        if user_id != creator_id:  # Don't add creator twice
            participant = ChatParticipant(
                chat_room_id=chat_room.id,
                user_id=user_id,
                is_admin=chat_data.chat_type == "group" and user_id == creator_id
            )
            participants.append(participant)
    
    # Add creator as participant
    creator_participant = ChatParticipant(
        chat_room_id=chat_room.id,
        user_id=creator_id,
        is_admin=True
    )
    participants.append(creator_participant)
    
    db.add_all(participants)
    db.commit()
    db.refresh(chat_room)
    return chat_room


async def get_chat_room(db: Session, chat_room_id: int, user_id: int) -> Optional[ChatRoom]:
    """Get chat room if user is a participant"""
    return db.query(ChatRoom).join(ChatParticipant).filter(
        and_(
            ChatRoom.id == chat_room_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.left_at.is_(None)
        )
    ).first()


async def get_user_chats(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatRoom]:
    """Get all chat rooms for a user"""
    return db.query(ChatRoom).join(ChatParticipant).filter(
        and_(
            ChatParticipant.user_id == user_id,
            ChatParticipant.left_at.is_(None),
            ChatRoom.is_active == True
        )
    ).options(
        joinedload(ChatRoom.participants).joinedload(ChatParticipant.user),
        joinedload(ChatRoom.messages).joinedload(Message.sender)
    ).order_by(desc(ChatRoom.updated_at)).offset(skip).limit(limit).all()


async def update_chat_room(db: Session, chat_room_id: int, update_data: Dict[str, Any]) -> Optional[ChatRoom]:
    """Update chat room details"""
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first()
    if chat_room:
        for field, value in update_data.items():
            if hasattr(chat_room, field):
                setattr(chat_room, field, value)
        chat_room.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(chat_room)
    return chat_room


# Message CRUD
async def create_message(db: Session, message_data: MessageCreate, sender_id: int) -> Message:
    """Create a new message"""
    message = Message(
        chat_room_id=message_data.chat_room_id,
        sender_id=sender_id,
        content=message_data.content,
        message_type=message_data.message_type,
        metadata=message_data.metadata,
        reply_to_id=message_data.reply_to_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update chat room's updated_at
    chat_room = db.query(ChatRoom).filter(ChatRoom.id == message_data.chat_room_id).first()
    if chat_room:
        chat_room.updated_at = datetime.utcnow()
        db.commit()
    
    return message


async def get_messages(db: Session, chat_room_id: int, user_id: int, 
                      skip: int = 0, limit: int = 50) -> List[Message]:
    """Get messages for a chat room"""
    # Verify user is participant
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.left_at.is_(None)
        )
    ).first()
    
    if not participant:
        return []
    
    return db.query(Message).filter(
        and_(
            Message.chat_room_id == chat_room_id,
            Message.is_deleted == False
        )
    ).options(
        joinedload(Message.sender),
        joinedload(Message.read_status)
    ).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()


async def update_message(db: Session, message_id: int, sender_id: int, 
                        content: str) -> Optional[Message]:
    """Update a message"""
    message = db.query(Message).filter(
        and_(
            Message.id == message_id,
            Message.sender_id == sender_id,
            Message.is_deleted == False
        )
    ).first()
    
    if message:
        message.content = content
        message.is_edited = True
        message.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
    
    return message


async def delete_message(db: Session, message_id: int, user_id: int) -> bool:
    """Soft delete a message"""
    message = db.query(Message).filter(
        and_(
            Message.id == message_id,
            Message.sender_id == user_id,
            Message.is_deleted == False
        )
    ).first()
    
    if message:
        message.is_deleted = True
        message.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


async def mark_message_read(db: Session, message_id: int, user_id: int) -> bool:
    """Mark a message as read"""
    # Check if already marked as read
    existing = db.query(MessageReadStatus).filter(
        and_(
            MessageReadStatus.message_id == message_id,
            MessageReadStatus.user_id == user_id
        )
    ).first()
    
    if not existing:
        read_status = MessageReadStatus(
            message_id=message_id,
            user_id=user_id
        )
        db.add(read_status)
        db.commit()
        return True
    return False


async def mark_chat_read(db: Session, chat_room_id: int, user_id: int) -> bool:
    """Mark all messages in a chat as read"""
    # Get unread messages
    unread_messages = db.query(Message).filter(
        and_(
            Message.chat_room_id == chat_room_id,
            Message.sender_id != user_id,
            Message.is_deleted == False
        )
    ).all()
    
    # Mark each as read
    for message in unread_messages:
        await mark_message_read(db, message.id, user_id)
    
    # Update participant's last_read_at
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == user_id
        )
    ).first()
    
    if participant:
        participant.last_read_at = datetime.utcnow()
        db.commit()
    
    return True


# Participant CRUD
async def add_participant(db: Session, chat_room_id: int, user_id: int, 
                         is_admin: bool = False) -> ChatParticipant:
    """Add a participant to a chat room"""
    # Check if already a participant
    existing = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == user_id
        )
    ).first()
    
    if existing:
        if existing.left_at:
            existing.left_at = None
            existing.is_admin = is_admin
            db.commit()
            db.refresh(existing)
            return existing
        return existing
    
    participant = ChatParticipant(
        chat_room_id=chat_room_id,
        user_id=user_id,
        is_admin=is_admin
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


async def remove_participant(db: Session, chat_room_id: int, user_id: int) -> bool:
    """Remove a participant from a chat room"""
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.left_at.is_(None)
        )
    ).first()
    
    if participant:
        participant.left_at = datetime.utcnow()
        db.commit()
        return True
    return False


async def get_participants(db: Session, chat_room_id: int) -> List[ChatParticipant]:
    """Get all participants in a chat room"""
    return db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.left_at.is_(None)
        )
    ).options(
        joinedload(ChatParticipant.user)
    ).all()


# Invitation CRUD
async def create_invitation(db: Session, chat_room_id: int, 
                           invited_by: int, invited_user_id: int) -> ChatInvitation:
    """Create a chat invitation"""
    invitation = ChatInvitation(
        chat_room_id=chat_room_id,
        invited_by=invited_by,
        invited_user_id=invited_user_id
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


async def respond_to_invitation(db: Session, invitation_id: int, 
                               user_id: int, status: str) -> Optional[ChatInvitation]:
    """Respond to a chat invitation"""
    invitation = db.query(ChatInvitation).filter(
        and_(
            ChatInvitation.id == invitation_id,
            ChatInvitation.invited_user_id == user_id,
            ChatInvitation.status == "pending"
        )
    ).first()
    
    if invitation:
        invitation.status = status
        invitation.responded_at = datetime.utcnow()
        
        if status == "accepted":
            # Add user to chat room
            await add_participant(db, invitation.chat_room_id, user_id)
        
        db.commit()
        db.refresh(invitation)
        return invitation
    return None


async def get_user_invitations(db: Session, user_id: int, 
                              skip: int = 0, limit: int = 50) -> List[ChatInvitation]:
    """Get invitations for a user"""
    return db.query(ChatInvitation).filter(
        and_(
            ChatInvitation.invited_user_id == user_id,
            ChatInvitation.status == "pending"
        )
    ).options(
        joinedload(ChatInvitation.chat_room),
        joinedload(ChatInvitation.inviter)
    ).order_by(desc(ChatInvitation.created_at)).offset(skip).limit(limit).all()


# Utility functions
async def get_unread_count(db: Session, chat_room_id: int, user_id: int) -> int:
    """Get unread message count for a user in a chat"""
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.chat_room_id == chat_room_id,
            ChatParticipant.user_id == user_id
        )
    ).first()
    
    if not participant or not participant.last_read_at:
        return db.query(Message).filter(
            and_(
                Message.chat_room_id == chat_room_id,
                Message.sender_id != user_id,
                Message.is_deleted == False
            )
        ).count()
    
    return db.query(Message).filter(
        and_(
            Message.chat_room_id == chat_room_id,
            Message.sender_id != user_id,
            Message.created_at > participant.last_read_at,
            Message.is_deleted == False
        )
    ).count()


async def get_direct_chat(db: Session, user1_id: int, user2_id: int) -> Optional[ChatRoom]:
    """Get or create direct chat between two users"""
    # Look for existing direct chat
    chat_room = db.query(ChatRoom).join(ChatParticipant).filter(
        and_(
            ChatRoom.chat_type == "direct",
            ChatParticipant.user_id.in_([user1_id, user2_id])
        )
    ).group_by(ChatRoom.id).having(
        func.count(ChatParticipant.user_id) == 2
    ).first()
    
    return chat_room
