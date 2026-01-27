import streamlit as st
import os
import sys
import time

# ===========================
# 0. 基础路径 & 引入模块
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from engine_manager import render_sidebar, WAREHOUSE, init_data
from style_manager import apply_pro_style

# ==========================================
# 1. 核心逻辑：选择范围管理
# ==========================================

def init_selection_state():
    """初始化选择状态，默认全选"""
    if "selected_range" not in st.session_state:
        st.session_state.selected_range = {}
        for cat in WAREHOUSE.keys():
            # 初始状态：每个词都标记为 True (选中)
            all_words = st.session_state.db_all.get(cat, [])
            st.session_state.selected_range[cat] = {word: True for word in all_words}

def handle_bulk_selection(cat, action):
    """全选或反选处理"""
    all_words = st.session_state.db_all.get(cat, [])
    if action == "all":
        for word in all_words: st.session_state.selected_range[cat][word] = True
    else:
        for word in all_words: st.session_state.selected_range[cat][word] = False

# ===========================
# 2. 页面配置与初始化
# ===========================
st.set_page_config(layout="wide", page_title="ultraT Control Center")
apply_pro_style()

if "db_all" not in st.session_state:
    init_data()

init_selection_state()
render_sidebar()

# ===========================
# 3. 界面布局：关键词范围控制系统
# ===========================
st.markdown("## ⚙️ 关键词随机范围控制系统")
st.caption("勾选你想要在 Graphic Lab 中随机出现的关键词。未勾选的词将不会被引擎选中。")
st.markdown("---")

# 按类目平铺显示
for cat in WAREHOUSE.keys():
    all_words = st.session_state.db_all.get(cat, [])
    if not all_words: continue

    # 创建一个可折叠的类目块
    with st.expander(f"📂 {cat} ({len(all_words)} Items)", expanded=False):
        # 第一行：功能按钮
        c_btn1, c_btn2, _ = st.columns([1, 1, 6])
        with c_btn1:
            if st.button(f"全选", key=f"all_{cat}", use_container_width=True):
                handle_bulk_selection(cat, "all")
                st.rerun()
        with c_btn2:
            if st.button(f"清空", key=f"none_{cat}", use_container_width=True):
                handle_bulk_selection(cat, "none")
                st.rerun()

        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

        # 第二行：平铺关键词复选框
        # 使用每行 5 个的栅格布局
        cols = st.columns(5)
        for i, word in enumerate(all_words):
            with cols[i % 5]:
                # 绑定到 session_state
                is_selected = st.session_state.selected_range[cat].get(word, True)
                new_val = st.checkbox(word, value=is_selected, key=f"cb_{cat}_{word}")
                st.session_state.selected_range[cat][word] = new_val

st.markdown("---")

# ===========================
# 4. 发送指令
# ===========================
if st.button("🚀 将关键词范围发送至 Graphic Lab", type="primary", use_container_width=True):
    # 计算当前选中的有效数据
    final_dispatch = {}
    total_count = 0
    
    for cat, words_dict in st.session_state.selected_range.items():
        selected_list = [w for w, val in words_dict.items() if val]
        final_dispatch[cat] = selected_list
        total_count += len(selected_list)
    
    # 将过滤后的名单存入 session_state 供其他页面读取
    st.session_state.active_pool = final_dispatch
    
    st.toast(f"✅ 范围已锁定！共计 {total_count} 个关键词进入随机池。", icon="🎯")
    time.sleep(1)
    st.switch_page("pages/01_Graphic_Lab.py")
