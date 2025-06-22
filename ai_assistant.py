
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import random

class AIAssistant:
    def __init__(self):
        self.responses = {
            "greeting": [
                "안녕하세요! 폴라리스반 AI 어시스턴트입니다. 무엇을 도와드릴까요?",
                "반갑습니다! 동아리 활동에 대해 궁금한 것이 있으시면 언제든 물어보세요!",
                "안녕하세요! 오늘도 열심히 활동하시는 모습이 멋져요!"
            ],
            "attendance": [
                "출석률을 높이려면 매일 일정한 시간에 체크인하는 습관을 만들어보세요!",
                "연속 출석 목표를 설정하고 달성해보는 것은 어떨까요?",
                "출석 알림을 설정해서 빠뜨리지 않도록 도움을 받아보세요!"
            ],
            "study": [
                "학습 계획을 세우고 단계별로 진행해보세요!",
                "동아리 친구들과 스터디 그룹을 만들어보는 것은 어떨까요?",
                "과제는 미리미리 준비하는 것이 좋아요!"
            ]
        }

    def show_ai_interface(self, user):
        """AI 어시스턴트 인터페이스 표시"""
        st.markdown("### 🤖 AI 어시스턴트")
        
        # AI 어시스턴트 소개
        with st.expander("🤖 AI 어시스턴트 소개", expanded=False):
            st.markdown("""
            **폴라리스반 AI 어시스턴트**는 여러분의 동아리 활동을 도와주는 똑똑한 도우미입니다!
            
            **주요 기능:**
            - 📊 학습 분석 및 조언
            - 🎯 개인 맞춤 추천
            - 📅 일정 관리 도움
            - 🏆 목표 설정 지원
            - 💡 창의적 아이디어 제안
            """)
        
        # 채팅 인터페이스
        st.markdown("#### 💬 AI와 대화하기")
        
        # 채팅 히스토리 표시
        if 'ai_chat_history' not in st.session_state:
            st.session_state.ai_chat_history = []
        
        # 채팅 기록 표시
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.ai_chat_history:
                if message['sender'] == 'user':
                    st.markdown(f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <div style="background: #007bff; color: white; padding: 10px; border-radius: 15px; display: inline-block; max-width: 70%;">
                            {message['content']}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            {message['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="background: #f1f3f4; color: #333; padding: 10px; border-radius: 15px; display: inline-block; max-width: 70%;">
                            🤖 {message['content']}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            {message['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 사용자 입력
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("메시지를 입력하세요...", key="ai_chat_input", label_visibility="collapsed")
        with col2:
            send_button = st.button("전송", use_container_width=True)
        
        # 빠른 질문 버튼들
        st.markdown("##### 🚀 빠른 질문")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 내 출석률은?"):
                user_input = "내 출석률을 알려줘"
                send_button = True
        
        with col2:
            if st.button("🎯 학습 조언"):
                user_input = "학습 방법을 추천해줘"
                send_button = True
        
        with col3:
            if st.button("📅 일정 도움"):
                user_input = "일정 관리 도움이 필요해"
                send_button = True
        
        with col4:
            if st.button("💡 아이디어"):
                user_input = "창의적인 아이디어를 제안해줘"
                send_button = True
        
        # 메시지 처리
        if send_button and user_input:
            # 사용자 메시지 추가
            st.session_state.ai_chat_history.append({
                'sender': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime('%H:%M')
            })
            
            # AI 응답 생성
            ai_response = self.generate_ai_response(user_input, user)
            
            # AI 응답 추가
            st.session_state.ai_chat_history.append({
                'sender': 'ai',
                'content': ai_response,
                'timestamp': datetime.now().strftime('%H:%M')
            })
            
            st.rerun()
        
        # AI 분석 대시보드
        st.markdown("---")
        st.markdown("#### 📊 AI 분석 대시보드")
        
        tabs = st.tabs(["🎯 개인 분석", "📈 추세 예측", "💡 맞춤 추천", "🏆 목표 설정"])
        
        with tabs[0]:
            self.show_personal_analysis(user)
        
        with tabs[1]:
            self.show_trend_prediction(user)
        
        with tabs[2]:
            self.show_personalized_recommendations(user)
        
        with tabs[3]:
            self.show_goal_suggestions(user)

    def generate_ai_response(self, user_input, user):
        """AI 응답 생성"""
        input_lower = user_input.lower()
        
        # 출석 관련 질문
        if any(keyword in input_lower for keyword in ['출석', '출석률', '참석']):
            return self.get_attendance_response(user)
        
        # 학습 관련 질문
        elif any(keyword in input_lower for keyword in ['학습', '공부', '과제', '퀴즈']):
            return self.get_study_response(user)
        
        # 일정 관련 질문
        elif any(keyword in input_lower for keyword in ['일정', '스케줄', '계획']):
            return self.get_schedule_response(user)
        
        # 동아리 관련 질문
        elif any(keyword in input_lower for keyword in ['동아리', '활동', '참여']):
            return self.get_club_response(user)
        
        # 인사말
        elif any(keyword in input_lower for keyword in ['안녕', '안녕하세요', '반가워', '처음']):
            return random.choice(self.responses["greeting"])
        
        # 기본 응답
        else:
            return self.get_general_response(user_input, user)

    def get_attendance_response(self, user):
        """출석 관련 응답"""
        # 실제 출석 데이터 조회
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        if not user_attendance.empty:
            total_days = len(user_attendance)
            present_days = len(user_attendance[user_attendance['status'] == '출석'])
            rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            if rate >= 90:
                return f"와! 출석률이 {rate:.1f}%네요! 정말 성실하시군요! 🌟 이 조자로 계속 유지해주세요!"
            elif rate >= 80:
                return f"출석률이 {rate:.1f}%입니다. 좋은 편이에요! 조금만 더 노력하면 90% 달성 가능해요! 💪"
            elif rate >= 70:
                return f"출석률이 {rate:.1f}%입니다. 개선이 필요해 보여요. 알림 설정을 활용해보시는 건 어떨까요? 📱"
            else:
                return f"출석률이 {rate:.1f}%입니다. 함께 개선 계획을 세워볼까요? 작은 목표부터 시작해보세요! 🎯"
        else:
            return "아직 출석 기록이 없네요! 첫 출석을 시작해보시는 건 어떨까요? 시작이 반이에요! 🚀"

    def get_study_response(self, user):
        """학습 관련 응답"""
        # 과제 및 퀴즈 데이터 조회
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        
        pending_assignments = len(assignments_df) if not assignments_df.empty else 0
        total_quizzes = len(quizzes_df) if not quizzes_df.empty else 0
        
        responses = [
            f"현재 {pending_assignments}개의 과제가 있어요. 계획적으로 진행해보세요! 📚",
            "학습할 때는 25분 집중 + 5분 휴식 방법을 써보세요! (포모도로 기법) 🍅",
            "동아리 친구들과 함께 스터디하면 더 효과적일 거예요! 👥",
            "어려운 내용은 작은 단위로 나누어 학습해보세요! 🧩"
        ]
        
        return random.choice(responses)

    def get_schedule_response(self, user):
        """일정 관련 응답"""
        schedule_df = st.session_state.data_manager.load_csv('schedule')
        today = date.today()
        
        if not schedule_df.empty:
            today_schedules = schedule_df[schedule_df['date'] == today.strftime('%Y-%m-%d')]
            upcoming_count = len(today_schedules)
            
            if upcoming_count > 0:
                return f"오늘 {upcoming_count}개의 일정이 있어요! 미리 준비하셨나요? 📅✨"
            else:
                return "오늘은 예정된 일정이 없네요. 개인 학습 시간으로 활용해보시는 건 어떨까요? 📖"
        
        return "일정 관리는 성공의 열쇠예요! 우선순위를 정해서 계획을 세워보세요! 🗓️"

    def get_club_response(self, user):
        """동아리 관련 응답"""
        user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        
        if not user_clubs.empty:
            club_count = len(user_clubs)
            return f"{club_count}개 동아리에서 활동 중이시군요! 다양한 경험이 소중한 자산이 될 거예요! 🌟"
        else:
            return "동아리 활동을 시작해보세요! 새로운 친구들과 흥미로운 경험을 할 수 있어요! 🎭"

    def get_general_response(self, user_input, user):
        """일반적인 응답"""
        general_responses = [
            "흥미로운 질문이네요! 더 구체적으로 설명해주시면 도움을 드릴 수 있어요! 🤔",
            "좋은 생각이에요! 함께 해결 방법을 찾아볼까요? 💡",
            "그 부분에 대해 더 자세히 알려주시면 맞춤형 조언을 드릴 수 있어요! 📋",
            "멋진 아이디어네요! 실행 계획을 함께 세워볼까요? 🚀"
        ]
        
        return random.choice(general_responses)

    def show_personal_analysis(self, user):
        """개인 분석 표시"""
        st.markdown("##### 🎯 개인 맞춤 분석")
        
        # 출석 패턴 분석
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        if not user_attendance.empty:
            # 요일별 출석 패턴
            user_attendance['date'] = pd.to_datetime(user_attendance['date'])
            user_attendance['weekday'] = user_attendance['date'].dt.day_name()
            
            weekday_pattern = user_attendance.groupby('weekday')['status'].apply(
                lambda x: (x == '출석').sum() / len(x) * 100
            )
            
            if not weekday_pattern.empty:
                st.markdown("**📊 요일별 출석 패턴**")
                for day, rate in weekday_pattern.items():
                    st.write(f"- {day}: {rate:.1f}%")
                
                best_day = weekday_pattern.idxmax()
                worst_day = weekday_pattern.idxmin()
                
                st.info(f"💡 **분석 결과**: {best_day}에 가장 출석률이 높고, {worst_day}에 가장 낮아요!")
        
        # 학습 활동 분석
        assignments_df = st.session_state.data_manager.load_csv('submissions')
        user_submissions = assignments_df[assignments_df['username'] == user['username']] if not assignments_df.empty else pd.DataFrame()
        
        if not user_submissions.empty:
            st.markdown("**📚 학습 활동 분석**")
            total_submissions = len(user_submissions)
            on_time_submissions = len(user_submissions[user_submissions.get('status', '') == 'on_time'])
            
            punctuality_rate = (on_time_submissions / total_submissions * 100) if total_submissions > 0 else 0
            
            st.write(f"- 총 제출: {total_submissions}회")
            st.write(f"- 정시 제출률: {punctuality_rate:.1f}%")
            
            if punctuality_rate >= 80:
                st.success("🌟 시간 관리를 잘 하고 계시네요!")
            else:
                st.warning("⏰ 시간 관리 개선이 필요해 보여요!")

    def show_trend_prediction(self, user):
        """추세 예측 표시"""
        st.markdown("##### 📈 AI 추세 예측")
        
        # 출석률 예측 (간단한 예측 모델)
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        if len(user_attendance) >= 5:
            recent_attendance = user_attendance.tail(10)
            present_count = len(recent_attendance[recent_attendance['status'] == '출석'])
            recent_rate = (present_count / len(recent_attendance)) * 100
            
            # 간단한 추세 계산
            if len(user_attendance) >= 10:
                older_attendance = user_attendance.tail(20).head(10)
                older_present = len(older_attendance[older_attendance['status'] == '출석'])
                older_rate = (older_present / len(older_attendance)) * 100
                
                trend = recent_rate - older_rate
                
                if trend > 5:
                    st.success(f"📈 출석률이 {trend:.1f}% 상승 추세예요! 훌륭해요!")
                elif trend < -5:
                    st.warning(f"📉 출석률이 {abs(trend):.1f}% 하락 추세입니다. 주의가 필요해요!")
                else:
                    st.info("📊 출석률이 안정적으로 유지되고 있어요!")
                
                # 예측
                predicted_rate = recent_rate + (trend * 0.5)  # 간단한 예측
                st.write(f"🔮 **다음 주 예상 출석률**: {predicted_rate:.1f}%")
        
        else:
            st.info("더 많은 데이터가 축적되면 정확한 예측을 제공할 수 있어요!")

    def show_personalized_recommendations(self, user):
        """개인 맞춤 추천"""
        st.markdown("##### 💡 AI 맞춤 추천")
        
        recommendations = []
        
        # 출석 기반 추천
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        if not user_attendance.empty:
            recent_attendance = user_attendance.tail(7)
            absent_count = len(recent_attendance[recent_attendance['status'] == '결석'])
            
            if absent_count > 2:
                recommendations.append({
                    'icon': '⏰',
                    'title': '출석 알림 설정',
                    'description': '최근 결석이 많아요. 출석 알림을 설정해보세요!',
                    'priority': 'high'
                })
            
            late_count = len(recent_attendance[recent_attendance['status'] == '지각'])
            if late_count > 1:
                recommendations.append({
                    'icon': '🕐',
                    'title': '시간 관리 개선',
                    'description': '지각을 줄이기 위해 일찍 출발하는 습관을 만들어보세요!',
                    'priority': 'medium'
                })
        
        # 학습 기반 추천
        user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        if not user_clubs.empty:
            recommendations.append({
                'icon': '📚',
                'title': '스터디 그룹 참여',
                'description': f'{user_clubs.iloc[0]["club_name"]} 동아리 스터디 그룹에 참여해보세요!',
                'priority': 'medium'
            })
        
        # 목표 달성 추천
        recommendations.append({
            'icon': '🎯',
            'title': '주간 목표 설정',
            'description': '이번 주 달성하고 싶은 구체적인 목표를 설정해보세요!',
            'priority': 'low'
        })
        
        # 추천 표시
        for rec in recommendations:
            priority_color = {'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745'}
            
            st.markdown(f"""
            <div style="border-left: 4px solid {priority_color[rec['priority']]}; padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 5px;">
                <h5>{rec['icon']} {rec['title']}</h5>
                <p style="margin: 5px 0; color: #555;">{rec['description']}</p>
                <small style="color: #666;">우선순위: {rec['priority'].upper()}</small>
            </div>
            """, unsafe_allow_html=True)

    def show_goal_suggestions(self, user):
        """목표 설정 제안"""
        st.markdown("##### 🏆 AI 목표 설정 도우미")
        
        # 현재 상태 분석
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_attendance = attendance_df[attendance_df['username'] == user['username']]
        
        current_stats = self.analyze_current_performance(user_attendance, user)
        
        # 맞춤형 목표 제안
        suggested_goals = []
        
        if current_stats['attendance_rate'] < 80:
            suggested_goals.append({
                'category': '출석',
                'goal': '이번 달 출석률 85% 달성',
                'current': f"{current_stats['attendance_rate']:.1f}%",
                'target': '85%',
                'difficulty': 'realistic'
            })
        elif current_stats['attendance_rate'] < 90:
            suggested_goals.append({
                'category': '출석',
                'goal': '이번 달 출석률 95% 달성',
                'current': f"{current_stats['attendance_rate']:.1f}%",
                'target': '95%',
                'difficulty': 'challenging'
            })
        else:
            suggested_goals.append({
                'category': '출석',
                'goal': '완벽한 출석률 100% 유지',
                'current': f"{current_stats['attendance_rate']:.1f}%",
                'target': '100%',
                'difficulty': 'expert'
            })
        
        # 학습 목표
        suggested_goals.append({
            'category': '학습',
            'goal': '이번 주 과제 100% 정시 제출',
            'current': '분석중',
            'target': '100%',
            'difficulty': 'realistic'
        })
        
        # 참여 목표
        suggested_goals.append({
            'category': '참여',
            'goal': '동아리 활동 적극 참여',
            'current': '분석중',
            'target': '주 3회 이상',
            'difficulty': 'realistic'
        })
        
        # 목표 표시
        for goal in suggested_goals:
            difficulty_color = {'realistic': '#28a745', 'challenging': '#ffc107', 'expert': '#dc3545'}
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding: 15px; border: 1px solid #ddd; border-radius: 10px; margin: 10px 0;">
                    <h5>🎯 {goal['goal']}</h5>
                    <p><strong>현재:</strong> {goal['current']} → <strong>목표:</strong> {goal['target']}</p>
                    <span style="background: {difficulty_color[goal['difficulty']]}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                        {goal['difficulty'].upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("목표 설정", key=f"set_goal_{goal['category']}"):
                    self.set_user_goal(user['username'], goal)
                    st.success("목표가 설정되었습니다!")
        
        # 목표 달성 팁
        st.markdown("##### 💡 목표 달성 팁")
        
        tips = [
            "🎯 구체적이고 측정 가능한 목표를 설정하세요",
            "📅 마감일을 정해서 긴박감을 만들어보세요",
            "📊 정기적으로 진행 상황을 확인하세요",
            "🎉 작은 성취도 축하하며 동기를 유지하세요",
            "👥 친구들과 목표를 공유해서 서로 격려하세요"
        ]
        
        for tip in tips:
            st.write(tip)

    def analyze_current_performance(self, attendance_data, user):
        """현재 성과 분석"""
        if attendance_data.empty:
            return {'attendance_rate': 0, 'streak': 0, 'trend': 'stable'}
        
        # 최근 30일 데이터
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_data = attendance_data[pd.to_datetime(attendance_data['date']) >= thirty_days_ago]
        
        if recent_data.empty:
            return {'attendance_rate': 0, 'streak': 0, 'trend': 'stable'}
        
        # 출석률 계산
        present_count = len(recent_data[recent_data['status'] == '출석'])
        total_count = len(recent_data)
        attendance_rate = (present_count / total_count * 100) if total_count > 0 else 0
        
        # 연속 출석 계산 (간단 버전)
        streak = 0
        recent_sorted = recent_data.sort_values('date', ascending=False)
        for _, record in recent_sorted.iterrows():
            if record['status'] == '출석':
                streak += 1
            else:
                break
        
        return {
            'attendance_rate': attendance_rate,
            'streak': streak,
            'trend': 'improving'  # 실제로는 더 복잡한 계산 필요
        }

    def set_user_goal(self, username, goal):
        """사용자 목표 설정"""
        # 실제로는 데이터베이스에 저장
        goal_data = {
            'username': username,
            'category': goal['category'],
            'goal': goal['goal'],
            'target': goal['target'],
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active'
        }
        
        # 목표 데이터 저장 (실제 구현 필요)
        return True
import streamlit as st
import pandas as pd
from datetime import datetime
import random

class AIAssistant:
    def __init__(self):
        self.responses = {
            "출석": [
                "오늘도 출석해주셔서 감사합니다! 🎉",
                "꾸준한 출석이 성공의 열쇠입니다! 💪",
                "훌륭한 출석률을 유지하고 계시네요! ⭐"
            ],
            "지각": [
                "지각하셨군요. 다음에는 좀 더 일찍 와주세요! ⏰",
                "시간 관리에 신경써보세요. 응원합니다! 📅",
                "지각보다는 출석이 좋겠어요! 화이팅! 🔥"
            ],
            "결석": [
                "결석하셨네요. 괜찮으신가요? 😟",
                "건강 관리 잘 하시고 다음에는 만나요! 🏥",
                "몸조리 잘 하시고 빨리 회복하세요! 💊"
            ]
        }
    
    def get_smart_response(self, status, username):
        """상황에 맞는 스마트 응답 생성"""
        if status in self.responses:
            return random.choice(self.responses[status])
        return "좋은 하루 되세요! 😊"
    
    def analyze_attendance_pattern(self, username):
        """출석 패턴 분석 및 조언"""
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        user_data = attendance_df[attendance_df['username'] == username]
        
        if user_data.empty:
            return "아직 출석 기록이 없어 분석할 수 없습니다."
        
        recent_data = user_data.tail(10)
        present_rate = (recent_data['status'] == '출석').mean() * 100
        
        if present_rate >= 90:
            return "🌟 완벽한 출석률입니다! 이 상태를 유지하세요!"
        elif present_rate >= 70:
            return "📈 출석률이 괜찮지만 더 개선할 수 있어요!"
        else:
            return "⚠️ 출석률 개선이 필요합니다. 목표를 세워보세요!"
    
    def suggest_improvement(self, username):
        """개선 제안"""
        suggestions = [
            "매일 같은 시간에 알림을 설정해보세요! ⏰",
            "출석 목표를 세우고 달성해보세요! 🎯",
            "친구와 함께 출석 챌린지를 해보는 건 어떨까요? 👥",
            "출석할 때마다 작은 보상을 정해보세요! 🎁"
        ]
        return random.choice(suggestions)
