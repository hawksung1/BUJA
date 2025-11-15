"""
Common Sidebar Component
Dynamically displays menu based on user authentication status and onboarding status.
"""
import streamlit as st
from src.middleware import auth_middleware
from src.utils.async_helpers import run_async
from src.services import UserService, InvestmentPreferenceService
from src.repositories import FinancialSituationRepository, FinancialGoalRepository
from src.exceptions import DatabaseError, UserNotFoundError
from config.database import db
from config.logging import get_logger

logger = get_logger(__name__)


def _hide_default_navigation():
    """Completely hides Streamlit default navigation menu."""
    st.markdown("""
    <style>
    /* Compact sidebar styling */
    [data-testid="stSidebar"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.25rem !important;
    }
    
    /* Remove button styling - make it look like text links */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.05rem !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0.35rem 0.6rem !important;
        margin-bottom: 0 !important;
        font-size: 0.875rem !important;
        height: auto !important;
        min-height: auto !important;
        width: 100% !important;
        text-align: left !important;
        color: inherit !important;
        box-shadow: none !important;
        border-radius: 0.375rem !important;
        transition: all 0.2s ease !important;
        font-weight: 400 !important;
        justify-content: flex-start !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(100, 100, 100, 0.35) !important;
        transform: translateX(2px) !important;
        color: rgba(255, 255, 255, 1) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        background-color: rgba(100, 100, 100, 0.4) !important;
        transform: translateX(0) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Selected state for buttons - 더 진하게 */
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: rgba(100, 100, 100, 0.35) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: rgba(100, 100, 100, 0.45) !important;
        color: rgba(255, 255, 255, 1) !important;
    }
    
    /* Secondary button style - 새 채팅, 새 프로젝트 등 */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"],
    [data-testid="stSidebar"] .stButton > button[data-baseweb="button"][kind="secondary"] {
        background-color: transparent !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background-color: rgba(100, 100, 100, 0.35) !important;
        transform: translateX(2px) !important;
        color: rgba(255, 255, 255, 1) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:active {
        background-color: rgba(100, 100, 100, 0.4) !important;
        transform: translateX(0) !important;
    }
    
    /* 삭제 버튼 스타일 - 버튼 모양 완전히 제거하고 x만 표시 */
    [data-testid="stSidebar"] button[title*="프로젝트 삭제"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: auto !important;
        width: auto !important;
        height: auto !important;
        box-shadow: none !important;
        opacity: 0.6 !important;
        font-size: 1.2rem !important;
        line-height: 1 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stSidebar"] button[title*="프로젝트 삭제"]:hover {
        background: transparent !important;
        opacity: 1 !important;
        transform: none !important;
        color: rgba(255, 100, 100, 0.9) !important;
    }
    
    /* × 문자가 포함된 삭제 버튼 스타일 */
    [data-testid="stSidebar"] .delete-btn {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: auto !important;
        width: auto !important;
        height: auto !important;
        box-shadow: none !important;
        opacity: 0.6 !important;
        font-size: 1.2rem !important;
        line-height: 1 !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stSidebar"] .delete-btn:hover {
        background: transparent !important;
        opacity: 1 !important;
        transform: none !important;
        color: rgba(255, 100, 100, 0.9) !important;
    }
    
    /* 프로젝트 삭제 버튼 컨테이너 스타일 */
    [data-testid="stSidebar"] [data-testid="column"]:has(button[title*="프로젝트 삭제"]) {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stSidebar"] .stTextInput {
        margin-bottom: 0.25rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        padding: 0.35rem 0.6rem !important;
        margin-bottom: 0 !important;
        font-size: 0.875rem !important;
        height: 1.9rem !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.375rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 0.2rem !important;
    }
    
    [data-testid="stSidebar"] h1 {
        font-size: 1.25rem !important;
        margin-bottom: 0.3rem !important;
        padding-top: 0 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 0.75rem !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.25rem !important;
        padding-top: 0 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        opacity: 0.6 !important;
    }
    
    [data-testid="stSidebar"] strong {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        opacity: 0.6 !important;
        display: block !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.25rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.875rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 0.3rem 0 !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] .stPageLink {
        padding: 0.2rem 0.5rem !important;
        margin-bottom: 0.1rem !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stSidebar"] .stPageLink > a {
        padding: 0.4rem 0.6rem !important;
        border-radius: 0.375rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebar"] .stPageLink > a:hover {
        background-color: rgba(100, 100, 100, 0.35) !important;
        transform: translateX(2px) !important;
        color: rgba(255, 255, 255, 1) !important;
    }
    
    [data-testid="stSidebar"] .stPageLink > a:active {
        background-color: rgba(100, 100, 100, 0.4) !important;
    }
    
    /* 선택된 페이지 링크 */
    [data-testid="stSidebar"] .stPageLink > a[aria-current="page"] {
        background-color: rgba(100, 100, 100, 0.35) !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stPageLink > a[aria-current="page"]:hover {
        background-color: rgba(100, 100, 100, 0.45) !important;
        color: rgba(255, 255, 255, 1) !important;
    }
    
    [data-testid="stSidebar"] .stExpander {
        margin-bottom: 0.2rem !important;
    }
    
    [data-testid="stSidebar"] .stExpander > label {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stSidebar"] .stExpander > div {
        padding: 0.2rem 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.75rem !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
        opacity: 0.7 !important;
    }
    
    [data-testid="stSidebar"] p {
        margin: 0.2rem 0 !important;
        font-size: 0.875rem !important;
    }
    
    /* Account info styling */
    [data-testid="stSidebar"] .account-info {
        padding: 0.5rem 0.6rem !important;
        border-radius: 0.5rem !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
        margin-top: 0.5rem !important;
        position: relative !important;
        color: rgba(38, 39, 48, 0.9) !important;
    }
    
    [data-testid="stSidebar"] .account-info:hover {
        background-color: rgba(0, 0, 0, 0.05) !important;
        color: rgba(38, 39, 48, 1) !important;
    }
    
    /* Account info 내부 텍스트 색상 강제 적용 - 어두운 색으로 변경 */
    [data-testid="stSidebar"] .account-info,
    [data-testid="stSidebar"] .account-info *,
    [data-testid="stSidebar"] .account-info div,
    [data-testid="stSidebar"] .account-info span {
        color: rgba(38, 39, 48, 0.9) !important;
    }
    
    /* 사용자 이름 스타일 */
    [data-testid="stSidebar"] .account-info > div > div:nth-child(2) > div:first-child {
        color: rgba(38, 39, 48, 0.9) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* 이메일 스타일 */
    [data-testid="stSidebar"] .account-info > div > div:nth-child(2) > div:last-child {
        color: rgba(38, 39, 48, 0.7) !important;
        font-size: 0.75rem !important;
    }
    
    /* 드롭다운 화살표 색상 */
    [data-testid="stSidebar"] .account-info #account-dropdown-arrow {
        color: rgba(38, 39, 48, 0.6) !important;
    }
    
    /* Account dropdown menu */
    .account-dropdown {
        position: absolute !important;
        bottom: 100% !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        z-index: 1000 !important;
        overflow: hidden !important;
        display: none !important;
        animation: slideDown 0.2s ease-out !important;
    }
    
    .account-dropdown.show {
        display: block !important;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .account-dropdown-item {
        padding: 0.6rem 1rem !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
        font-size: 0.875rem !important;
        color: rgba(38, 39, 48, 0.9) !important;
        border: none !important;
        background: transparent !important;
        width: 100% !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    .account-dropdown-item:hover {
        background-color: rgba(0, 0, 0, 0.05) !important;
        color: rgba(38, 39, 48, 1) !important;
    }
    
    .account-dropdown-item:first-child {
        border-top-left-radius: 0.5rem !important;
        border-top-right-radius: 0.5rem !important;
    }
    
    .account-dropdown-item:last-child {
        border-bottom-left-radius: 0.5rem !important;
        border-bottom-right-radius: 0.5rem !important;
    }
    
    .account-dropdown-divider {
        height: 1px !important;
        background-color: rgba(0, 0, 0, 0.1) !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Settings modal overlay - positioned relative to viewport */
    .settings-modal-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        backdrop-filter: blur(4px) !important;
        animation: fadeIn 0.2s ease-in-out !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .settings-modal {
        background-color: #1e1e1e !important;
        border-radius: 0.75rem !important;
        width: 90% !important;
        max-width: 900px !important;
        max-height: 85vh !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        animation: slideUp 0.3s ease-out !important;
    }
    
    @keyframes slideUp {
        from { 
            transform: translateY(20px);
            opacity: 0;
        }
        to { 
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .settings-modal-header {
        position: relative !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: #252525 !important;
    }
    
    .settings-modal-sidebar {
        width: 220px !important;
        background-color: #252525 !important;
        padding: 1rem 0 !important;
        overflow-y: auto !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        flex-shrink: 0 !important;
    }
    
    .settings-modal-content {
        flex: 1 !important;
        padding: 1.5rem !important;
        overflow-y: auto !important;
        background-color: #1e1e1e !important;
    }
    
    .settings-modal-item {
        padding: 0.6rem 1rem !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
        font-size: 0.875rem !important;
        color: rgba(255, 255, 255, 0.7) !important;
        border: none !important;
        background: transparent !important;
        width: 100% !important;
        text-align: left !important;
        display: block !important;
    }
    
    .settings-modal-item:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .settings-modal-item.active {
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Completely hide Streamlit default navigation menu - CSS */
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }
    
    /* Hide navigation item list */
    [data-testid="stSidebarNavItems"],
    ul[data-testid="stSidebarNavItems"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }
    
    /* Hide navigation link container */
    [data-testid="stSidebarNavLinkContainer"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide navigation links */
    [data-testid="stSidebarNavLink"],
    a[data-testid="stSidebarNavLink"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide navigation related elements */
    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    
    /* Hide navigation related li elements in sidebar */
    [data-testid="stSidebar"] li:has([data-testid="stSidebarNavLink"]),
    [data-testid="stSidebarNavItems"] li {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* All navigation related elements */
    nav[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNav"],
    section[data-testid="stSidebar"] > nav,
    section[data-testid="stSidebar"] > div > nav {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }
    
    /* Hide hidden form controls for dropdown (checkbox and text input) */
    [data-testid="stSidebar"] [data-testid*="account_dropdown_toggle"],
    [data-testid="stSidebar"] [data-testid*="account_dropdown_toggle"] ~ *,
    [data-testid="stSidebar"] label:has([data-testid*="account_dropdown_toggle"]),
    [data-testid="stSidebar"] [data-testid*="account_menu_action"],
    [data-testid="stSidebar"] [data-testid*="account_menu_action"] ~ *,
    [data-testid="stSidebar"] label:has([data-testid*="account_menu_action"]) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* Hide element containers for hidden controls */
    [data-testid="stSidebar"] .element-container:has([data-testid*="account_dropdown_toggle"]),
    [data-testid="stSidebar"] .element-container:has([data-testid*="account_menu_action"]) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }
    </style>
    
    <script>
    // Dynamic hiding using JavaScript (fallback if CSS doesn't apply)
    (function() {
        // 삭제 버튼 스타일 적용 함수
        function styleDeleteButtons() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            
            // × 문자가 포함된 버튼 찾기
            const buttons = sidebar.querySelectorAll('button');
            buttons.forEach(button => {
                // 이미 스타일이 적용된 버튼은 건너뛰기
                if (button.classList.contains('delete-btn-styled')) {
                    return;
                }
                
                const buttonText = button.textContent.trim();
                const buttonTitle = button.getAttribute('title') || '';
                
                // × 문자가 있거나 title에 "프로젝트 삭제"가 포함된 경우
                if (buttonText === '×' || buttonTitle.includes('프로젝트 삭제')) {
                    button.style.background = 'transparent';
                    button.style.border = 'none';
                    button.style.padding = '0';
                    button.style.margin = '0';
                    button.style.minWidth = 'auto';
                    button.style.width = 'auto';
                    button.style.height = 'auto';
                    button.style.boxShadow = 'none';
                    button.style.opacity = '0.6';
                    button.style.fontSize = '1.2rem';
                    button.style.lineHeight = '1';
                    button.style.display = 'inline-flex';
                    button.style.alignItems = 'center';
                    button.style.justifyContent = 'center';
                    button.classList.add('delete-btn', 'delete-btn-styled');
                    
                    // 호버 이벤트 (한 번만 추가)
                    button.addEventListener('mouseenter', function() {
                        this.style.background = 'transparent';
                        this.style.opacity = '1';
                        this.style.transform = 'none';
                        this.style.color = 'rgba(255, 100, 100, 0.9)';
                    });
                    
                    button.addEventListener('mouseleave', function() {
                        this.style.background = 'transparent';
                        this.style.opacity = '0.6';
                        this.style.color = '';
                    });
                }
            });
        }
        
        function hideNavigation() {
            // Find and hide navigation elements
            const selectors = [
                '[data-testid="stSidebarNav"]',
                '[data-testid="stSidebarNavItems"]',
                '[data-testid="stSidebarNavLink"]',
                '[data-testid="stSidebarNavLinkContainer"]',
                'ul[data-testid="stSidebarNavItems"]',
                'nav[data-testid="stSidebarNav"]'
            ];
            
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.height = '0';
                    el.style.opacity = '0';
                    el.style.margin = '0';
                    el.style.padding = '0';
                });
            });
            
            // Hide li elements (all li containing navigation links)
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                // Find li elements containing navigation links
                const allLinks = sidebar.querySelectorAll('[data-testid="stSidebarNavLink"]');
                allLinks.forEach(link => {
                    let parent = link.closest('li');
                    while (parent && parent !== sidebar) {
                        parent.style.display = 'none';
                        parent.style.visibility = 'hidden';
                        parent = parent.parentElement;
                    }
                });
                
                // Hide all li inside stSidebarNavItems
                const navItems = sidebar.querySelector('[data-testid="stSidebarNavItems"]');
                if (navItems) {
                    navItems.querySelectorAll('li').forEach(li => {
                        li.style.display = 'none';
                        li.style.visibility = 'hidden';
                    });
                }
            }
        }
        
        // Execute immediately
        hideNavigation();
        styleDeleteButtons();
        
        // Detect DOM changes (fallback for when Streamlit dynamically adds elements)
        const observer = new MutationObserver(() => {
            hideNavigation();
            styleDeleteButtons();
        });
        
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            observer.observe(sidebar, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }
        
        // 문서 전체도 관찰
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Execute after page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                hideNavigation();
                styleDeleteButtons();
            });
        } else {
            hideNavigation();
            styleDeleteButtons();
        }
        
        // Execute after Streamlit is fully loaded
        window.addEventListener('load', () => {
            setTimeout(() => {
                hideNavigation();
                styleDeleteButtons();
            }, 100);
        });
        
        // Periodic check (more frequently)
        setInterval(() => {
            hideNavigation();
            styleDeleteButtons();
        }, 200);
        
        // Streamlit custom event listener
        if (window.parent) {
            window.parent.addEventListener('message', (event) => {
                if (event.data && (event.data.type === 'streamlit:render' || event.data.type === 'streamlit:rerun')) {
                    setTimeout(() => {
                        hideNavigation();
                        styleDeleteButtons();
                    }, 50);
                }
            });
        }
    })();
    </script>
    """, unsafe_allow_html=True)


