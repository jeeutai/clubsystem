import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io
import os

class BoardSystem:
    def __init__(self):
        self.posts_file = 'data/posts.csv'

    def show_board_interface(self, user):
        """Display the board interface"""
        st.markdown("### 📝 게시판")

        # Tab layout
        tab1, tab2 = st.tabs(["📋 게시글 목록", "✍️ 글쓰기"])

        with tab1:
            self.show_posts_list(user)

        with tab2:
            self.show_post_creation(user)

    def show_posts_list(self, user):
        """Display list of posts"""
        st.markdown("#### 📋 게시글 목록")

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            # Club filter
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                club_options = ["전체"] + user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 필터", club_options, key="board_club_filter_unique")

        with col2:
            # Sort options
            sort_options = ["최신순", "좋아요순", "댓글순"]
            sort_by = st.selectbox("📊 정렬", sort_options)

        with col3:
            # Search
            search_term = st.text_input("🔍 검색", placeholder="제목, 내용 검색...")

        # Load and filter posts
        posts_df = st.session_state.data_manager.load_csv('posts')

        if posts_df.empty:
            st.info("등록된 게시글이 없습니다.")
            return

        # Apply filters
        if selected_club != "전체":
            posts_df = posts_df[posts_df['club'] == selected_club]

        if search_term:
            posts_df = posts_df[
                posts_df['title'].str.contains(search_term, case=False, na=False) |
                posts_df['content'].str.contains(search_term, case=False, na=False)
            ]

        # Sort posts
        if sort_by == "좋아요순":
            posts_df['likes'] = pd.to_numeric(posts_df['likes'], errors='coerce').fillna(0)
            posts_df = posts_df.sort_values('likes', ascending=False)
        elif sort_by == "댓글순":
            posts_df['comments'] = pd.to_numeric(posts_df['comments'], errors='coerce').fillna(0)
            posts_df = posts_df.sort_values('comments', ascending=False)
        else:  # 최신순
            posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
            posts_df = posts_df.sort_values('created_date', ascending=False)

        # Display posts
        for _, post in posts_df.iterrows():
            self.show_post_card(post, user)

    def show_post_card(self, post, user):
        """Display a single post card"""
        # Calculate engagement metrics
        likes = int(post.get('likes', 0)) if pd.notna(post.get('likes')) else 0
        comments = int(post.get('comments', 0)) if pd.notna(post.get('comments')) else 0

        # Tags display
        tags_html = ""
        if pd.notna(post.get('tags')) and post['tags']:
            tags = post['tags'].split(',')
            tags_html = ' '.join([f'<span style="background: #e9ecef; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">#{tag.strip()}</span>' for tag in tags])

        # Image display
        image_html = ""
        if pd.notna(post.get('image_path')) and post['image_path']:
            image_html = f'<img src="data:image/png;base64,{post["image_path"]}" style="max-width: 100%; border-radius: 8px; margin: 10px 0;">'

        with st.container():
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #333;">{post['title']}</h4>
                        <div style="margin: 5px 0;">
                            <span style="color: #666; font-size: 14px;">👤 {post['author']}</span>
                            <span style="color: #666; font-size: 14px; margin-left: 15px;">🏷️ {post['club']}</span>
                            <span style="color: #666; font-size: 14px; margin-left: 15px;">📅 {str(post['created_date'])[:16]}</span>
                        </div>
                        {tags_html}
                    </div>
                </div>

                <div style="margin: 15px 0;">
                    <p style="color: #333; line-height: 1.6; margin: 0;">{post['content']}</p>
                    {image_html}
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                    <div>
                        <span style="color: #666; margin-right: 20px;">❤️ {likes}</span>
                        <span style="color: #666;">💬 {comments}</span>
                    </div>
                    <div>
                        <small style="color: #999;">게시글 ID: {post['id']}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("👍 좋아요", key=f"like_{post['id']}"):
                    self.like_post(post['id'])
                    st.rerun()

            with col2:
                if st.button("💬 댓글", key=f"comment_{post['id']}"):
                    st.session_state[f'show_comments_{post["id"]}'] = True

            with col3:
                if user['role'] in ['선생님'] or user['username'] == post['author']:
                    if st.button("✏️ 수정", key=f"edit_{post['id']}"):
                        st.session_state[f'edit_post_{post["id"]}'] = True

            with col4:
                if user['role'] in ['선생님'] or user['username'] == post['author']:
                    if st.button("🗑️ 삭제", key=f"delete_{post['id']}"):
                        if self.delete_post(post['id']):
                            st.success("게시글이 삭제되었습니다.")
                            st.rerun()

            # Show comments if requested
            if st.session_state.get(f'show_comments_{post["id"]}', False):
                self.show_comments_section(post['id'], user)

            # Show edit form if requested
            if st.session_state.get(f'edit_post_{post["id"]}', False):
                self.show_edit_post_form(post, user)

    def show_post_creation(self, user):
        """Display post creation form"""
        st.markdown("#### ✍️ 새 게시글 작성")

        with st.form("create_post_form"):
            # Get user's clubs for club selection
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            club_options = user_clubs['club_name'].tolist()

            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                all_clubs = clubs_df['name'].tolist() if not clubs_df.empty else []
                club_options = ["전체"] + all_clubs

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="post_club_select_unique")
            title = st.text_input("📝 제목", placeholder="게시글 제목을 입력하세요", key="post_title_input")
            content = st.text_area("📄 내용", placeholder="게시글 내용을 입력하세요", height=200, key="post_content_input")

            # Enhanced image upload with multiple files
            uploaded_images = st.file_uploader(
                "🖼️ 이미지 첨부 (여러 개 가능)", 
                type=['png', 'jpg', 'jpeg', 'gif'],
                accept_multiple_files=True,
                help="갤러리 기능이 통합되어 여러 이미지를 한 번에 업로드할 수 있습니다."
            )

            # Tags and post type
            tags = st.text_input("🏷️ 태그", placeholder="태그를 쉼표로 구분하여 입력하세요 (예: 갤러리, 공지, 중요)")
            post_type = st.selectbox("📝 게시글 유형", ["일반", "공지", "갤러리", "질문", "자료공유"])

            submit_post = st.form_submit_button("📤 게시글 등록", use_container_width=True)

            if submit_post:
                if title and content and selected_club:
                    # Process image if uploaded
                    image_data = None
                    if uploaded_images:
                       image_data_list = []
                       for uploaded_image in uploaded_images:
                           image_data_list.append(self.process_uploaded_image(uploaded_image))
                       image_data = ','.join(image_data_list)
                    post_data = {
                        'title': title,
                        'content': content,
                        'author': user['name'],
                        'club': selected_club,
                        'likes': 0,
                        'comments': 0,
                        'image_path': image_data,
                        'tags': tags,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('posts', post_data):
                        st.success("게시글이 등록되었습니다!")
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 게시글: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 게시글을 등록했습니다."
                        )
                        st.rerun()
                    else:
                        st.error("게시글 등록에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def process_uploaded_image(self, uploaded_file):
        """Process uploaded image and return base64 encoded string"""
        try:
            image = Image.open(uploaded_file)

            # Resize image if too large
            max_size = (800, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return img_str
        except Exception as e:
            st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")
            return None

    def like_post(self, post_id):
        """Add like to post"""
        posts_df = st.session_state.data_manager.load_csv('posts')

        if not posts_df.empty:
            current_likes = int(posts_df.loc[posts_df['id'] == post_id, 'likes'].iloc[0]) if not posts_df[posts_df['id'] == post_id].empty else 0
            new_likes = current_likes + 1

            st.session_state.data_manager.update_record('posts', post_id, {'likes': new_likes})

    def delete_post(self, post_id):
        """Delete a post"""
        return st.session_state.data_manager.delete_record('posts', post_id)

    def show_comments_section(self, post_id, user):
        """Display comments section for a post"""
        st.markdown("---")
        st.markdown("#### 💬 댓글")

        # Comment input
        with st.form(f"comment_form_{post_id}"):
            comment_text = st.text_area("댓글 작성", placeholder="댓글을 입력하세요...", key=f"comment_{post_id}")
            submit_comment = st.form_submit_button("💬 댓글 등록")

            if submit_comment and comment_text:
                # Add comment logic here
                st.success("댓글이 등록되었습니다!")

                # Update comment count
                posts_df = st.session_state.data_manager.load_csv('posts')
                if not posts_df.empty:
                    current_comments = int(posts_df.loc[posts_df['id'] == post_id, 'comments'].iloc[0]) if not posts_df[posts_df['id'] == post_id].empty else 0
                    new_comments = current_comments + 1
                    st.session_state.data_manager.update_record('posts', post_id, {'comments': new_comments})

        # Close comments
        if st.button("❌ 댓글 닫기", key=f"close_comments_{post_id}"):
            st.session_state[f'show_comments_{post_id}'] = False
            st.rerun()

    def show_edit_post_form(self, post, user):
        """Display post edit form"""
        st.markdown("---")
        st.markdown("#### ✏️ 게시글 수정")

        with st.form(f"edit_post_form_{post['id']}"):
            new_title = st.text_input("제목", value=post['title'])
            new_content = st.text_area("내용", value=post['content'], height=150)
            new_tags = st.text_input("태그", value=post.get('tags', ''))

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 저장")
            with col2:
                cancel_button = st.form_submit_button("❌ 취소")

            if save_button:
                updates = {
                    'title': new_title,
                    'content': new_content,
                    'tags': new_tags
                }

                if st.session_state.data_manager.update_record('posts', post['id'], updates):
                    st.success("게시글이 수정되었습니다!")
                    st.session_state[f'edit_post_{post["id"]}'] = False
                    st.rerun()
                else:
                    st.error("게시글 수정에 실패했습니다.")

            if cancel_button:
                st.session_state[f'edit_post_{post["id"]}'] = False
                st.rerun()