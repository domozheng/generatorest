import streamlit as st

def apply_pro_style():
    font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap"
    
    st.markdown(f"""
    <style>
        @import url('{font_url}');

        /* ============================
           1. 字体修复 (👉 关键修复点)
           ============================ */
        /* 之前是强制所有元素(div, span)都换字体，导致 Icon 图标变成了文字乱码。
           现在改为只针对真正的“文本标签”应用字体。 */
        html, body, p, label, button, input, textarea, h1, h2, h3, h4, h5, h6, .stMarkdown {{ 
            font-family: 'Poppins', 'Noto Sans SC', sans-serif !important;
            color: #d0d0d0; 
        }}
        
        /* 保护 Streamlit 的图标字体不被覆盖 */
        .material-icons, .material-symbols-rounded, [data-testid="stExpander"] svg {{
            font-family: 'Material Icons', 'Material Symbols Rounded', sans-serif !important;
        }}

        .stApp {{ background-color: #000000; }}

        /* ============================
           2. 布局修正
           ============================ */
        .block-container {{
            padding-top: 3rem !important; /* 稍微留点呼吸感 */
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }}
       
        
        /* 隐藏掉不需要的 Header 元素，但保留布局空间 */
        #MainMenu, footer {{ visibility: hidden !important; }} 
        header {{ 
            background-color: transparent !important;
        }}

        /* ============================
           3. 控件纯黑化 (输入框、下拉框)
           ============================ */
        div[data-baseweb="select"] > div {{
            background-color: #0a0a0a !important;
            border-color: #333 !important;
            color: #eee !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
        }}
        li[role="option"] {{ color: #ccc !important; }}
        li[role="option"]:hover {{ background-color: #1a1a1a !important; }}
        li[aria-selected="true"] {{ background-color: #222 !important; color: #fff !important; }}
        
        /* 输入框去红 */
        .stTextArea textarea, .stTextInput input {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
            caret-color: #fff !important; 
        }}
        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: #777 !important; 
            box-shadow: none !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: #0a0a0a !important;
            border: 1px solid #333 !important;
            color: #e0e0e0 !important;
        }}

        /* ============================
           4. 工业风按钮
           =========================== */
        div.stButton > button {{
            background-color: #000000 !important;
            color: #ccc !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            transition: all 0.2s;
        }}
        div.stButton > button:hover {{
            background-color: #1a1a1a !important;
            border-color: #888 !important;
            color: #fff !important;
        }}
        
        /* 针对“反选”等特殊按钮的微调 */
        div.stButton > button:active {{
            background-color: #333 !important;
            color: #fff !important;
        }}

        /* ============================
           5. 侧边栏 & Expander 修复
           =========================== */
        [data-testid="stSidebar"] {{ 
            background-color: #0a0a0a !important; 
            border-right: 1px solid #1a1a1a !important; 
        }}
        
        /* 修复 Expander 的标题样式，防止它也继承错误的 CSS */
        div[data-testid="stExpander"] details summary {{
            color: #e0e0e0 !important;
            font-size: 1.1em !important;
        }}
        
        /* 修复左上角 Logo 区域的层级问题 */
        [data-testid="stSidebarNav"] {{
            padding-top: 1rem !important;
        }}

    </style>
    """, unsafe_allow_html=True)
