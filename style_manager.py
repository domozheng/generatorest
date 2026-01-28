import streamlit as st

def apply_pro_style():
    # 引入 Apple 风格的 Inter 字体
    font_url = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Sans+SC:wght@300;400&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 字体保护 (解决乱码的关键)
           ============================ */
        html, body, p, label, button, input, textarea, h1, h2, h3, h4, h5, h6, .stMarkdown {{ 
            font-family: 'Inter', 'Noto Sans SC', sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }}
        
        /* 强制保护图标字体，防止出现 arr... 或 MOD... 乱码 */
        .material-icons, .material-symbols-rounded, [data-testid="stExpander"] svg, [data-testid="stSidebarNav"] svg {{
            font-family: 'Material Icons', 'Material Symbols Rounded', sans-serif !important;
        }}

        /* ============================
           2. 液态渐变背景 (Liquid Background)
           ============================ */
        .stApp {{
            background: radial-gradient(circle at 0% 0%, #e0c3fc 0%, #8ec5fc 100%);
            background-attachment: fixed;
        }}

        /* ============================
           3. 玻璃拟态容器 (Glassmorphism)
           ============================ */
        /* 针对所有卡片、输入框、折叠面板的玻璃化 */
        div[data-testid="stVerticalBlockBorderWrapper"], 
        div.stExpander, 
        .stTextArea textarea, 
        .stTextInput input {{
            background: rgba(255, 255, 255, 0.4) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
            color: #1d1d1f !important;
        }}

        /* 修正输入框聚焦态 */
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border: 1px solid rgba(0, 122, 255, 0.5) !important;
            background: rgba(255, 255, 255, 0.6) !important;
            box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1) !important;
        }}

        /* ============================
           4. 苹果胶囊按钮 (Liquid Button)
           ============================ */
        div.stButton > button {{
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 50px !important; /* 完美的胶囊圆角 */
            color: #007AFF !important; /* 苹果蓝 */
            padding: 10px 24px !important;
            font-weight: 500 !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }}

        /* 主按钮：实色苹果蓝，白色文字 */
        div.stButton > button[kind="primary"] {{
            background: #007AFF !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3) !important;
        }}

        div.stButton > button:hover {{
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1) !important;
        }}

        /* ============================
           5. 侧边栏与导航 (Frosted Sidebar)
           ============================ */
        [data-testid="stSidebar"] {{
            background: rgba(245, 245, 247, 0.5) !important;
            backdrop-filter: blur(30px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
        }}

        /* 去掉所有分割线，改用间距感 */
        hr {{ border: none !important; border-top: 1px solid rgba(0,0,0,0.05) !important; }}

        /* 修正文字颜色 */
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span {{
            color: #1d1d1f !important;
        }}
        
        .block-container {{ padding-top: 4rem !important; }}

    </style>
    """, unsafe_allow_html=True)
