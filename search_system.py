import streamlit as st
import pandas as pd
from datetime import datetime

class SearchSystem:
    def __init__(self):
        pass
    
    def show_search_interface(self, user):
        """Display the search interface"""
        st.markdown("### 🔍 통합 검색")
        
        # Search form
        with st.form("search_form"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_query = st.text_input(
                    "검색어", 
                    placeholder="제목, 내용, 작성자 등을 검색하세요...",
                    label_visibility="collapsed"
                )
            
            with col2:
                search_button = st.form_submit_button("🔍 검색", use_container_width=True)
        
        # Search filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Content type filter
            search_types = st.multiselect(
                "🗂️ 검색 범위",
                ["게시글", "채팅", "과제", "일정", "투표", "사용자"],
                default=["게시글", "채팅", "과제", "일정"]
            )
        
        with col2:
            # Club filter
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            club_options = ["전체"] + user_clubs['club_name'].tolist()
            
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                all_clubs = clubs_df['name'].tolist() if not clubs_df.empty else []
                club_options = ["전체"] + all_clubs
            
            selected_club = st.selectbox("🏷️ 동아리 필터", club_options)
        
        with col3:
            # Date range filter
            date_range = st.selectbox(
                "📅 기간 필터",
                ["전체", "오늘", "이번 주", "이번 달", "최근 3개월"]
            )
        
        # Perform search
        if search_button and search_query.strip():
            search_results = self.perform_search(
                search_query.strip(),
                search_types,
                selected_club,
                date_range,
                user
            )
            
            self.display_search_results(search_results, search_query)
        
        elif search_query.strip() == "":
            st.info("검색어를 입력해주세요.")
        
        # Recent searches
        self.show_recent_searches(user)
        
        # Quick search suggestions
        self.show_quick_search_suggestions(user)
    
    def perform_search(self, query, search_types, club_filter, date_range, user):
        """Perform search across different content types"""
        results = {
            'posts': [],
            'chats': [],
            'assignments': [],
            'schedules': [],
            'votes': [],
            'users': []
        }
        
        # Date filter helper
        date_filter_start = self.get_date_filter_start(date_range)
        
        # Search posts
        if "게시글" in search_types:
            results['posts'] = self.search_posts(query, club_filter, date_filter_start, user)
        
        # Search chats
        if "채팅" in search_types:
            results['chats'] = self.search_chats(query, club_filter, date_filter_start, user)
        
        # Search assignments
        if "과제" in search_types:
            results['assignments'] = self.search_assignments(query, club_filter, date_filter_start, user)
        
        # Search schedules
        if "일정" in search_types:
            results['schedules'] = self.search_schedules(query, club_filter, date_filter_start, user)
        
        # Search votes
        if "투표" in search_types:
            results['votes'] = self.search_votes(query, club_filter, date_filter_start, user)
        
        # Search users
        if "사용자" in search_types:
            results['users'] = self.search_users(query, club_filter, user)
        
        return results
    
    def get_date_filter_start(self, date_range):
        """Get start date for date range filter"""
        now = datetime.now()
        
        if date_range == "오늘":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "이번 주":
            return now - pd.Timedelta(days=7)
        elif date_range == "이번 달":
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "최근 3개월":
            return now - pd.Timedelta(days=90)
        else:  # 전체
            return None
    
    def search_posts(self, query, club_filter, date_filter_start, user):
        """Search in posts"""
        try:
            posts_df = st.session_state.data_manager.load_csv('posts')
            
            if posts_df.empty:
                return []
            
            # Apply filters
            if club_filter != "전체":
                posts_df = posts_df[posts_df['club'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                posts_df = posts_df[posts_df['club'].isin(user_club_names)]
            
            # Date filter
            if date_filter_start:
                posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
                posts_df = posts_df[posts_df['created_date'] >= date_filter_start]
            
            # Text search
            query_lower = query.lower()
            matching_posts = posts_df[
                posts_df['title'].str.lower().str.contains(query_lower, na=False) |
                posts_df['content'].str.lower().str.contains(query_lower, na=False) |
                posts_df['author'].str.lower().str.contains(query_lower, na=False) |
                posts_df['tags'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, post in matching_posts.iterrows():
                results.append({
                    'type': 'post',
                    'id': post['id'],
                    'title': post['title'],
                    'content': post['content'][:200] + '...' if len(post['content']) > 200 else post['content'],
                    'author': post['author'],
                    'club': post['club'],
                    'created_date': post['created_date'],
                    'extra_info': f"❤️ {post.get('likes', 0)} 💬 {post.get('comments', 0)}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"게시글 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def search_chats(self, query, club_filter, date_filter_start, user):
        """Search in chat logs"""
        try:
            chat_df = st.session_state.data_manager.load_csv('chat_logs')
            
            if chat_df.empty:
                return []
            
            # Filter non-deleted messages
            chat_df = chat_df[chat_df['deleted'] != True]
            
            # Apply filters
            if club_filter != "전체":
                chat_df = chat_df[chat_df['club'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                chat_df = chat_df[chat_df['club'].isin(user_club_names)]
            
            # Date filter
            if date_filter_start:
                chat_df['timestamp'] = pd.to_datetime(chat_df['timestamp'])
                chat_df = chat_df[chat_df['timestamp'] >= date_filter_start]
            
            # Text search
            query_lower = query.lower()
            matching_chats = chat_df[
                chat_df['message'].str.lower().str.contains(query_lower, na=False) |
                chat_df['username'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, chat in matching_chats.iterrows():
                results.append({
                    'type': 'chat',
                    'id': chat['id'],
                    'title': f"💬 {chat['username']}의 메시지",
                    'content': chat['message'],
                    'author': chat['username'],
                    'club': chat['club'],
                    'created_date': chat['timestamp'],
                    'extra_info': f"채팅방: {chat['club']}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"채팅 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def search_assignments(self, query, club_filter, date_filter_start, user):
        """Search in assignments"""
        try:
            assignments_df = st.session_state.data_manager.load_csv('assignments')
            
            if assignments_df.empty:
                return []
            
            # Apply filters
            if club_filter != "전체":
                assignments_df = assignments_df[assignments_df['club'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                assignments_df = assignments_df[assignments_df['club'].isin(user_club_names)]
            
            # Date filter
            if date_filter_start:
                assignments_df['created_date'] = pd.to_datetime(assignments_df['created_date'])
                assignments_df = assignments_df[assignments_df['created_date'] >= date_filter_start]
            
            # Text search
            query_lower = query.lower()
            matching_assignments = assignments_df[
                assignments_df['title'].str.lower().str.contains(query_lower, na=False) |
                assignments_df['description'].str.lower().str.contains(query_lower, na=False) |
                assignments_df['creator'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, assignment in matching_assignments.iterrows():
                results.append({
                    'type': 'assignment',
                    'id': assignment['id'],
                    'title': assignment['title'],
                    'content': assignment['description'][:200] + '...' if len(assignment['description']) > 200 else assignment['description'],
                    'author': assignment['creator'],
                    'club': assignment['club'],
                    'created_date': assignment['created_date'],
                    'extra_info': f"마감일: {assignment['due_date'][:10]} | 상태: {assignment['status']}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"과제 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def search_schedules(self, query, club_filter, date_filter_start, user):
        """Search in schedules"""
        try:
            schedule_df = st.session_state.data_manager.load_csv('schedule')
            
            if schedule_df.empty:
                return []
            
            # Apply filters
            if club_filter != "전체":
                schedule_df = schedule_df[schedule_df['club'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                schedule_df = schedule_df[schedule_df['club'].isin(user_club_names)]
            
            # Date filter
            if date_filter_start:
                schedule_df['created_date'] = pd.to_datetime(schedule_df['created_date'])
                schedule_df = schedule_df[schedule_df['created_date'] >= date_filter_start]
            
            # Text search
            query_lower = query.lower()
            matching_schedules = schedule_df[
                schedule_df['title'].str.lower().str.contains(query_lower, na=False) |
                schedule_df['description'].str.lower().str.contains(query_lower, na=False) |
                schedule_df['location'].str.lower().str.contains(query_lower, na=False) |
                schedule_df['creator'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, schedule in matching_schedules.iterrows():
                results.append({
                    'type': 'schedule',
                    'id': schedule['id'],
                    'title': schedule['title'],
                    'content': schedule['description'],
                    'author': schedule['creator'],
                    'club': schedule['club'],
                    'created_date': schedule['created_date'],
                    'extra_info': f"📅 {schedule['date']} ⏰ {schedule['time']} 📍 {schedule['location']}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"일정 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def search_votes(self, query, club_filter, date_filter_start, user):
        """Search in votes"""
        try:
            votes_df = st.session_state.data_manager.load_csv('votes')
            
            if votes_df.empty:
                return []
            
            # Apply filters
            if club_filter != "전체":
                votes_df = votes_df[votes_df['club'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                votes_df = votes_df[votes_df['club'].isin(user_club_names)]
            
            # Date filter
            if date_filter_start:
                votes_df['created_date'] = pd.to_datetime(votes_df['created_date'])
                votes_df = votes_df[votes_df['created_date'] >= date_filter_start]
            
            # Text search
            query_lower = query.lower()
            matching_votes = votes_df[
                votes_df['title'].str.lower().str.contains(query_lower, na=False) |
                votes_df['description'].str.lower().str.contains(query_lower, na=False) |
                votes_df['creator'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, vote in matching_votes.iterrows():
                results.append({
                    'type': 'vote',
                    'id': vote['id'],
                    'title': vote['title'],
                    'content': vote['description'],
                    'author': vote['creator'],
                    'club': vote['club'],
                    'created_date': vote['created_date'],
                    'extra_info': f"마감일: {vote['end_date'][:10]} | 상태: {vote['status']}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"투표 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def search_users(self, query, club_filter, user):
        """Search in users"""
        try:
            users_df = st.session_state.data_manager.load_csv('users')
            
            if users_df.empty:
                return []
            
            # Apply filters
            if club_filter != "전체":
                users_df = users_df[users_df['club_name'] == club_filter]
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = user_clubs['club_name'].tolist()
                users_df = users_df[users_df['club_name'].isin(user_club_names)]
            
            # Text search
            query_lower = query.lower()
            matching_users = users_df[
                users_df['name'].str.lower().str.contains(query_lower, na=False) |
                users_df['username'].str.lower().str.contains(query_lower, na=False) |
                users_df['role'].str.lower().str.contains(query_lower, na=False)
            ]
            
            # Format results
            results = []
            for _, user_row in matching_users.iterrows():
                results.append({
                    'type': 'user',
                    'id': user_row['username'],
                    'title': f"👤 {user_row['name']}",
                    'content': f"사용자명: {user_row['username']} | 역할: {user_row['role']}",
                    'author': user_row['name'],
                    'club': user_row['club_name'],
                    'created_date': user_row['created_date'],
                    'extra_info': f"동아리: {user_row['club_name']} | 역할: {user_row['role']}"
                })
            
            return results
            
        except Exception as e:
            st.error(f"사용자 검색 중 오류가 발생했습니다: {e}")
            return []
    
    def display_search_results(self, results, query):
        """Display search results"""
        st.markdown("---")
        st.markdown(f"### 🔍 '{query}' 검색 결과")
        
        # Count total results
        total_results = sum(len(result_list) for result_list in results.values())
        
        if total_results == 0:
            st.info("검색 결과가 없습니다. 다른 검색어를 시도해보세요.")
            return
        
        st.markdown(f"**총 {total_results}개의 결과를 찾았습니다.**")
        
        # Result type icons
        type_icons = {
            'post': '📝',
            'chat': '💬',
            'assignment': '📚',
            'schedule': '📅',
            'vote': '🗳️',
            'user': '👤'
        }
        
        type_names = {
            'post': '게시글',
            'chat': '채팅',
            'assignment': '과제',
            'schedule': '일정',
            'vote': '투표',
            'user': '사용자'
        }
        
        # Display results by category
        for result_type, result_list in results.items():
            if result_list:
                icon = type_icons.get(result_type, '📄')
                name = type_names.get(result_type, result_type)
                
                st.markdown(f"#### {icon} {name} ({len(result_list)}개)")
                
                for result in result_list:
                    self.display_search_result_item(result, query)
    
    def display_search_result_item(self, result, query):
        """Display a single search result item"""
        # Highlight search terms
        highlighted_title = self.highlight_search_terms(result['title'], query)
        highlighted_content = self.highlight_search_terms(result['content'], query)
        
        # Result type styling
        type_colors = {
            'post': '#FF6B6B',
            'chat': '#4ECDC4',
            'assignment': '#45B7D1',
            'schedule': '#96CEB4',
            'vote': '#FFEAA7',
            'user': '#DDA0DD'
        }
        
        color = type_colors.get(result['type'], '#6c757d')
        
        st.markdown(f"""
        <div style="
            background: white; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 10px 0; 
            border-left: 4px solid {color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h5 style="margin: 0 0 8px 0; color: {color};">{highlighted_title}</h5>
            <p style="color: #666; margin: 8px 0; line-height: 1.4;">{highlighted_content}</p>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <div>
                    <small style="color: #999;">
                        👤 {result['author']} | 🏷️ {result['club']} | 📅 {result['created_date'][:16]}
                    </small>
                </div>
                <div>
                    <small style="color: #666;">{result['extra_info']}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def highlight_search_terms(self, text, query):
        """Highlight search terms in text"""
        if not text or not query:
            return text
        
        # Simple highlighting (case-insensitive)
        import re
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(f'<mark style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">{query}</mark>', str(text))
        
        return highlighted
    
    def show_recent_searches(self, user):
        """Show recent search suggestions"""
        st.markdown("---")
        st.markdown("#### 💡 빠른 검색")
        
        # Quick search buttons for common queries
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 최근 게시글", use_container_width=True):
                recent_results = self.get_recent_posts(user)
                if recent_results:
                    st.markdown("##### 📝 최근 게시글")
                    for post in recent_results[:5]:
                        st.markdown(f"• **{post['title']}** ({post['author']} | {post['created_date'][:10]})")
        
        with col2:
            if st.button("📚 진행 중 과제", use_container_width=True):
                active_assignments = self.get_active_assignments(user)
                if active_assignments:
                    st.markdown("##### 📚 진행 중인 과제")
                    for assignment in active_assignments[:5]:
                        st.markdown(f"• **{assignment['title']}** (마감: {assignment['due_date'][:10]})")
        
        with col3:
            if st.button("📅 다가오는 일정", use_container_width=True):
                upcoming_schedules = self.get_upcoming_schedules(user)
                if upcoming_schedules:
                    st.markdown("##### 📅 다가오는 일정")
                    for schedule in upcoming_schedules[:5]:
                        st.markdown(f"• **{schedule['title']}** ({schedule['date']})")
    
    def show_quick_search_suggestions(self, user):
        """Show quick search suggestions"""
        st.markdown("#### 🏷️ 인기 검색어")
        
        # Generate popular search terms based on recent activity
        suggestions = [
            "공지", "과제", "회의", "프로젝트", "발표", 
            "준비물", "일정", "변경", "마감", "제출"
        ]
        
        # Display as clickable tags
        cols = st.columns(5)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 5]:
                if st.button(f"#{suggestion}", use_container_width=True):
                    # Perform search with the suggestion
                    search_results = self.perform_search(
                        suggestion,
                        ["게시글", "과제", "일정"],
                        "전체",
                        "최근 3개월",
                        user
                    )
                    self.display_search_results(search_results, suggestion)
    
    def get_recent_posts(self, user):
        """Get recent posts for quick search"""
        try:
            posts_df = st.session_state.data_manager.load_csv('posts')
            
            if posts_df.empty:
                return []
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                posts_df = posts_df[posts_df['club'].isin(user_club_names)]
            
            posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
            recent_posts = posts_df.sort_values('created_date', ascending=False).head(10)
            
            return recent_posts.to_dict('records')
            
        except:
            return []
    
    def get_active_assignments(self, user):
        """Get active assignments for quick search"""
        try:
            assignments_df = st.session_state.data_manager.load_csv('assignments')
            
            if assignments_df.empty:
                return []
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                assignments_df = assignments_df[assignments_df['club'].isin(user_club_names)]
            
            active_assignments = assignments_df[assignments_df['status'] == '활성']
            active_assignments['due_date'] = pd.to_datetime(active_assignments['due_date'])
            active_assignments = active_assignments.sort_values('due_date')
            
            return active_assignments.to_dict('records')
            
        except:
            return []
    
    def get_upcoming_schedules(self, user):
        """Get upcoming schedules for quick search"""
        try:
            schedule_df = st.session_state.data_manager.load_csv('schedule')
            
            if schedule_df.empty:
                return []
            
            # Filter by user's accessible clubs if not teacher
            if user['role'] != '선생님':
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                user_club_names = ["전체"] + user_clubs['club_name'].tolist()
                schedule_df = schedule_df[schedule_df['club'].isin(user_club_names)]
            
            from datetime import date
            today = date.today()
            schedule_df['date'] = pd.to_datetime(schedule_df['date']).dt.date
            upcoming_schedules = schedule_df[schedule_df['date'] >= today]
            upcoming_schedules = upcoming_schedules.sort_values('date').head(10)
            
            return upcoming_schedules.to_dict('records')
            
        except:
            return []