def render_sidebar(current_page: str = None):
    """
    Dynamically renders sidebar based on user status.
    
    User scenarios:
    1. Unauthenticated user: Only Login, Register displayed
    2. Authenticated + Onboarding incomplete: Onboarding emphasized, main features disabled
    3. Authenticated + Onboarding complete: All menus enabled
    
    Args:
        current_page: Current page identifier (e.g., 'agent_chat', 'dashboard', etc.)
    """
    # Hide Streamlit default navigation
    _hide_default_navigation()
    
    user = auth_middleware.get_current_user()
    is_authenticated = auth_middleware.is_authenticated()
    
    # Unauthenticated user
    if not is_authenticated or not user:
        _render_unauthenticated_sidebar()
        return
    
    # Authenticated user - check onboarding status
    onboarding_status = _check_onboarding_status(user.id)
    _render_authenticated_sidebar(user, onboarding_status, current_page)


def _render_unauthenticated_sidebar():
    """Sidebar for unauthenticated users"""
    with st.sidebar:
        st.title("💰 BUJA")
        st.markdown("---")
        
        st.page_link("pages/login.py", label="Login", icon="🔐")
        st.page_link("pages/register.py", label="Register", icon="📝")
        
        st.markdown("---")
        st.caption("Please login to use the service.")


