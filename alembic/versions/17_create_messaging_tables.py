"""create messaging system tables

Revision ID: 17_create_messaging_tables
Revises: 16_enhance_payment_models
Create Date: 2025-08-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17_create_messaging_tables'
down_revision = '16_enhance_payment_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_rooms table
    op.create_table(
        'chat_rooms',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('chat_type', sa.String(), nullable=False, server_default='direct'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    
    # Create chat_participants table
    op.create_table(
        'chat_participants',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_read_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False, server_default='text'),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('reply_to_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    )
    
    # Create message_read_status table
    op.create_table(
        'message_read_status',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create chat_invitations table
    op.create_table(
        'chat_invitations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('chat_room_id', sa.Integer(), nullable=False),
        sa.Column('invited_by', sa.Integer(), nullable=False),
        sa.Column('invited_user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for better performance
    op.create_index('ix_chat_rooms_created_by', 'chat_rooms', ['created_by'])
    op.create_index('ix_chat_rooms_chat_type', 'chat_rooms', ['chat_type'])
    op.create_index('ix_chat_rooms_updated_at', 'chat_rooms', ['updated_at'])
    
    op.create_index('ix_chat_participants_chat_room_id', 'chat_participants', ['chat_room_id'])
    op.create_index('ix_chat_participants_user_id', 'chat_participants', ['user_id'])
    op.create_index('ix_chat_participants_left_at', 'chat_participants', ['left_at'])
    
    op.create_index('ix_messages_chat_room_id', 'messages', ['chat_room_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_reply_to_id', 'messages', ['reply_to_id'])
    op.create_index('ix_messages_is_deleted', 'messages', ['is_deleted'])
    
    op.create_index('ix_message_read_status_message_id', 'message_read_status', ['message_id'])
    op.create_index('ix_message_read_status_user_id', 'message_read_status', ['user_id'])
    
    op.create_index('ix_chat_invitations_chat_room_id', 'chat_invitations', ['chat_room_id'])
    op.create_index('ix_chat_invitations_invited_user_id', 'chat_invitations', ['invited_user_id'])
    op.create_index('ix_chat_invitations_status', 'chat_invitations', ['status'])
    
    # Add foreign key constraints
    op.create_foreign_key('fk_chat_rooms_created_by', 'chat_rooms', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_chat_participants_chat_room_id', 'chat_participants', 'chat_rooms', ['chat_room_id'], ['id'])
    op.create_foreign_key('fk_chat_participants_user_id', 'chat_participants', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_messages_chat_room_id', 'messages', 'chat_rooms', ['chat_room_id'], ['id'])
    op.create_foreign_key('fk_messages_sender_id', 'messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('fk_messages_reply_to_id', 'messages', 'messages', ['reply_to_id'], ['id'])
    op.create_foreign_key('fk_message_read_status_message_id', 'message_read_status', 'messages', ['message_id'], ['id'])
    op.create_foreign_key('fk_message_read_status_user_id', 'message_read_status', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_chat_invitations_chat_room_id', 'chat_invitations', 'chat_rooms', ['chat_room_id'], ['id'])
    op.create_foreign_key('fk_chat_invitations_invited_by', 'chat_invitations', 'users', ['invited_by'], ['id'])
    op.create_foreign_key('fk_chat_invitations_invited_user_id', 'chat_invitations', 'users', ['invited_user_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_chat_invitations_invited_user_id', 'chat_invitations', type_='foreignkey')
    op.drop_constraint('fk_chat_invitations_invited_by', 'chat_invitations', type_='foreignkey')
    op.drop_constraint('fk_chat_invitations_chat_room_id', 'chat_invitations', type_='foreignkey')
    op.drop_constraint('fk_message_read_status_user_id', 'message_read_status', type_='foreignkey')
    op.drop_constraint('fk_message_read_status_message_id', 'message_read_status', type_='foreignkey')
    op.drop_constraint('fk_messages_reply_to_id', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_sender_id', 'messages', type_='foreignkey')
    op.drop_constraint('fk_messages_chat_room_id', 'messages', type_='foreignkey')
    op.drop_constraint('fk_chat_participants_user_id', 'chat_participants', type_='foreignkey')
    op.drop_constraint('fk_chat_participants_chat_room_id', 'chat_participants', type_='foreignkey')
    op.drop_constraint('fk_chat_rooms_created_by', 'chat_rooms', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_chat_invitations_status', table_name='chat_invitations')
    op.drop_index('ix_chat_invitations_invited_user_id', table_name='chat_invitations')
    op.drop_index('ix_chat_invitations_chat_room_id', table_name='chat_invitations')
    op.drop_index('ix_message_read_status_user_id', table_name='message_read_status')
    op.drop_index('ix_message_read_status_message_id', table_name='message_read_status')
    op.drop_index('ix_messages_is_deleted', table_name='messages')
    op.drop_index('ix_messages_reply_to_id', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_sender_id', table_name='messages')
    op.drop_index('ix_messages_chat_room_id', table_name='messages')
    op.drop_index('ix_chat_participants_left_at', table_name='chat_participants')
    op.drop_index('ix_chat_participants_user_id', table_name='chat_participants')
    op.drop_index('ix_chat_participants_chat_room_id', table_name='chat_participants')
    op.drop_index('ix_chat_rooms_updated_at', table_name='chat_rooms')
    op.drop_index('ix_chat_rooms_chat_type', table_name='chat_rooms')
    op.drop_index('ix_chat_rooms_created_by', table_name='chat_rooms')
    
    # Drop tables
    op.drop_table('chat_invitations')
    op.drop_table('message_read_status')
    op.drop_table('messages')
    op.drop_table('chat_participants')
    op.drop_table('chat_rooms')
