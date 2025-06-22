
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class GamificationSystem:
    def __init__(self):
        self.point_rules = {
            '출석': 10,
            '지각': 5,
            '결석': 0,
            '조퇴': 7,
            '완벽한_주': 50,
            '월_완벽출석': 200
        }
        
        self.badges = {
            '첫_출석': {'name': '첫 걸음', 'icon': '🎯', 'description': '첫 출석 완료'},
            '일주일_연속': {'name': '일주일 챔피언', 'icon': '🏆', 'description': '7일 연속 출석'},
            '한달_완벽': {'name': '완벽한 한 달', 'icon': '🌟', 'description': '한 달 완벽 출석'},
            '지각_Zero': {'name': '타임 마스터', 'icon': '⏰', 'description': '한 달간 지각 없음'},
            '출석률_90': {'name': '우수 학습자', 'icon': '📚', 'description': '출석률 90% 달성'}
        }
    
    def calculate_points(self, username):
        """사용자 포인트 계산"""
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_records = attendance_df[attendance_df['username'] == username]
        
        total_points = 0
        for _, record in user_records.iterrows():
            total_points += self.point_rules.get(record['status'], 0)
        
        # 보너스 포인트 계산
        total_points += self.calculate_bonus_points(username)
        
        return total_points
    
    def calculate_bonus_points(self, username):
        """보너스 포인트 계산"""
        bonus = 0
        
        # 연속 출석 보너스
        streak = self.get_attendance_streak(username)
        if streak >= 7:
            bonus += self.point_rules['완벽한_주']
        
        # 월 완벽 출석 보너스
        if self.check_monthly_perfect_attendance(username):
            bonus += self.point_rules['월_완벽출석']
        
        return bonus
    
    def get_attendance_streak(self, username):
        """연속 출석일 계산"""
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_records = attendance_df[attendance_df['username'] == username]
        
        if user_records.empty:
            return 0
        
        user_records = user_records.sort_values('date', ascending=False)
        streak = 0
        
        for _, record in user_records.iterrows():
            if record['status'] == '출석':
                streak += 1
            else:
                break
        
        return streak
    
    def check_monthly_perfect_attendance(self, username):
        """월 완벽 출석 확인"""
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        current_month = datetime.now().strftime('%Y-%m')
        
        month_records = attendance_df[
            (attendance_df['username'] == username) &
            (attendance_df['date'].str.startswith(current_month))
        ]
        
        if month_records.empty:
            return False
        
        return all(month_records['status'] == '출석')
    
    def check_and_award_badges(self, username):
        """뱃지 확인 및 수여"""
        awarded_badges = []
        
        # 기존 뱃지 확인
        badges_df = st.session_state.data_manager.load_csv('badges')
        user_badges = badges_df[badges_df['username'] == username]['badge_name'].tolist() if not badges_df.empty else []
        
        # 첫 출석 뱃지
        if '첫 걸음' not in user_badges:
            attendance_df = st.session_state.data_manager.load_csv('attendance')
            if not attendance_df[attendance_df['username'] == username].empty:
                self.award_badge(username, 'first_attendance')
                awarded_badges.append('첫 걸음')
        
        # 연속 출석 뱃지
        streak = self.get_attendance_streak(username)
        if streak >= 7 and '일주일 챔피언' not in user_badges:
            self.award_badge(username, 'week_champion')
            awarded_badges.append('일주일 챔피언')
        
        # 월 완벽 출석 뱃지
        if self.check_monthly_perfect_attendance(username) and '완벽한 한 달' not in user_badges:
            self.award_badge(username, 'perfect_month')
            awarded_badges.append('완벽한 한 달')
        
        return awarded_badges
    
    def award_badge(self, username, badge_type):
        """뱃지 수여"""
        badge_info = self.badges.get(badge_type, {})
        
        badge_data = {
            'username': username,
            'badge_name': badge_info.get('name', '뱃지'),
            'badge_icon': badge_info.get('icon', '🏅'),
            'description': badge_info.get('description', '뱃지 획득'),
            'awarded_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'awarded_by': 'System'
        }
        
        st.session_state.data_manager.add_record('badges', badge_data)
    
    def get_user_level(self, username):
        """사용자 레벨 계산"""
        points = self.calculate_points(username)
        level = min(points // 100 + 1, 20)  # 100점당 레벨업, 최대 20레벨
        return level
    
    def get_next_level_progress(self, username):
        """다음 레벨까지 진행률"""
        points = self.calculate_points(username)
        current_level_points = (points // 100) * 100
        next_level_points = current_level_points + 100
        progress = (points - current_level_points) / 100
        
        return {
            'current_points': points,
            'next_level_points': next_level_points,
            'progress': progress
        }
    
    def create_leaderboard(self):
        """리더보드 생성"""
        users_df = st.session_state.data_manager.load_csv('users')
        leaderboard = []
        
        for _, user in users_df.iterrows():
            username = user['username']
            points = self.calculate_points(username)
            level = self.get_user_level(username)
            
            leaderboard.append({
                '순위': 0,  # 정렬 후 설정
                '이름': user['name'],
                '포인트': points,
                '레벨': level,
                '동아리': user.get('club_name', 'N/A')
            })
        
        # 포인트로 정렬
        leaderboard.sort(key=lambda x: x['포인트'], reverse=True)
        
        # 순위 설정
        for i, entry in enumerate(leaderboard):
            entry['순위'] = i + 1
        
        return leaderboard[:10]  # 상위 10명만 반환