def _render_authenticated_sidebar(user, onboarding_status, current_page: str = None):
    """Sidebar for authenticated users"""
    with st.sidebar:
        # App title
        st.markdown("### 💰 BUJA")
        
        st.markdown("---")
        
        # Chat section (only for agent_chat page)
        if current_page == "agent_chat":
            _render_chat_section(user)
            st.markdown("---")
        
        # Main menu - compact style
        st.markdown("**메뉴**")
        
        # Emphasize if onboarding incomplete
        if not onboarding_status["completed"]:
            # Onboarding incomplete: Show onboarding prominently, disable main features
            st.page_link(
                "pages/onboarding.py",
                label="👋 온보딩 (필수)",
                disabled=False
            )
            st.caption("⚠️ 온보딩을 먼저 완료하세요")
            
            # Main features disabled
            st.page_link("pages/agent_chat.py", label="🤖 에이전트 채팅", disabled=True)
            st.page_link("pages/dashboard.py", label="📊 대시보드", disabled=True)
        else:
            # Onboarding complete: Enable all main features
            st.page_link("pages/agent_chat.py", label="🤖 에이전트 채팅")
            st.page_link("pages/dashboard.py", label="📊 대시보드")
        
        # Spacer to push account info to bottom
        st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Account info at bottom (clickable to open settings)
        _render_account_info(user, onboarding_status)
        
        # Settings modal (rendered if opened)
        _render_settings_modal(user, onboarding_status)


