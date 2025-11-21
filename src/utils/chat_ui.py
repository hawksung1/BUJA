"""
채팅 UI 관련 유틸리티 함수
"""
import streamlit as st


def render_chat_file_upload_styles() -> None:
    """채팅 파일 업로드 관련 CSS 스타일 렌더링"""
    st.markdown("""
    <style>
        /* 메시지 영역에 하단 패딩 추가 */
        .main .block-container {
            padding-bottom: 200px !important;
        }
        
        /* 원본 파일 업로더 완전히 숨기기 */
        div[data-testid="stFileUploader"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        
        /* 채팅 입력창 내부 파일 업로드 아이콘 버튼 */
        #chat-file-upload-icon {
            position: absolute !important;
            left: 12px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            background: transparent !important;
            border: none !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            z-index: 1000 !important;
            font-size: 18px !important;
            color: #666 !important;
            transition: all 0.2s !important;
        }
        
        #chat-file-upload-icon:hover {
            background: rgba(0, 0, 0, 0.05) !important;
            color: #333 !important;
        }
        
        /* 채팅 입력창 컨테이너에 상대 위치 설정 */
        div[data-testid="stChatInputContainer"],
        textarea[placeholder*="물어보세요"]:not([data-upload-icon-added]),
        textarea[placeholder*="ask"]:not([data-upload-icon-added]) {
            position: relative !important;
        }
        
        /* 채팅 입력창 텍스트 영역에 왼쪽 패딩 추가 (아이콘 공간 확보) */
        textarea[placeholder*="물어보세요"],
        textarea[placeholder*="ask"] {
            padding-left: 50px !important;
        }
        
        /* 모든 textarea의 부모도 상대 위치로 */
        textarea {
            position: relative !important;
        }
        
        /* 썸네일을 채팅 입력 위에 작게 표시 */
        .thumbnail-preview {
            position: fixed !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: auto !important;
            max-width: 400px !important;
            z-index: 998 !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px) !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.75rem !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_chat_file_upload_script() -> None:
    """채팅 파일 업로드 관련 JavaScript 렌더링"""
    st.markdown("""
    <script>
    (function() {
        let uploadIcon = null;
        let iconUpdateInterval = null;
        
        // Streamlit iframe 처리
        function getDocument() {
            try {
                if (window.parent && window.parent !== window) {
                    return window.parent.document;
                }
            } catch(e) {
                // Cross-origin 에러 무시
            }
            return document;
        }
        
        function findChatInput() {
            const doc = getDocument();
            let chatInput = doc.querySelector('textarea[placeholder*="물어보세요"]');
            if (!chatInput) {
                chatInput = doc.querySelector('textarea[placeholder*="ask"]');
            }
            if (!chatInput) {
                const allTextareas = Array.from(doc.querySelectorAll('textarea'));
                if (allTextareas.length > 0) {
                    chatInput = allTextareas.reduce((bottom, ta) => {
                        const rect = ta.getBoundingClientRect();
                        const bottomRect = bottom.getBoundingClientRect();
                        return rect.bottom > bottomRect.bottom ? ta : bottom;
                    });
                }
            }
            return chatInput;
        }
        
        function findFileInput() {
            const doc = getDocument();
            return doc.querySelector('input[type="file"]');
        }
        
        function createUploadIcon() {
            const chatInput = findChatInput();
            const fileInput = findFileInput();
            
            if (!chatInput || !fileInput) {
                return false;
            }
            
            // 기존 아이콘이 있으면 제거
            const existingIcon = document.getElementById('chat-file-upload-icon');
            if (existingIcon) {
                existingIcon.remove();
            }
            
            // 파일 업로드 아이콘 버튼 생성
            uploadIcon = document.createElement('button');
            uploadIcon.id = 'chat-file-upload-icon';
            uploadIcon.innerHTML = '📎';
            uploadIcon.type = 'button';
            uploadIcon.title = '파일 업로드';
            
            // 스타일 설정
            Object.assign(uploadIcon.style, {
                position: 'fixed',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: '10000',
                fontSize: '18px',
                color: '#666',
                transition: 'all 0.2s',
                padding: '0',
                margin: '0',
                lineHeight: '1'
            });
            
            uploadIcon.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(0, 0, 0, 0.05)';
                this.style.color = '#333';
            });
            
            uploadIcon.addEventListener('mouseleave', function() {
                this.style.background = 'transparent';
                this.style.color = '#666';
            });
            
            // 아이콘 클릭 시 파일 입력 트리거
            uploadIcon.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const input = findFileInput();
                if (input) {
                    input.click();
                }
            });
            
            // 아이콘을 body에 추가
            const doc = getDocument();
            try {
                document.body.appendChild(uploadIcon);
            } catch(e) {
                try {
                    if (window.parent && window.parent !== window) {
                        window.parent.document.body.appendChild(uploadIcon);
                    } else {
                        doc.body.appendChild(uploadIcon);
                    }
                } catch(e2) {
                    const input = findChatInput();
                    if (input && input.parentElement) {
                        input.parentElement.style.position = 'relative';
                        input.parentElement.appendChild(uploadIcon);
                        uploadIcon.style.position = 'absolute';
                    }
                }
            }
            
            // 위치 업데이트 함수
            function updateIconPosition() {
                const input = findChatInput();
                if (!input || !uploadIcon) return;
                
                try {
                    const rect = input.getBoundingClientRect();
                    uploadIcon.style.left = (rect.left + 12) + 'px';
                    uploadIcon.style.top = (rect.top + rect.height / 2) + 'px';
                    uploadIcon.style.transform = 'translateY(-50%)';
                } catch(e) {
                    console.log('[FileUpload] Error updating icon position:', e);
                }
            }
            
            // 즉시 위치 설정
            setTimeout(updateIconPosition, 50);
            
            // 스크롤 및 리사이즈 시 위치 업데이트
            const win = window.parent !== window ? window.parent : window;
            win.addEventListener('scroll', updateIconPosition, true);
            win.addEventListener('resize', updateIconPosition);
            
            // 기존 인터벌 제거
            if (iconUpdateInterval) {
                clearInterval(iconUpdateInterval);
            }
            
            // 주기적으로 위치 업데이트
            iconUpdateInterval = setInterval(updateIconPosition, 100);
            
            return true;
        }
        
        function updateThumbnailPosition() {
            const chatInput = findChatInput();
            if (!chatInput) return;
            
            const removeButton = document.querySelector('button[key="remove_image"]');
            if (!removeButton) return;
            
            const column = removeButton.closest('[data-testid="column"]');
            if (!column) return;
            
            const thumbnailContainer = column.parentElement;
            if (!thumbnailContainer) return;
            
            if (!thumbnailContainer.classList.contains('thumbnail-preview')) {
                thumbnailContainer.classList.add('thumbnail-preview');
            }
            
            const chatInputRect = chatInput.getBoundingClientRect();
            const spacing = 10;
            const thumbnailHeight = thumbnailContainer.offsetHeight || 50;
            const targetTop = chatInputRect.top - thumbnailHeight - spacing;
            
            thumbnailContainer.style.setProperty('position', 'fixed', 'important');
            thumbnailContainer.style.setProperty('top', targetTop + 'px', 'important');
            thumbnailContainer.style.setProperty('left', '50%', 'important');
            thumbnailContainer.style.setProperty('transform', 'translateX(-50%)', 'important');
        }
        
        function fixAll() {
            const iconCreated = createUploadIcon();
            updateThumbnailPosition();
            return iconCreated;
        }
        
        // 즉시 실행 (여러 번 시도)
        let attempts = 0;
        const maxAttempts = 100;
        let iconCreated = false;
        const tryFix = () => {
            attempts++;
            if (!iconCreated) {
                iconCreated = createUploadIcon();
            }
            updateThumbnailPosition();
            if (attempts < maxAttempts && !iconCreated) {
                setTimeout(tryFix, 100);
            }
        };
        tryFix();
        
        // 페이지 로드 시 실행
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', tryFix);
        } else {
            tryFix();
        }
        
        // Streamlit이 DOM을 업데이트할 때마다 실행
        const observer = new MutationObserver(function(mutations) {
            fixAll();
        });
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true
        });
        
        // 윈도우 리사이즈 및 스크롤 시 위치 재조정
        window.addEventListener('resize', fixAll);
        window.addEventListener('scroll', fixAll, true);
        
        // 주기적으로 확인
        setInterval(fixAll, 300);
        
        window.addEventListener('load', tryFix);
    })();
    </script>
    """, unsafe_allow_html=True)



