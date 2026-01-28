import streamlit as st

def apply_pro_style():
    # 引入 Inter 字体 (最接近苹果 SF Pro 的字体)
    font_url = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 整体底色与字体
           ============================ */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: #F5F5F7 !important;
            font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif !important;
        }}
        
        .stApp {{
            background-color: #F5F5F7 !important;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label {{
            color: #1D1D1F !important; /* 苹果标志性的深灰黑 */
            font-family: 'Inter', 'Noto Sans SC', sans-serif !important;
        }}

        /* ============================
           2. 容器与卡片设计 (Apple Card Style)
           ============================ */
        /* 给主要交互区域增加白色圆角卡片感 */
        div[data-testid="stVerticalBlockBorderWrapper"], 
        div.stExpander, 
        .stTextArea textarea, 
        .stTextInput input {{
            background-color: #FFFFFF !important;
            border: 1px solid #D2D2D7 !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            transition: all 0.3s ease;
        }}
        
        /* 悬停效果 */
        div.stExpander:hover {{
            border-color: #007AFF !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        }}

        /* ============================
           3. 侧边栏 (苹果灰风格)
           ============================ */
        [data-testid="stSidebar"] {{
            background-color: #F5F5F7 !important;
            border-right: 1px solid #D2D2D7 !important;
        }}
        
        /* 侧边栏文字颜色 */
        [data-testid="stSidebar"] * {{
            color: #1D1D1F !important;
        }}

        /* ============================
           4. 苹果蓝按钮 (Apple Blue)
           =========================== */
        div.stButton > button {{
            background-color: #FFFFFF !important;
            color: #007AFF !important;
            border: 1px solid #007AFF !important;
            border-radius: 20px !important; /* 更加圆润的按钮 */
            padding: 0.5rem 1.5rem !important;
            font-weight: 500 !important;
        }}
        
        /* 主按钮 (Primary) 风格 */
        div.stButton > button[kind="primary"] {{
            background-color: #007AFF !important;
            color: #FFFFFF !important;
            border: none !important;
        }}
        
        div.stButton > button:hover {{
            background-color: #007AFF !important;
            color: #FFFFFF !important;
            opacity: 0.8;
        }}

        /* ============================
           5. 搜索框与输入框
           =========================== */
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: #007AFF !important;
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1) !important;
        }}

        /* ============================
           6. 修复重叠与布局
           =========================== */
        .block-container {{
            padding-top: 2rem !important;
        }}
        
        /* 保持图标字体正常 */
        .material-icons, svg {{
            fill: #1D1D1F !important;
        }}

    </style>
    """, unsafe_allow_html=True)