def _render_chat_section(user):
    """Render chat-specific sidebar section (only for agent_chat page)"""
    from src.services.chat_service import ChatService
    from src.services.chat_project_service import ChatProjectService
    
    chat_service = ChatService()
    project_service = ChatProjectService()
    
    # 새 채팅 버튼
    if st.button("✏️ 새 채팅", use_container_width=True, type="secondary", key="sidebar_new_chat_btn"):
        try:
            run_async(chat_service.clear_messages(user.id))
            st.session_state.messages = []
            st.session_state.current_project_id = None
            st.session_state.uploaded_image = None
            st.session_state.uploaded_image_name = None
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # 채팅 검색
    chat_search = st.text_input("🔍 채팅 검색", placeholder="검색어 입력...", key="sidebar_chat_search", label_visibility="collapsed")
    if chat_search:
        try:
            search_results = run_async(chat_service.search_messages(user.id, chat_search))
            if search_results:
                st.caption(f"검색 결과: {len(search_results)}개")
                for idx, msg in enumerate(search_results[:3]):
                    with st.expander(f"💬 {msg.get('content', '')[:30]}...", expanded=False):
                        st.caption(f"**{msg.get('role')}**")
                        st.write(msg.get('content', '')[:150] + "...")
        except Exception as e:
            st.error(f"검색 오류: {str(e)}")
    
    st.markdown("---")
    
    # 프로젝트 섹션
    st.markdown("**프로젝트**")
    
    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = None
    
    try:
        projects = run_async(project_service.get_projects(user.id))
        
        # 새 프로젝트 버튼
        if st.button("➕ 새 프로젝트", use_container_width=True, type="secondary", key="sidebar_new_project_btn"):
            st.session_state.show_new_project_form = not st.session_state.get("show_new_project_form", False)
        
        # 새 프로젝트 폼
        if st.session_state.get("show_new_project_form", False):
            with st.form("new_project_form", clear_on_submit=True):
                project_name = st.text_input("이름 *", placeholder="예: 투자 전략")
                project_icon = st.text_input("아이콘", placeholder="💰", max_chars=5)
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("생성", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("취소", use_container_width=True)
                
                if cancel:
                    st.session_state.show_new_project_form = False
                    st.rerun()
                
                if submit and project_name:
                    try:
                        new_project = run_async(project_service.create_project(
                            user_id=user.id,
                            name=project_name,
                            icon=project_icon if project_icon else None
                        ))
                        st.session_state.show_new_project_form = False
                        st.session_state.current_project_id = new_project["id"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"생성 실패: {str(e)}")
        
        # 프로젝트 목록
        if projects:
            for project in projects:
                icon = project.get("icon", "📁")
                name = project.get("name", "Unnamed")
                project_id = project.get("id")
                is_selected = st.session_state.current_project_id == project_id
                
                # 프로젝트 항목을 두 개의 컬럼으로 나눔: 이름 버튼과 삭제 버튼
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if st.button(
                        f"{icon} {name}",
                        key=f"sidebar_proj_{project_id}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.current_project_id = project_id
                        project_messages = run_async(chat_service.get_messages(user.id, project_id=project_id))
                        st.session_state.messages = project_messages
                        st.rerun()
                
                with col2:
                    # 삭제 확인 상태 확인
                    is_confirming = st.session_state.get(f"delete_project_confirm_{project_id}", False)
                    
                    if is_confirming:
                        # 확인 모드: 삭제 확인 버튼 표시
                        if st.button(
                            "✓",
                            key=f"sidebar_proj_confirm_{project_id}",
                            use_container_width=True,
                            type="primary",
                            help="삭제 확인"
                        ):
                            try:
                                success = run_async(project_service.delete_project(project_id, user.id))
                                if success:
                                    # 삭제된 프로젝트가 현재 선택된 프로젝트인 경우 초기화
                                    if st.session_state.current_project_id == project_id:
                                        st.session_state.current_project_id = None
                                        st.session_state.messages = []
                                    st.session_state[f"delete_project_confirm_{project_id}"] = False
                                    st.success(f"'{name}' 프로젝트가 삭제되었습니다.")
                                    st.rerun()
                                else:
                                    st.error("프로젝트 삭제에 실패했습니다.")
                                    st.session_state[f"delete_project_confirm_{project_id}"] = False
                            except Exception as e:
                                st.error(f"삭제 오류: {str(e)}")
                                st.session_state[f"delete_project_confirm_{project_id}"] = False
                    else:
                        # 일반 모드: 삭제 버튼 표시 (x만 보이도록)
                        if st.button(
                            "×",
                            key=f"sidebar_proj_delete_{project_id}",
                            use_container_width=False,
                            type="secondary",
                            help=f"'{name}' 프로젝트 삭제"
                        ):
                            # 삭제 확인을 위한 세션 상태 설정
                            st.session_state[f"delete_project_confirm_{project_id}"] = True
                            st.rerun()
                
                # 삭제 확인 중일 때 경고 메시지 표시
                if st.session_state.get(f"delete_project_confirm_{project_id}", False):
                    st.caption(f"⚠️ '{name}' 삭제하려면 ✓ 클릭")
    except Exception as e:
        st.warning(f"프로젝트 로드 실패: {str(e)}")
    
    st.markdown("---")
    
    # 내 채팅 섹션
    st.markdown("**내 채팅**")
    try:
        all_messages = run_async(chat_service.get_messages(user.id, limit=50))
        if all_messages:
            # 사용자 메시지만 표시 (채팅 제목으로 사용)
            user_messages = [msg for msg in all_messages if msg.get("role") == "user"]
            # 중복 제거 (같은 내용의 메시지는 하나만)
            seen = set()
            unique_messages = []
            for msg in user_messages:
                content = msg.get("content", "")[:50]  # 처음 50자만 비교
                if content and content not in seen:
                    seen.add(content)
                    unique_messages.append(msg)
            
            for idx, msg in enumerate(unique_messages[:20]):  # 최대 20개만 표시
                title = msg.get("content", "채팅")[:30]
                if st.button(
                    f"💬 {title}...",
                    key=f"sidebar_chat_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    # 해당 채팅으로 이동 (간단 구현)
                    st.session_state.messages = [msg]
                    st.rerun()
    except Exception as e:
        st.caption("채팅 목록을 불러올 수 없습니다.")


def _render_account_info(user, onboarding_status):
    """Render account info at bottom of sidebar with dropdown menu"""
    # Initialize dropdown state
    if "show_account_dropdown" not in st.session_state:
        st.session_state.show_account_dropdown = False
    
    # Get user profile info
    try:
        user_service = UserService()
        user_with_profile = run_async(user_service.get_user_with_profile(user.id))
        profile = user_with_profile.profile if user_with_profile else None
        user_name = profile.name if profile and profile.name else user.email.split("@")[0]
        user_email = user.email
    except (DatabaseError, UserNotFoundError, AttributeError) as e:
        logger.debug(f"Could not load user profile: {e}")
        user_name = user.email.split("@")[0]
        user_email = user.email
    
    # Get initials for avatar (first 2 letters)
    initials = "".join([c.upper() for c in user_name[:2] if c.isalpha()]) or user_name[0].upper() if user_name else "U"
    
    # Account info container - clickable with dropdown
    account_container_id = "account-info-container"
    
    # Render account info with dropdown
    st.markdown(f"""
    <div id="{account_container_id}" class="account-info" style="position: relative; color: rgba(38, 39, 48, 0.9);">
        <div style="display: flex; align-items: center; gap: 0.75rem; color: inherit;">
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
                font-size: 0.75rem;
                flex-shrink: 0;
            ">{initials}</div>
            <div style="flex: 1; min-width: 0; color: inherit;">
                <div style="font-size: 0.875rem; font-weight: 500; color: rgba(38, 39, 48, 0.9);">{user_name}</div>
                <div style="font-size: 0.75rem; color: rgba(38, 39, 48, 0.7);">@{user_email.split('@')[0]}</div>
            </div>
            <div style="
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: rgba(38, 39, 48, 0.6);
                transition: transform 0.2s;
                flex-shrink: 0;
            " id="account-dropdown-arrow">▼</div>
        </div>
        <div class="account-dropdown" id="account-dropdown-menu">
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('settings')">
                <span>⚙️</span>
                <span>설정</span>
            </button>
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('profile')">
                <span>👤</span>
                <span>프로필</span>
            </button>
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('investment')">
                <span>📈</span>
                <span>투자 선호도</span>
            </button>
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('onboarding')">
                <span>👋</span>
                <span>온보딩</span>
            </button>
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('mcp_tools')">
                <span>🔧</span>
                <span>MCP 도구</span>
            </button>
            <div class="account-dropdown-divider"></div>
            <button class="account-dropdown-item" onclick="handleAccountMenuClick('logout')" style="color: rgba(220, 53, 69, 0.9);">
                <span>🚪</span>
                <span>로그아웃</span>
            </button>
        </div>
    </div>
    <script>
        (function() {{
            const accountContainer = document.getElementById('{account_container_id}');
            const dropdown = document.getElementById('account-dropdown-menu');
            const arrow = document.getElementById('account-dropdown-arrow');
            const initialDropdownState = {str(st.session_state.show_account_dropdown).lower()};
            
            function toggleDropdown() {{
                const isOpen = dropdown.classList.contains('show');
                if (isOpen) {{
                    dropdown.classList.remove('show');
                    if (arrow) arrow.style.transform = 'rotate(0deg)';
                }} else {{
                    dropdown.classList.add('show');
                    if (arrow) arrow.style.transform = 'rotate(180deg)';
                }}
                
                // No need to update Streamlit state - just toggle UI
            }}
            
            // Initialize dropdown state
            if (initialDropdownState === 'true') {{
                dropdown.classList.add('show');
                if (arrow) arrow.style.transform = 'rotate(180deg)';
            }}
            
            // Click handler for account container
            if (accountContainer) {{
                accountContainer.addEventListener('click', function(e) {{
                    // Don't toggle if clicking inside dropdown
                    if (dropdown.contains(e.target)) {{
                        return;
                    }}
                    toggleDropdown();
                }});
            }}
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {{
                if (accountContainer && !accountContainer.contains(e.target)) {{
                    dropdown.classList.remove('show');
                    if (arrow) arrow.style.transform = 'rotate(0deg)';
                }}
            }});
            
            // Handle menu item clicks - direct navigation
            window.handleAccountMenuClick = function(action) {{
                // Close dropdown first
                dropdown.classList.remove('show');
                if (arrow) arrow.style.transform = 'rotate(0deg)';
                
                // Actions that need Streamlit state (settings, logout)
                if (action === 'settings' || action === 'logout') {{
                    // Find and click the hidden button
                    const button = document.querySelector('button[data-testid*="account_action_' + action + '"]');
                    if (button) {{
                        button.click();
                    }} else {{
                        // Fallback: use URL parameter
                        const url = new URL(window.location);
                        url.searchParams.set('account_action', action);
                        window.location.href = url.toString();
                    }}
                }} else {{
                    // Direct page navigation for other actions
                    const pageMap = {{
                        'profile': '/pages/profile',
                        'investment': '/pages/investment_preference',
                        'onboarding': '/pages/onboarding',
                        'mcp_tools': '/pages/mcp_tools'
                    }};
                    
                    if (pageMap[action]) {{
                        window.location.href = pageMap[action];
                    }}
                }}
            }};
        }})();
    </script>
    """, unsafe_allow_html=True)
    
    # Hidden buttons for settings and logout (completely hidden with CSS)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Settings", key="account_action_settings", help="설정 열기"):
            st.session_state.show_settings_modal = True
            st.rerun()
    with col2:
        if st.button("Logout", key="account_action_logout", help="로그아웃"):
            from src.middleware import auth_middleware
            auth_middleware.logout()
            st.rerun()
    
    # Hide the buttons completely
    st.markdown("""
    <style>
    button[data-testid*="account_action_settings"],
    button[data-testid*="account_action_logout"],
    button[data-testid*="account_action_settings"] ~ *,
    button[data-testid*="account_action_logout"] ~ *,
    [data-testid="column"]:has(button[data-testid*="account_action_settings"]),
    [data-testid="column"]:has(button[data-testid*="account_action_logout"]) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -9999px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Also check URL parameter as fallback
    query_params = st.query_params
    if "account_action" in query_params:
        action = query_params["account_action"]
        # Remove from URL
        st.query_params.clear()
        
        if action == "settings":
            st.session_state.show_settings_modal = True
            st.rerun()
        elif action == "logout":
            from src.middleware import auth_middleware
            auth_middleware.logout()
            st.rerun()


def _render_settings_modal(user, onboarding_status):
    """Render settings modal popup"""
    # Initialize modal state
    if "show_settings_modal" not in st.session_state:
        st.session_state.show_settings_modal = False
    if "settings_category" not in st.session_state:
        st.session_state.settings_category = "일반"
    
    # Show modal if opened - render as popup using HTML/CSS
    if st.session_state.show_settings_modal:
        categories = {
            "일반": "⚙️ 일반",
            "프로필": "👤 프로필",
            "투자": "📈 투자 선호도",
            "온보딩": "👋 온보딩",
            "도구": "🔧 MCP 도구",
            "API": "🔑 API 키"
        }
        
        # Generate category buttons HTML
        category_buttons_html = ""
        for cat_key, cat_label in categories.items():
            is_active = st.session_state.settings_category == cat_key
            active_class = "active" if is_active else ""
            category_buttons_html += f'''
            <button class="settings-modal-item {active_class}" 
                    data-category="{cat_key}"
                    onclick="handleCategoryChange('{cat_key}')">
                {cat_label}
            </button>
            '''
        
        # Generate content HTML
        content_html = _generate_settings_content_html(st.session_state.settings_category, onboarding_status)
        
        # Render modal popup - use JavaScript to append to body for proper positioning
        modal_html = f"""
        <div id="settings-modal-overlay" class="settings-modal-overlay" onclick="handleOverlayClick(event)">
            <div class="settings-modal" onclick="event.stopPropagation();">
                <div class="settings-modal-header">
                    <h2 style="margin: 0; padding: 1rem 1.5rem; font-size: 1.25rem; font-weight: 600;">설정</h2>
                    <button onclick="handleCloseModal()" 
                            style="
                                position: absolute;
                                top: 1rem;
                                right: 1rem;
                                background: transparent;
                                border: none;
                                color: rgba(255, 255, 255, 0.7);
                                font-size: 1.5rem;
                                cursor: pointer;
                                padding: 0.25rem 0.5rem;
                                border-radius: 0.25rem;
                                transition: all 0.2s;
                                line-height: 1;
                            "
                            onmouseover="this.style.backgroundColor='rgba(255,255,255,0.1)'; this.style.color='white';" 
                            onmouseout="this.style.backgroundColor='transparent'; this.style.color='rgba(255,255,255,0.7)';"
                    >×</button>
                </div>
                <div style="display: flex; flex-direction: row; height: calc(85vh - 60px);">
                    <div class="settings-modal-sidebar">
                        {category_buttons_html}
                    </div>
                    <div class="settings-modal-content">
                        {content_html}
                    </div>
                </div>
            </div>
        </div>
        """
        
        # 모달을 직접 body에 렌더링
        # HTML을 안전하게 이스케이프하여 JavaScript에 삽입
        import json
        modal_html_escaped = json.dumps(modal_html)
        
        st.markdown(f"""
        <div id="settings-modal-container" style="display: none;">{modal_html}</div>
        <script>
        (function() {{
            // Move modal to body for proper positioning
            function initModal() {{
                // Remove existing modal if any
                const existing = document.getElementById('settings-modal-overlay');
                if (existing) existing.remove();
                
                // Get modal HTML from container
                const container = document.getElementById('settings-modal-container');
                if (!container) return;
                
                const modalHtml = container.innerHTML;
                if (!modalHtml) return;
                
                // Try to find the correct body element (handle Streamlit iframe structure)
                let targetBody = null;
                
                // First, try current window's body
                if (document.body) {{
                    targetBody = document.body;
                }}
                
                // If in iframe, try parent window's body
                if (window.parent && window.parent !== window && window.parent.document && window.parent.document.body) {{
                    targetBody = window.parent.document.body;
                }}
                
                // Fallback to current document
                if (!targetBody) {{
                    targetBody = document.body || document.getElementsByTagName('body')[0];
                }}
                
                if (!targetBody) return;
                
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = modalHtml;
                const modalElement = tempDiv.firstElementChild;
                
                if (modalElement) {{
                    // Remove from container if it exists there
                    if (modalElement.parentNode) {{
                        modalElement.parentNode.removeChild(modalElement);
                    }}
                    
                    targetBody.appendChild(modalElement);
                    
                    // Ensure modal is visible
                    modalElement.style.display = 'flex';
                    modalElement.style.visibility = 'visible';
                    modalElement.style.opacity = '1';
                    
                    // Force z-index to be highest
                    modalElement.style.zIndex = '999999';
                }}
            }}
            
            // Initialize immediately
            initModal();
            
            // Also initialize after delays to ensure Streamlit is ready
            setTimeout(initModal, 50);
            setTimeout(initModal, 200);
            setTimeout(initModal, 500);
            setTimeout(initModal, 1000);
            
            // Watch for DOM changes
            const observer = new MutationObserver(function() {{
                const existing = document.getElementById('settings-modal-overlay');
                if (!existing) {{
                    setTimeout(initModal, 100);
                }} else {{
                    // Ensure it's visible
                    existing.style.display = 'flex';
                    existing.style.visibility = 'visible';
                    existing.style.opacity = '1';
                }}
            }});
            
            if (document.body) {{
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
            }}
            
            // Also observe parent window if in iframe
            if (window.parent && window.parent !== window && window.parent.document && window.parent.document.body) {{
                observer.observe(window.parent.document.body, {{
                    childList: true,
                    subtree: true
                }});
            }}
            
            // Category change handler
            window.handleCategoryChange = function(category) {{
                // Update hidden input to trigger Streamlit rerun
                const input = document.querySelector('input[data-testid*="settings_category_input"]');
                if (input) {{
                    input.value = category;
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
                // Also try to trigger Streamlit rerun via parent
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        key: 'settings_category_input',
                        value: category
                    }}, '*');
                }}
            }};
            
            // Close modal handler
            window.handleCloseModal = function() {{
                const checkbox = document.querySelector('input[data-testid*="close_settings_modal_input"]');
                if (checkbox) {{
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
                // Also try to trigger Streamlit rerun via parent
                if (window.parent) {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        key: 'close_settings_modal_input',
                        value: true
                    }}, '*');
                }}
            }};
            
            // Overlay click handler
            window.handleOverlayClick = function(event) {{
                if (event.target.id === 'settings-modal-overlay') {{
                    handleCloseModal();
                }}
            }};
            
            // Close on Escape key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    const overlay = document.getElementById('settings-modal-overlay');
                    if (overlay && overlay.style.display !== 'none') {{
                        handleCloseModal();
                    }}
                }}
            }});
        }})();
        </script>
        """, unsafe_allow_html=True)
        
        # Hidden inputs to handle interactions
        # Category change handler
        category_input = st.text_input(
            "Category",
            value=st.session_state.settings_category,
            key="settings_category_input",
            label_visibility="collapsed"
        )
        if category_input != st.session_state.settings_category:
            st.session_state.settings_category = category_input
            st.rerun()
        
        # Close handler
        close_input = st.checkbox(
            "Close",
            value=False,
            key="close_settings_modal_input",
            label_visibility="collapsed"
        )
        if close_input:
            st.session_state.show_settings_modal = False
            st.rerun()


def _generate_settings_content_html(category: str, onboarding_status: dict) -> str:
    """Generate HTML content for settings modal based on category"""
    if category == "일반":
        return """
        <div>
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">일반 설정</h3>
            <p style="color: rgba(255, 255, 255, 0.7);">일반 설정은 준비 중입니다.</p>
        </div>
        """
    
    elif category == "프로필":
        return """
        <div>
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">프로필</h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">프로필 정보를 확인하고 수정하세요.</p>
            <a href="/pages/profile" target="_self" 
               style="
                   display: inline-block;
                   background-color: rgba(255, 255, 255, 0.1);
                   border: 1px solid rgba(255, 255, 255, 0.2);
                   color: white;
                   padding: 0.5rem 1rem;
                   border-radius: 0.375rem;
                   cursor: pointer;
                   font-size: 0.875rem;
                   text-decoration: none;
                   transition: all 0.2s;
               "
               onmouseover="this.style.backgroundColor='rgba(255,255,255,0.15)';"
               onmouseout="this.style.backgroundColor='rgba(255,255,255,0.1)';"
            >프로필 페이지로 이동 →</a>
        </div>
        """
    
    elif category == "투자":
        return """
        <div>
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">투자 선호도</h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">투자 선호도를 설정하고 관리하세요.</p>
            <a href="/pages/investment_preference" target="_self" 
               style="
                   display: inline-block;
                   background-color: rgba(255, 255, 255, 0.1);
                   border: 1px solid rgba(255, 255, 255, 0.2);
                   color: white;
                   padding: 0.5rem 1rem;
                   border-radius: 0.375rem;
                   cursor: pointer;
                   font-size: 0.875rem;
                   text-decoration: none;
                   transition: all 0.2s;
               "
               onmouseover="this.style.backgroundColor='rgba(255,255,255,0.15)';"
               onmouseout="this.style.backgroundColor='rgba(255,255,255,0.1)';"
            >투자 선호도 페이지로 이동 →</a>
        </div>
        """
    
    elif category == "온보딩":
        if onboarding_status["completed"]:
            return """
            <div>
                <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">온보딩</h3>
                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">온보딩 정보를 다시 확인하거나 수정할 수 있습니다.</p>
                <a href="/pages/onboarding" target="_self" 
                   style="
                       display: inline-block;
                       background-color: rgba(255, 255, 255, 0.1);
                       border: 1px solid rgba(255, 255, 255, 0.2);
                       color: white;
                       padding: 0.5rem 1rem;
                       border-radius: 0.375rem;
                       cursor: pointer;
                       font-size: 0.875rem;
                       text-decoration: none;
                       transition: all 0.2s;
                   "
                   onmouseover="this.style.backgroundColor='rgba(255,255,255,0.15)';"
                   onmouseout="this.style.backgroundColor='rgba(255,255,255,0.1)';"
                >온보딩 페이지로 이동 →</a>
            </div>
            """
        else:
            return """
            <div>
                <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">온보딩</h3>
                <div style="
                    background-color: rgba(255, 193, 7, 0.1);
                    border: 1px solid rgba(255, 193, 7, 0.3);
                    border-radius: 0.375rem;
                    padding: 0.75rem;
                    margin-bottom: 1rem;
                    color: rgba(255, 193, 7, 0.9);
                ">
                    ⚠️ 온보딩을 먼저 완료하세요.
                </div>
                <a href="/pages/onboarding" target="_self" 
                   style="
                       display: inline-block;
                       background-color: rgba(255, 255, 255, 0.1);
                       border: 1px solid rgba(255, 255, 255, 0.2);
                       color: white;
                       padding: 0.5rem 1rem;
                       border-radius: 0.375rem;
                       cursor: pointer;
                       font-size: 0.875rem;
                       text-decoration: none;
                       transition: all 0.2s;
                   "
                   onmouseover="this.style.backgroundColor='rgba(255,255,255,0.15)';"
                   onmouseout="this.style.backgroundColor='rgba(255,255,255,0.1)';"
                >온보딩 시작하기 →</a>
            </div>
            """
    
    elif category == "도구":
        return """
        <div>
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">MCP 도구</h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">MCP 도구를 관리하고 설정하세요.</p>
            <a href="/pages/mcp_tools" target="_self" 
               style="
                   display: inline-block;
                   background-color: rgba(255, 255, 255, 0.1);
                   border: 1px solid rgba(255, 255, 255, 0.2);
                   color: white;
                   padding: 0.5rem 1rem;
                   border-radius: 0.375rem;
                   cursor: pointer;
                   font-size: 0.875rem;
                   text-decoration: none;
                   transition: all 0.2s;
               "
               onmouseover="this.style.backgroundColor='rgba(255,255,255,0.15)';"
               onmouseout="this.style.backgroundColor='rgba(255,255,255,0.1)';"
            >MCP 도구 페이지로 이동 →</a>
        </div>
        """
    
    elif category == "API":
        # API 키 설정은 Streamlit 컴포넌트가 필요하므로 안내 메시지 표시
        return """
        <div>
            <h3 style="margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">API 키 설정</h3>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">API 키를 설정하고 관리하세요.</p>
            <div style="
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 0.375rem;
                padding: 1rem;
                margin-bottom: 1rem;
            ">
                <p style="color: rgba(255, 255, 255, 0.6); font-size: 0.875rem; margin: 0;">
                    API 키 설정은 모달을 닫고 사이드바에서 관리할 수 있습니다.<br>
                    또는 설정 모달을 닫은 후 사이드바 하단의 사용자 정보를 다시 클릭하여 설정 메뉴를 열 수 있습니다.
                </p>
            </div>
        </div>
        """
    
    return ""


def _render_api_key_settings():
    """Render API key settings section (expander 내부에서 사용)"""
    
    # Initialize session_state
    if "user_openai_api_key" not in st.session_state:
        st.session_state.user_openai_api_key = ""
    if "user_anthropic_api_key" not in st.session_state:
        st.session_state.user_anthropic_api_key = ""
    
    # Get default values from environment variables
    from config.settings import settings
    default_openai_key = settings.openai_api_key or ""
    default_anthropic_key = settings.anthropic_api_key or ""
    
    # OpenAI API key input
    with st.expander("OpenAI API Key", expanded=False):
        current_openai_key = st.session_state.user_openai_api_key or default_openai_key
        if current_openai_key:
            # Display masked key
            masked_key = current_openai_key[:8] + "..." + current_openai_key[-4:] if len(current_openai_key) > 12 else "***"
            st.info(f"Currently set: `{masked_key}`")
        
        new_openai_key = st.text_input(
            "Enter OpenAI API Key",
            value="",
            type="password",
            placeholder="sk-...",
            key="openai_key_input",
            help="Enter OpenAI API key. If not entered, environment variable value will be used."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key="save_openai_key", use_container_width=True):
                if new_openai_key:
                    st.session_state.user_openai_api_key = new_openai_key
                    st.success("OpenAI API key has been saved!")
                    # Set session state flag for LLM client reinitialization
                    st.session_state.llm_client_needs_reload = True
                    st.rerun()
                else:
                    # Use environment variable value if empty
                    st.session_state.user_openai_api_key = ""
                    st.info("Using environment variable value.")
                    st.session_state.llm_client_needs_reload = True
                    st.rerun()
        
        with col2:
            if st.button("Clear", key="clear_openai_key", use_container_width=True):
                st.session_state.user_openai_api_key = ""
                st.info("Using environment variable value.")
                st.session_state.llm_client_needs_reload = True
                st.rerun()
    
    # Anthropic API key input
    with st.expander("Anthropic API Key", expanded=False):
        current_anthropic_key = st.session_state.user_anthropic_api_key or default_anthropic_key
        if current_anthropic_key:
            # Display masked key
            masked_key = current_anthropic_key[:8] + "..." + current_anthropic_key[-4:] if len(current_anthropic_key) > 12 else "***"
            st.info(f"Currently set: `{masked_key}`")
        
        new_anthropic_key = st.text_input(
            "Enter Anthropic API Key",
            value="",
            type="password",
            placeholder="sk-ant-...",
            key="anthropic_key_input",
            help="Enter Anthropic API key. If not entered, environment variable value will be used."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key="save_anthropic_key", use_container_width=True):
                if new_anthropic_key:
                    st.session_state.user_anthropic_api_key = new_anthropic_key
                    st.success("Anthropic API key has been saved!")
                    st.session_state.llm_client_needs_reload = True
                    st.rerun()
                else:
                    st.session_state.user_anthropic_api_key = ""
                    st.info("Using environment variable value.")
                    st.session_state.llm_client_needs_reload = True
                    st.rerun()
        
        with col2:
            if st.button("Clear", key="clear_anthropic_key", use_container_width=True):
                st.session_state.user_anthropic_api_key = ""
                st.info("Using environment variable value.")
                st.session_state.llm_client_needs_reload = True
                st.rerun()


def _check_onboarding_status(user_id: int) -> dict:
    """
    Check user's onboarding status.
    
    Returns:
        dict: {
            "completed": bool,
            "has_profile": bool,
            "has_preference": bool,
            "has_financial_situation": bool,
            "has_financial_goals": bool
        }
    """
    try:
        user_service = UserService()
        preference_service = InvestmentPreferenceService()
        financial_situation_repo = FinancialSituationRepository(db)
        financial_goal_repo = FinancialGoalRepository(db)
        
        # Check user profile
        user_with_profile = run_async(user_service.get_user_with_profile(user_id))
        has_profile = user_with_profile.profile is not None
        
        # Check investment preference
        preference = run_async(preference_service.get_preference(user_id))
        has_preference = preference is not None
        
        # Check financial situation
        has_financial_situation = False
        try:
            financial_situation = run_async(financial_situation_repo.get_by_user_id(user_id))
            has_financial_situation = financial_situation is not None
        except (DatabaseError, UserNotFoundError) as e:
            logger.debug(f"Could not check financial situation: {e}")
            pass
        
        # Check financial goals (optional)
        has_financial_goals = False
        try:
            financial_goals = run_async(financial_goal_repo.get_by_user_id(user_id))
            has_financial_goals = len(financial_goals) > 0 if financial_goals else False
        except (DatabaseError, UserNotFoundError) as e:
            logger.debug(f"Could not check financial goals: {e}")
            pass
        
        # Onboarding completion condition: profile, investment preference, and financial situation must all exist
        completed = has_profile and has_preference and has_financial_situation
        
        return {
            "completed": completed,
            "has_profile": has_profile,
            "has_preference": has_preference,
            "has_financial_situation": has_financial_situation,
            "has_financial_goals": has_financial_goals
        }
    except Exception as e:
        # Consider onboarding incomplete if error occurs
        return {
            "completed": False,
            "has_profile": False,
            "has_preference": False,
            "has_financial_situation": False,
            "has_financial_goals": False
        }

