"""
Messaging and Chat System Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ChatType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


# Chat Room Schemas
class ChatRoomBase(BaseModel):
    name: Optional[str] = None
    chat_type: ChatType = ChatType.DIRECT


class ChatRoomCreate(ChatRoomBase):
    participant_ids: List[int] = Field(..., description="List of user IDs to add to the chat")


class ChatRoomUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ChatRoomOut(ChatRoomBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    participant_count: int
    last_message: Optional[Dict[str, Any]] = None
    unread_count: int = 0
    
    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None
    reply_to_id: Optional[int] = None


class MessageCreate(MessageBase):
    chat_room_id: int


class MessageUpdate(BaseModel):
    content: str


class MessageOut(MessageBase):
    id: int
    chat_room_id: int
    sender_id: int
    created_at: datetime
    updated_at: datetime
    is_edited: bool
    is_deleted: bool
    sender_name: str
    sender_avatar: Optional[str] = None
    read_by: List[int] = []
    
    class Config:
        from_attributes = True


# Participant Schemas
class ChatParticipantBase(BaseModel):
    user_id: int
    is_admin: bool = False


class ChatParticipantCreate(ChatParticipantBase):
    chat_room_id: int


class ChatParticipantUpdate(BaseModel):
    is_admin: Optional[bool] = None
    last_read_at: Optional[datetime] = None


class ChatParticipantOut(ChatParticipantBase):
    id: int
    chat_room_id: int
    joined_at: datetime
    left_at: Optional[datetime] = None
    last_read_at: Optional[datetime] = None
    user_name: str
    user_avatar: Optional[str] = None
    user_online: bool = False
    
    class Config:
        from_attributes = True


# Invitation Schemas
class ChatInvitationBase(BaseModel):
    invited_user_id: int


class ChatInvitationCreate(ChatInvitationBase):
    chat_room_id: int


class ChatInvitationUpdate(BaseModel):
    status: InvitationStatus


class ChatInvitationOut(ChatInvitationBase):
    id: int
    chat_room_id: int
    invited_by: int
    status: InvitationStatus
    created_at: datetime
    responded_at: Optional[datetime] = None
    chat_room_name: str
    inviter_name: str
    invited_user_name: str
    
    class Config:
        from_attributes = True


# Response Schemas
class ChatListResponse(BaseModel):
    chats: List[ChatRoomOut]
    total: int
    page: int
    page_size: int


class MessageListResponse(BaseModel):
    messages: List[MessageOut]
    total: int
    page: int
    page_size: int
    has_more: bool


class ParticipantListResponse(BaseModel):
    participants: List[ChatParticipantOut]
    total: int


class InvitationListResponse(BaseModel):
    invitations: List[ChatInvitationOut]
    total: int
    page: int
    page_size: int


# WebSocket Schemas
class WebSocketMessage(BaseModel):
    type: str  # message, typing, read, join, leave
    data: Dict[str, Any]


class TypingIndicator(BaseModel):
    chat_room_id: int
    user_id: int
    is_typing: bool


class ReadReceipt(BaseModel):
    message_id: int
    user_id: int
    read_at: datetime


