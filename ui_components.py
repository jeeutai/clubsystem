import streamlit as st
import pandas as pd
from datetime import datetime

class UIComponents:
    def __init__(self):
        pass
    
    def show_club_card(self, club, user_role=None, show_join_button=False):
        """Display a club information card"""
        meet_button = ""
        if pd.notna(club['meet_link']) and club['meet_link']:
            meet_button = f'<a href="{club["meet_link"]}" target="_blank" style="background: #28a745; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; margin-top: 10px; display: inline-block;">🎥 화상회의 참여</a>'
        
        st.markdown(f"""
        <div class="club-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3>{club['icon']} {club['name']}</h3>
                    <p style="color: #666; margin: 10px 0;">{club['description']}</p>
                    <div style="margin-top: 15px;">
                        <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px; margin-right: 10px;">
                            👑 회장: {club['president']}
                        </span>
                        <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px;">
                            👥 정원: {club['max_members']}명
                        </span>
                    </div>
                    {meet_button}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_user_card(self, user, show_actions=False):
        """Display a user information card"""
        actions_html = ""
        if show_actions:
            actions_html = """
            <div style="margin-top: 10px;">
                <small>관리 작업 가능</small>
            </div>
            """
        
        st.markdown(f"""
        <div class="club-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{user['name']}</h4>
                    <p style="margin: 5px 0; color: #666;">@{user['username']}</p>
                    <span class="role-badge">{user['role']}</span>
                    <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px; margin-left: 10px;">
                        {user['club_name']}
                    </span>
                </div>
                <div style="text-align: right;">
                    <small style="color: #666;">가입일</small><br>
                    <small>{user['created_date'][:10]}</small>
                </div>
            </div>
            {actions_html}
        </div>
        """, unsafe_allow_html=True)
    
    def show_stats_card(self, title, value, icon, color="#FF6B6B"):
        """Display a statistics card"""
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {color}; margin: 0;">{icon}</h3>
            <h2 style="margin: 5px 0;">{value}</h2>
            <p style="color: #666; margin: 0;">{title}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_notification(self, message, notification_type="info"):
        """Display a notification"""
        colors = {
            "info": "#17a2b8",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        color = colors.get(notification_type, "#17a2b8")
        icon = icons.get(notification_type, "ℹ️")
        
        st.markdown(f"""
        <div style="background-color: {color}15; border-left: 4px solid {color}; padding: 15px; margin: 10px 0; border-radius: 5px;">
            {icon} {message}
        </div>
        """, unsafe_allow_html=True)
    
    def show_loading_spinner(self, text="로딩 중..."):
        """Display a loading spinner"""
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #FF6B6B; border-radius: 50%; animation: spin 2s linear infinite;"></div>
            <p style="margin-top: 10px; color: #666;">{text}</p>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def show_progress_bar(self, current, total, label="진행률"):
        """Display a progress bar"""
        percentage = (current / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>{label}</span>
                <span>{current}/{total} ({percentage:.1f}%)</span>
            </div>
            <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #FF6B6B, #4ECDC4); height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_badge(self, text, color="#FF6B6B"):
        """Display a badge"""
        return f'<span style="background: {color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{text}</span>'
    
    def show_timeline_item(self, title, description, time, icon="📅"):
        """Display a timeline item"""
        st.markdown(f"""
        <div style="border-left: 3px solid #FF6B6B; padding-left: 20px; margin: 15px 0; position: relative;">
            <div style="position: absolute; left: -8px; top: 0; background: white; border: 2px solid #FF6B6B; border-radius: 50%; width: 16px; height: 16px;"></div>
            <div style="margin-left: 10px;">
                <h4 style="margin: 0; color: #FF6B6B;">{icon} {title}</h4>
                <p style="margin: 5px 0; color: #666;">{description}</p>
                <small style="color: #999;">{time}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_form_container(self, title, description=""):
        """Create a styled form container"""
        st.markdown(f"""
        <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 20px 0;">
            <h3 style="color: #FF6B6B; margin-bottom: 10px;">{title}</h3>
            {f'<p style="color: #666; margin-bottom: 20px;">{description}</p>' if description else ''}
        """, unsafe_allow_html=True)
    
    def close_form_container(self):
        """Close form container"""
        st.markdown("</div>", unsafe_allow_html=True)
