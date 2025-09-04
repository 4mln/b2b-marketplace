"""
Messaging and Chat System Models
Supports direct messages, group chats, and message status tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base


class ChatRoom(Base):
    """Chat room for direct messages or group chats"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # For group chats
    chat_type = Column(String, nullable=False, default="direct")  # direct, group
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    participants = relationship("ChatParticipant", back_populates="chat_room")
    messages = relationship("Message", back_populates="chat_room")
    creator = relationship("User", foreign_keys=[created_by])


class ChatParticipant(Base):
    """Participants in chat rooms"""
    __tablename__ = "chat_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    is_admin = Column(Boolean, default=False)  # For group chat admins
    last_read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    chat_room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User")


class Message(Base):
    """Individual messages in chat rooms"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, file, system
    extra_metadata = Column("metadata", JSON, nullable=True)  # For file info, etc.
    reply_to_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")
    reply_to = relationship("Message", remote_side=[id])
    read_status = relationship("MessageReadStatus", back_populates="message")


class MessageReadStatus(Base):
    """Track message read status for each participant"""
    __tablename__ = "message_read_status"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="read_status")
    user = relationship("User")


class ChatInvitation(Base):
    """Invitations to join group chats"""
    __tablename__ = "chat_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, declined
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    chat_room = relationship("ChatRoom")
    inviter = relationship("User", foreign_keys=[invited_by])
    invited_user = relationship("User", foreign_keys=[invited_user_id])


