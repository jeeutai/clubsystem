import streamlit as st
import pandas as pd
import zipfile
import os
import io
from datetime import datetime
import json

class BackupSystem:
    def __init__(self):
        self.data_manager = None
    
    def initialize_backup_system(self):
        """Initialize backup system"""
        if hasattr(st.session_state, 'data_manager'):
            self.data_manager = st.session_state.data_manager
    
    def show_backup_interface(self, user):
        """Display backup interface"""
        self.initialize_backup_system()
        
        if user['role'] != '선생님':
            st.warning("백업 기능은 관리자만 사용할 수 있습니다.")
            return
        
        st.markdown("### 💾 데이터 백업 및 복원")
        
        tab1, tab2, tab3 = st.tabs(["📥 백업 생성", "📤 백업 복원", "📊 백업 관리"])
        
        with tab1:
            self.show_backup_creation()
        
        with tab2:
            self.show_backup_restore()
        
        with tab3:
            self.show_backup_management()
    
    def show_backup_creation(self):
        """Display backup creation interface"""
        st.markdown("#### 📥 시스템 백업 생성")
        
        col1, col2 = st.columns(2)
        
        with col1:
            backup_type = st.selectbox("백업 유형", [
                "전체 백업",
                "사용자 데이터만",
                "게시판 데이터만",
                "과제 데이터만",
                "선택적 백업"
            ])
        
        with col2:
            include_images = st.checkbox("이미지 포함", value=True)
            compress_backup = st.checkbox("압축", value=True)
        
        backup_description = st.text_area("백업 설명 (선택사항)")
        
        if st.button("🗂️ 백업 생성", use_container_width=True):
            with st.spinner("백업을 생성하는 중..."):
                backup_file = self.create_backup(backup_type, include_images, compress_backup, backup_description)
                
                if backup_file:
                    st.success("백업이 성공적으로 생성되었습니다!")
                    
                    # Download button
                    with open(backup_file, 'rb') as f:
                        st.download_button(
                            label="📥 백업 파일 다운로드",
                            data=f.read(),
                            file_name=os.path.basename(backup_file),
                            mime='application/zip'
                        )
    
    def show_backup_restore(self):
        """Display backup restore interface"""
        st.markdown("#### 📤 백업 복원")
        
        st.warning("⚠️ 백업 복원은 현재 데이터를 덮어씁니다. 신중하게 진행하세요.")
        
        uploaded_file = st.file_uploader(
            "백업 파일 선택",
            type=['zip'],
            help="ZIP 형태의 백업 파일을 업로드하세요."
        )
        
        if uploaded_file:
            st.info(f"업로드된 파일: {uploaded_file.name}")
            
            restore_options = st.multiselect(
                "복원할 데이터 선택",
                ["사용자 계정", "게시판", "과제", "퀴즈", "채팅", "일정", "투표", "출석"],
                default=["사용자 계정", "게시판", "과제"]
            )
            
            confirm_restore = st.checkbox("복원을 진행하겠습니다. (기존 데이터가 손실될 수 있습니다)")
            
            if confirm_restore and st.button("🔄 백업 복원", use_container_width=True):
                with st.spinner("백업을 복원하는 중..."):
                    success = self.restore_backup(uploaded_file, restore_options)
                    
                    if success:
                        st.success("백업이 성공적으로 복원되었습니다!")
                        st.balloons()
                    else:
                        st.error("백업 복원 중 오류가 발생했습니다.")
    
    def show_backup_management(self):
        """Display backup management interface"""
        st.markdown("#### 📊 백업 관리")
        
        # CSV files overview
        data_dir = "data"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            
            st.markdown("##### 📁 현재 데이터 파일")
            
            file_data = []
            for csv_file in csv_files:
                file_path = os.path.join(data_dir, csv_file)
                file_size = os.path.getsize(file_path)
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                df = pd.read_csv(file_path)
                record_count = len(df)
                
                file_data.append({
                    'File': csv_file,
                    'Records': record_count,
                    'Size (KB)': f"{file_size/1024:.1f}",
                    'Modified': file_modified.strftime('%Y-%m-%d %H:%M')
                })
            
            files_df = pd.DataFrame(file_data)
            st.dataframe(files_df, use_container_width=True)
            
            # Individual file downloads
            st.markdown("##### 📥 개별 파일 다운로드")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_files = st.multiselect("다운로드할 파일 선택", csv_files)
            
            with col2:
                if selected_files and st.button("📥 선택된 파일 다운로드"):
                    zip_buffer = self.create_selective_backup(selected_files)
                    
                    st.download_button(
                        label="📥 선택된 파일 다운로드",
                        data=zip_buffer.getvalue(),
                        file_name=f"selective_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime='application/zip'
                    )
    
    def create_backup(self, backup_type, include_images, compress_backup, description):
        """Create system backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{backup_type.replace(' ', '_')}_{timestamp}.zip"
            backup_path = os.path.join("data", backup_filename)
            
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED if compress_backup else zipfile.ZIP_STORED) as zipf:
                # Add metadata
                metadata = {
                    'backup_type': backup_type,
                    'created_at': datetime.now().isoformat(),
                    'description': description,
                    'include_images': include_images,
                    'version': '1.0'
                }
                
                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
                
                # Add CSV files based on backup type
                data_dir = "data"
                if os.path.exists(data_dir):
                    files_to_backup = self.get_files_for_backup_type(backup_type)
                    
                    for filename in files_to_backup:
                        file_path = os.path.join(data_dir, filename)
                        if os.path.exists(file_path):
                            zipf.write(file_path, filename)
                
                # Add uploads directory if exists and images are included
                if include_images and os.path.exists("uploads"):
                    for root, dirs, files in os.walk("uploads"):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, ".")
                            zipf.write(file_path, arc_path)
            
            return backup_path
            
        except Exception as e:
            st.error(f"백업 생성 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def restore_backup(self, uploaded_file, restore_options):
        """Restore from backup file"""
        try:
            # Create temporary directory
            temp_dir = "temp_restore"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract backup file
            with zipfile.ZipFile(uploaded_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Read metadata if exists
            metadata_path = os.path.join(temp_dir, 'backup_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    st.info(f"백업 생성일: {metadata.get('created_at', 'Unknown')}")
                    st.info(f"백업 유형: {metadata.get('backup_type', 'Unknown')}")
            
            # Restore selected data
            file_mapping = {
                "사용자 계정": "users.csv",
                "게시판": "posts.csv",
                "과제": ["assignments.csv", "submissions.csv"],
                "퀴즈": ["quizzes.csv", "quiz_responses.csv"],
                "채팅": "chat_logs.csv",
                "일정": "schedule.csv",
                "투표": "votes.csv",
                "출석": "attendance.csv"
            }
            
            for option in restore_options:
                if option in file_mapping:
                    files = file_mapping[option]
                    if isinstance(files, str):
                        files = [files]
                    
                    for filename in files:
                        temp_file_path = os.path.join(temp_dir, filename)
                        target_file_path = os.path.join("data", filename)
                        
                        if os.path.exists(temp_file_path):
                            # Backup existing file
                            if os.path.exists(target_file_path):
                                backup_existing_path = f"{target_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                os.rename(target_file_path, backup_existing_path)
                            
                            # Copy restored file
                            os.rename(temp_file_path, target_file_path)
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True
            
        except Exception as e:
            st.error(f"백업 복원 중 오류가 발생했습니다: {str(e)}")
            return False
    
    def create_selective_backup(self, selected_files):
        """Create backup of selected files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in selected_files:
                file_path = os.path.join("data", filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def get_files_for_backup_type(self, backup_type):
        """Get list of files to backup based on type"""
        all_files = [
            "users.csv", "clubs.csv", "user_clubs.csv", "posts.csv", "comments.csv",
            "assignments.csv", "submissions.csv", "quizzes.csv", "quiz_responses.csv",
            "chat_logs.csv", "schedule.csv", "votes.csv", "vote_options.csv",
            "vote_responses.csv", "attendance.csv", "notifications.csv", "badges.csv",
            "points.csv", "video_conferences.csv"
        ]
        
        if backup_type == "전체 백업":
            return all_files
        elif backup_type == "사용자 데이터만":
            return ["users.csv", "clubs.csv", "user_clubs.csv", "badges.csv", "points.csv"]
        elif backup_type == "게시판 데이터만":
            return ["posts.csv", "comments.csv"]
        elif backup_type == "과제 데이터만":
            return ["assignments.csv", "submissions.csv", "quizzes.csv", "quiz_responses.csv"]
        else:
            return all_files