import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
from PIL import Image
import io

class GallerySystem:
    def __init__(self):
        self.data_manager = None
    
    def initialize_gallery_files(self):
        """Initialize gallery-related CSV files"""
        if not hasattr(st.session_state, 'data_manager'):
            return
        
        self.data_manager = st.session_state.data_manager
        
        # Gallery CSV structure
        gallery_headers = ['id', 'title', 'description', 'image_path', 'uploader', 'club', 'tags', 'likes', 'created_date']
        
        # Initialize if not exists
        gallery_df = self.data_manager.load_csv('gallery')
        if gallery_df.empty:
            gallery_df = pd.DataFrame(columns=gallery_headers)
            self.data_manager.save_csv('gallery', gallery_df)
    
    def show_gallery_interface(self, user):
        """Display the gallery interface"""
        self.initialize_gallery_files()
        
        st.markdown("### 🖼️ 갤러리")
        
        # Note about gallery-board integration
        st.info("📋 갤러리 기능이 게시판과 통합되었습니다. 게시판 탭에서 이미지를 업로드하고 공유할 수 있습니다.")
        
        # Upload section
        if st.button("📝 게시판에서 이미지 업로드하기"):
            st.session_state.redirect_to_board = True
            st.info("게시판 탭으로 이동하여 이미지가 포함된 게시글을 작성해보세요!")
        
        # Display existing gallery items from board posts
        self.show_gallery_from_posts(user)
    
    def show_gallery_from_posts(self, user):
        """Display gallery items from board posts with images"""
        posts_df = self.data_manager.load_csv('posts')
        
        if posts_df.empty:
            st.info("아직 업로드된 이미지가 없습니다.")
            return
        
        # Filter posts with images
        image_posts = posts_df[posts_df['image_data'].notna() & (posts_df['image_data'] != '')]
        
        if image_posts.empty:
            st.info("아직 이미지가 포함된 게시글이 없습니다.")
            return
        
        st.markdown("#### 📸 이미지 갤러리")
        
        # Display in grid format
        cols = st.columns(3)
        for idx, (_, post) in enumerate(image_posts.iterrows()):
            with cols[idx % 3]:
                self.show_gallery_item(post, user)
    
    def show_gallery_item(self, post, user):
        """Display a single gallery item"""
        try:
            # Display image
            if post['image_data']:
                image_data = base64.b64decode(post['image_data'])
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption=post['title'][:50], use_column_width=True)
            
            # Post info
            st.markdown(f"""
            <div style="background: white; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h4 style="margin: 0; color: #FF6B6B;">{post['title']}</h4>
                <p style="margin: 5px 0; color: #666; font-size: 12px;">
                    👤 {post['author']} | 🏷️ {post['club']}<br>
                    📅 {post['created_date'][:16] if isinstance(post['created_date'], str) else str(post['created_date'])[:16]}
                </p>
                <p style="margin: 5px 0; font-size: 14px;">{post['content'][:100]}{'...' if len(str(post['content'])) > 100 else ''}</p>
                <p style="margin: 5px 0; color: #FF6B6B;">❤️ {post.get('likes', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"이미지 표시 중 오류가 발생했습니다: {str(e)}")
    
    def process_uploaded_image(self, uploaded_file):
        """Process uploaded image and return base64 encoded string"""
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                
                # Resize image if too large
                max_size = (800, 600)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                image_data = base64.b64encode(buffer.getvalue()).decode()
                
                return image_data
            except Exception as e:
                st.error(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
                return None
        return None