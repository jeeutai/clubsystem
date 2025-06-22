import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class NotificationSystem:
    def __init__(self):
        self.notifications_file = 'data/notifications.csv'
    
    def add_notification(self, title, notification_type, target_user, message=""):
        """Add a new notification"""
        try:
            notification_data = {
                'username': target_user,
                'title': title,
                'message': message,
                'type': notification_type,
                'read': False,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # If target is "all", create notifications for all users
            if target_user == "all":
                users_df = st.session_state.data_manager.load_csv('users')
                if not users_df.empty:
                    for _, user in users_df.iterrows():
                        notification_data['username'] = user['username']
                        st.session_state.data_manager.add_record('notifications', notification_data.copy())
                    return True
            else:
                return st.session_state.data_manager.add_record('notifications', notification_data)
            
        except Exception as e:
            st.error(f"알림 생성 중 오류가 발생했습니다: {e}")
            return False
    
    def get_user_notifications(self, username):
        """Get notifications for a specific user"""
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            
            if notifications_df.empty:
                return []
            
            user_notifications = notifications_df[notifications_df['username'] == username]
            user_notifications = user_notifications.sort_values('created_date', ascending=False)
            
            return user_notifications.to_dict('records')
        except:
            return []
    
    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        try:
            return st.session_state.data_manager.update_record('notifications', notification_id, {'read': True})
        except Exception as e:
            st.error(f"알림 읽음 처리 중 오류가 발생했습니다: {e}")
            return False
    
    def mark_all_as_read(self, username):
        """Mark all notifications as read for a user"""
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            user_notifications = notifications_df[
                (notifications_df['username'] == username) & 
                (notifications_df['read'] == False)
            ]
            
            success_count = 0
            for _, notification in user_notifications.iterrows():
                if self.mark_as_read(notification['id']):
                    success_count += 1
            
            return success_count > 0
        except Exception as e:
            st.error(f"전체 알림 읽음 처리 중 오류가 발생했습니다: {e}")
            return False
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            return st.session_state.data_manager.delete_record('notifications', notification_id)
        except Exception as e:
            st.error(f"알림 삭제 중 오류가 발생했습니다: {e}")
            return False
    
    def show_notification_interface(self, user):
        """Display the notification interface"""
        st.markdown("### 🔔 알림")
        
        # Get user notifications
        notifications = self.get_user_notifications(user['username'])
        
        if not notifications:
            st.info("새로운 알림이 없습니다.")
            return
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unread_count = len([n for n in notifications if not n.get('read', False)])
            st.metric("읽지 않은 알림", unread_count)
        
        with col2:
            if st.button("📧 모두 읽음", use_container_width=True):
                if self.mark_all_as_read(user['username']):
                    st.success("모든 알림을 읽음 처리했습니다.")
                    st.rerun()
        
        with col3:
            # Filter options
            filter_type = st.selectbox("🔍 필터", ["전체", "읽지 않음", "읽음"])
        
        # Filter notifications
        filtered_notifications = notifications
        if filter_type == "읽지 않음":
            filtered_notifications = [n for n in notifications if not n.get('read', False)]
        elif filter_type == "읽음":
            filtered_notifications = [n for n in notifications if n.get('read', False)]
        
        # Display notifications
        st.markdown("---")
        
        for notification in filtered_notifications:
            self.show_notification_card(notification, user)
    
    def show_notification_card(self, notification, user):
        """Display a single notification card"""
        # Notification type colors
        type_colors = {
            "info": "#17a2b8",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "announcement": "#6f42c1"
        }
        
        type_icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "announcement": "📢"
        }
        
        color = type_colors.get(notification['type'], "#17a2b8")
        icon = type_icons.get(notification['type'], "🔔")
        
        # Read status styling
        read_status = notification.get('read', False)
        opacity = "0.6" if read_status else "1.0"
        border_style = "1px solid #dee2e6" if read_status else f"2px solid {color}"
        
        # Time formatting
        created_date = pd.to_datetime(notification['created_date'])
        now = datetime.now()
        time_diff = now - created_date
        
        if time_diff.days > 0:
            time_text = f"{time_diff.days}일 전"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            time_text = f"{hours}시간 전"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            time_text = f"{minutes}분 전"
        else:
            time_text = "방금 전"
        
        with st.container():
            st.markdown(f"""
            <div style="
                background: white; 
                padding: 20px; 
                border-radius: 12px; 
                margin: 10px 0; 
                border: {border_style}; 
                opacity: {opacity};
                transition: all 0.3s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 20px; margin-right: 10px;">{icon}</span>
                            <h4 style="margin: 0; color: {color};">{notification['title']}</h4>
                            {'' if read_status else '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">NEW</span>'}
                        </div>
                        
                        {f'<p style="color: #666; margin: 10px 0; line-height: 1.5;">{notification["message"]}</p>' if notification.get('message') else ''}
                        
                        <small style="color: #999;">{time_text} • {notification['created_date'][:16]}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            
            with col1:
                if not read_status:
                    if st.button("📖", key=f"read_{notification['id']}", help="읽음 처리"):
                        if self.mark_as_read(notification['id']):
                            st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{notification['id']}", help="삭제"):
                    if self.delete_notification(notification['id']):
                        st.success("알림이 삭제되었습니다.")
                        st.rerun()
    
    def send_system_notification(self, title, message, notification_type="info", target_users=None):
        """Send system-wide notification"""
        try:
            if target_users is None:
                # Send to all users
                users_df = st.session_state.data_manager.load_csv('users')
                target_users = users_df['username'].tolist() if not users_df.empty else []
            
            success_count = 0
            for username in target_users:
                if self.add_notification(title, notification_type, username, message):
                    success_count += 1
            
            return success_count > 0
        except Exception as e:
            st.error(f"시스템 알림 발송 중 오류가 발생했습니다: {e}")
            return False
    
    def send_club_notification(self, club_name, title, message, notification_type="info"):
        """Send notification to specific club members"""
        try:
            users_df = st.session_state.data_manager.load_csv('users')
            
            if club_name == "전체":
                club_users = users_df['username'].tolist()
            else:
                club_users = users_df[users_df['club_name'] == club_name]['username'].tolist()
            
            return self.send_system_notification(title, message, notification_type, club_users)
        except Exception as e:
            st.error(f"동아리 알림 발송 중 오류가 발생했습니다: {e}")
            return False
    
    def check_assignment_deadlines(self):
        """Check for assignment deadlines and send notifications"""
        try:
            assignments_df = st.session_state.data_manager.load_csv('assignments')
            
            if assignments_df.empty:
                return
            
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            # Check assignments due tomorrow
            assignments_df['due_date'] = pd.to_datetime(assignments_df['due_date'])
            due_tomorrow = assignments_df[
                (assignments_df['due_date'].dt.date == tomorrow.date()) &
                (assignments_df['status'] == '활성')
            ]
            
            for _, assignment in due_tomorrow.iterrows():
                title = f"⏰ 과제 마감 임박: {assignment['title']}"
                message = f"내일({tomorrow.strftime('%m월 %d일')}) 마감되는 과제가 있습니다. 서둘러 제출해주세요!"
                
                self.send_club_notification(assignment['club'], title, message, "warning")
            
        except Exception as e:
            st.error(f"과제 마감일 확인 중 오류가 발생했습니다: {e}")
    
    def check_schedule_reminders(self):
        """Check for upcoming schedules and send reminders"""
        try:
            schedule_df = st.session_state.data_manager.load_csv('schedule')
            
            if schedule_df.empty:
                return
            
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            # Check schedules for tomorrow
            schedule_df['date'] = pd.to_datetime(schedule_df['date'])
            tomorrow_schedules = schedule_df[
                schedule_df['date'].dt.date == tomorrow.date()
            ]
            
            for _, schedule in tomorrow_schedules.iterrows():
                title = f"📅 내일 일정 알림: {schedule['title']}"
                message = f"내일({tomorrow.strftime('%m월 %d일')}) {schedule['time']}에 '{schedule['title']}' 일정이 있습니다.\n장소: {schedule['location']}"
                
                self.send_club_notification(schedule['club'], title, message, "info")
            
        except Exception as e:
            st.error(f"일정 알림 확인 중 오류가 발생했습니다: {e}")
    
    def get_notification_statistics(self, user):
        """Get notification statistics for admin"""
        try:
            notifications_df = st.session_state.data_manager.load_csv('notifications')
            
            if notifications_df.empty:
                return {}
            
            # Overall stats
            total_notifications = len(notifications_df)
            unread_notifications = len(notifications_df[notifications_df['read'] == False])
            
            # By type
            type_counts = notifications_df['type'].value_counts().to_dict()
            
            # Recent activity
            week_ago = datetime.now() - timedelta(days=7)
            notifications_df['created_date'] = pd.to_datetime(notifications_df['created_date'])
            recent_notifications = len(notifications_df[notifications_df['created_date'] >= week_ago])
            
            return {
                'total': total_notifications,
                'unread': unread_notifications,
                'by_type': type_counts,
                'recent_week': recent_notifications,
                'read_rate': ((total_notifications - unread_notifications) / total_notifications * 100) if total_notifications > 0 else 0
            }
            
        except Exception as e:
            st.error(f"알림 통계 생성 중 오류가 발생했습니다: {e}")
            return {}
