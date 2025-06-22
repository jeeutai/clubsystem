import pandas as pd
import os
from datetime import datetime
import streamlit as st

class AuthManager:
    def __init__(self):
        self.users_file = 'data/users.csv'
        self.ensure_data_directory()
        self.initialize_users()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def initialize_users(self):
        """Initialize users.csv with default accounts if it doesn't exist"""
        if not os.path.exists(self.users_file):
            # Create initial user accounts based on the provided data
            initial_users = [
                # Teacher accounts
                {'username': '조성우', 'password': 'admin', 'name': '조성우', 'role': '선생님', 'club_name': '코딩', 'club_role': '선생님', 'created_date': '2024-01-15 09:00:00'},
                {'username': '장원진', 'password': '12341234', 'name': '장원진', 'role': '선생님', 'club_name': '전체', 'club_role': '선생님', 'created_date': '2024-01-15 09:00:00'},
                
                # Students with their club assignments
                {'username': '강서준', 'password': '1234', 'name': '강서준', 'role': '총무', 'club_name': '코딩', 'club_role': '총무', 'created_date': '2024-01-15 09:07:00'},
                {'username': '곽승현', 'password': '1234', 'name': '곽승현', 'role': '동아리원', 'club_name': '미스테리탐구', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김민아', 'password': '1234', 'name': '김민아', 'role': '동아리원', 'club_name': '줄넘기', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김보경', 'password': '1234', 'name': '김보경', 'role': '회장', 'club_name': '만들기', 'club_role': '회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김보민', 'password': '1234', 'name': '김보민', 'role': '동아리원', 'club_name': '만들기', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김영원', 'password': '1234', 'name': '김영원', 'role': '동아리원', 'club_name': '만들기', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김의준', 'password': '1234', 'name': '김의준', 'role': '동아리원', 'club_name': '미스테리탐구', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김제이', 'password': '1234', 'name': '김제이', 'role': '회장', 'club_name': '줄넘기', 'club_role': '회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '김현서', 'password': '1234', 'name': '김현서', 'role': '동아리원', 'club_name': '풍선아트', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '박규혁', 'password': '1234', 'name': '박규혁', 'role': '부회장', 'club_name': '풍선아트', 'club_role': '부회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '박효주', 'password': '1234', 'name': '박효주', 'role': '부회장', 'club_name': '미스테리탐구', 'club_role': '부회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '배다인', 'password': '1234', 'name': '배다인', 'role': '부회장', 'club_name': '댄스', 'club_role': '부회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '백주아', 'password': '1234', 'name': '백주아', 'role': '회장', 'club_name': '댄스', 'club_role': '회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '신소민', 'password': '1234', 'name': '신소민', 'role': '동아리원', 'club_name': '미스테리탐구', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '오채윤', 'password': '1234', 'name': '오채윤', 'role': '회장', 'club_name': '미스테리탐구', 'club_role': '회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '유수현', 'password': '1234', 'name': '유수현', 'role': '동아리원', 'club_name': '댄스', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '장주원', 'password': '1234', 'name': '장주원', 'role': '총무', 'club_name': '코딩', 'club_role': '총무', 'created_date': '2024-01-15 09:07:00'},
                {'username': '전준오', 'password': '1234', 'name': '전준오', 'role': '동아리원', 'club_name': '코딩', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '정예준', 'password': '1234', 'name': '정예준', 'role': '동아리원', 'club_name': '미스테리탐구', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '정지호', 'password': '1234', 'name': '정지호', 'role': '동아리원', 'club_name': '미스테리탐구', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '정찬희', 'password': '1234', 'name': '정찬희', 'role': '부회장', 'club_name': '코딩', 'club_role': '부회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '최명준', 'password': '1234', 'name': '최명준', 'role': '회장', 'club_name': '풍선아트', 'club_role': '회장', 'created_date': '2024-01-15 09:07:00'},
                {'username': '한동길', 'password': '1234', 'name': '한동길', 'role': '동아리원', 'club_name': '풍선아트', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '한수진', 'password': '1234', 'name': '한수진', 'role': '동아리원', 'club_name': '댄스', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'},
                {'username': '황하정', 'password': '1234', 'name': '황하정', 'role': '동아리원', 'club_name': '줄넘기', 'club_role': '동아리원', 'created_date': '2024-01-15 09:07:00'}
            ]
            
            df = pd.DataFrame(initial_users)
            df.to_csv(self.users_file, index=False, encoding='utf-8-sig')
    
    def login(self, username, password):
        """Authenticate user login"""
        try:
            df = pd.read_csv(self.users_file, encoding='utf-8-sig')
            user = df[(df['username'] == username) & (df['password'] == password)]
            
            if not user.empty:
                return user.iloc[0].to_dict()
            return None
        except Exception as e:
            st.error(f"Login error: {e}")
            return None
    
    def create_user(self, username, password, name, role, club_name, club_role):
        """Create a new user account"""
        try:
            df = pd.read_csv(self.users_file, encoding='utf-8-sig')
            
            # Check if username already exists
            if username in df['username'].values:
                return False, "사용자명이 이미 존재합니다."
            
            new_user = {
                'username': username,
                'password': password,
                'name': name,
                'role': role,
                'club_name': club_name,
                'club_role': club_role,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            df.to_csv(self.users_file, index=False, encoding='utf-8-sig')
            return True, "계정이 성공적으로 생성되었습니다."
        except Exception as e:
            return False, f"Account creation error: {e}"
    
    def get_all_users(self):
        """Get all user accounts"""
        try:
            return pd.read_csv(self.users_file, encoding='utf-8-sig')
        except:
            return pd.DataFrame()
    
    def update_user(self, username, updates):
        """Update user information"""
        try:
            df = pd.read_csv(self.users_file, encoding='utf-8-sig')
            
            for key, value in updates.items():
                df.loc[df['username'] == username, key] = value
            
            df.to_csv(self.users_file, index=False, encoding='utf-8-sig')
            return True, "사용자 정보가 업데이트되었습니다."
        except Exception as e:
            return False, f"Update error: {e}"
    
    def delete_user(self, username):
        """Delete a user account"""
        try:
            df = pd.read_csv(self.users_file, encoding='utf-8-sig')
            df = df[df['username'] != username]
            df.to_csv(self.users_file, index=False, encoding='utf-8-sig')
            return True, "사용자가 삭제되었습니다."
        except Exception as e:
            return False, f"Delete error: {e}"
