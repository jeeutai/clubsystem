import streamlit as st
import pandas as pd
from datetime import datetime

class ChatSystem:
    def __init__(self):
        self.chat_file = 'data/chat_logs.csv'
    
    def show_chat_interface(self, user):
        """Display the chat interface"""
        st.markdown("### 💬 채팅")
        
        # Get user's clubs
        user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        club_options = ["전체"] + user_clubs['club_name'].tolist()
        
        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            all_clubs = clubs_df['name'].tolist() if not clubs_df.empty else []
            club_options = ["전체"] + all_clubs
        
        # Chat room selection
        selected_room = st.selectbox("💬 채팅방 선택", club_options)
        
        # Display chat messages
        self.show_chat_messages(selected_room, user)
        
        # Message input
        self.show_message_input(selected_room, user)
    
    def show_chat_messages(self, room, user):
        """Display chat messages for the selected room"""
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        
        if chat_df.empty:
            st.info("아직 메시지가 없습니다.")
            return
        
        # Filter messages for the selected room
        if room != "전체":
            room_messages = chat_df[
                (chat_df['club'] == room) & 
                (chat_df['deleted'] != True)
            ]
        else:
            room_messages = chat_df[chat_df['deleted'] != True]
        
        if room_messages.empty:
            st.info("이 채팅방에는 아직 메시지가 없습니다.")
            return
        
        # Sort by timestamp
        room_messages = room_messages.sort_values('timestamp')
        
        # Create a container for messages with fixed height
        messages_container = st.container()
        
        with messages_container:
            st.markdown("#### 💬 메시지")
            
            # Display messages
            for _, message in room_messages.iterrows():
                self.display_message(message, user)
    
    def display_message(self, message, current_user):
        """Display a single chat message"""
        is_own_message = message['username'] == current_user['username']
        
        # Time formatting
        timestamp = pd.to_datetime(message['timestamp'])
        time_str = timestamp.strftime('%H:%M')
        date_str = timestamp.strftime('%m/%d')
        
        if is_own_message:
            # Own message (right aligned)
            st.markdown(f"""
            <div style="text-align: right; margin: 10px 0;">
                <div class="chat-message-own">
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 5px; opacity: 0.8;">{message['username']}</div>
                    <div>{message['message']}</div>
                    <div style="font-size: 10px; margin-top: 5px; opacity: 0.7;">{date_str} {time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Other's message (left aligned)
            st.markdown(f"""
            <div style="text-align: left; margin: 10px 0;">
                <div class="chat-message-other">
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 5px; color: #FF6B6B;">{message['username']}</div>
                    <div>{message['message']}</div>
                    <div style="font-size: 10px; margin-top: 5px; color: #666;">{date_str} {time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Admin controls
        if current_user['role'] == '선생님':
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("🗑️", key=f"delete_msg_{message['id']}", help="메시지 삭제"):
                    self.delete_message(message['id'])
                    st.rerun()
            with col2:
                if st.button("📋", key=f"copy_msg_{message['id']}", help="메시지 복사"):
                    st.write(f"복사됨: {message['message']}")
    
    def show_message_input(self, room, user):
        """Display message input form"""
        st.markdown("---")
        
        with st.form("message_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                message = st.text_input(
                    "메시지 입력", 
                    placeholder=f"{room} 채팅방에 메시지를 입력하세요...",
                    label_visibility="collapsed"
                )
            
            with col2:
                send_button = st.form_submit_button("📤 전송", use_container_width=True)
            
            if send_button and message.strip():
                self.send_message(user['username'], room, message.strip())
                st.rerun()
    
    def send_message(self, username, club, message):
        """Send a new message"""
        message_data = {
            'username': username,
            'club': club,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deleted': False
        }
        
        if st.session_state.data_manager.add_record('chat_logs', message_data):
            # Add notification for new message
            st.session_state.notification_system.add_notification(
                f"새 메시지 ({club})",
                "info",
                "all",
                f"{username}: {message[:50]}{'...' if len(message) > 50 else ''}"
            )
            return True
        return False
    
    def delete_message(self, message_id):
        """Mark a message as deleted"""
        return st.session_state.data_manager.update_record('chat_logs', message_id, {'deleted': True})
    
    def get_recent_messages(self, room, limit=50):
        """Get recent messages for a room"""
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        
        if chat_df.empty:
            return pd.DataFrame()
        
        # Filter by room
        if room != "전체":
            room_messages = chat_df[
                (chat_df['club'] == room) & 
                (chat_df['deleted'] != True)
            ]
        else:
            room_messages = chat_df[chat_df['deleted'] != True]
        
        # Sort and limit
        room_messages = room_messages.sort_values('timestamp', ascending=False).head(limit)
        return room_messages.sort_values('timestamp')
    
    def get_chat_statistics(self, club=None):
        """Get chat statistics"""
        chat_df = st.session_state.data_manager.load_csv('chat_logs')
        
        if chat_df.empty:
            return {
                'total_messages': 0,
                'active_users': 0,
                'messages_today': 0
            }
        
        # Filter by club if specified
        if club and club != "전체":
            chat_df = chat_df[chat_df['club'] == club]
        
        # Filter non-deleted messages
        chat_df = chat_df[chat_df['deleted'] != True]
        
        # Calculate statistics
        total_messages = len(chat_df)
        active_users = chat_df['username'].nunique()
        
        # Messages today
        today = datetime.now().strftime('%Y-%m-%d')
        messages_today = len(chat_df[chat_df['timestamp'].str.startswith(today)])
        
        return {
            'total_messages': total_messages,
            'active_users': active_users,
            'messages_today': messages_today
        }
