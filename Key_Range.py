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
# 1. 核心逻辑：选择范围管理 (修复版)
# ==========================================

def init_selection_state():
    """初始化选择状态"""
    if "selected_range" not in st.session_state:
        st.session_state.selected_range = {}
        # 遍历所有类目
        for cat in WAREHOUSE.keys():
            all_words = st.session_state.db_all.get(cat, [])
            # 初始化字典：词 -> 是否选中 (默认 True)
            st.session_state.selected_range[cat] = {word: True for word in all_words}

def handle_bulk_selection(cat, action):
    """
    全选/清空/反选 处理函数
    关键修复：不仅要更新 selected_range 数据，还要强制更新 checkbox 的 widget key
    """
    all_words = st.session_state.db_all.get(cat, [])
    
    for word in all_words:
        # 复选框的唯一 Key
        widget_key = f"cb_{cat}_{word}"
        
        # 获取当前状态
        current_state = st.session_state.selected_range[cat].get(word, True)
        
        # 计算新状态
        if action == "all":
            new_state = True
        elif action == "none":
            new_state = False
        elif action == "invert":
            new_state = not current_state # 取反
        else:
            new_state = current_state

        # 1. 更新后台数据字典
        st.session_state.selected_range[cat][word] = new_state
        
        # 2. 强制更新 Streamlit 组件状态 (这是修复按钮失效的关键!)
        # 如果组件已经被渲染过，它的 key 会存在于 session_state 中
        st.session_state[widget_key] = new_state

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
st.markdown("## Key Range")
st.caption("勾选你想要发送deepseek润色的关键词范围")
st.markdown("---")

# 按类目平铺显示
for cat in WAREHOUSE.keys():
    all_words = st.session_state.db_all.get(cat, [])
    if not all_words: continue

    # 修复点 1：移除 emoji，防止字符冲突显示为乱码
    label_text = f"{cat}  ({len(all_words)} Items)"
    
    # 创建一个可折叠的类目块
    with st.expander(label_text, expanded=False):
        
        # 第一行：功能按钮 (全选 | 清空 | 反选)
        # 布局调整：三个按钮并排
        c_btn1, c_btn2, c_btn3, _ = st.columns([1, 1, 1, 5])
        
        with c_btn1:
            if st.button(f"全选", key=f"all_{cat}", use_container_width=True):
                handle_bulk_selection(cat, "all")
                st.rerun()
        with c_btn2:
            if st.button(f"清空", key=f"none_{cat}", use_container_width=True):
                handle_bulk_selection(cat, "none")
                st.rerun()
        with c_btn3:
            # 新增：反选按钮
            if st.button(f"反选", key=f"inv_{cat}", use_container_width=True):
                handle_bulk_selection(cat, "invert")
                st.rerun()

        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

        # 第二行：平铺关键词复选框
        cols = st.columns(5)
        for i, word in enumerate(all_words):
            with cols[i % 5]:
                # 构造唯一 Key
                w_key = f"cb_{cat}_{word}"
                
                # 确保 Session State 里有这个 Key 的初始值 (防止报错)
                if w_key not in st.session_state:
                    st.session_state[w_key] = st.session_state.selected_range[cat].get(word, True)
                
                # 渲染复选框
                # 注意：这里不再用 value=... 而是依赖 st.session_state[w_key] 的自动绑定
                new_val = st.checkbox(word, key=w_key)
                
                # 监听手动点击：如果用户手动点了，同步回 selected_range
                st.session_state.selected_range[cat][word] = new_val

st.markdown("---")

# ===========================
# 4. 发送指令
# ===========================
if st.button("将关键词范围发送至 Work Space", type="primary", use_container_width=True):
    # 计算当前选中的有效数据
    final_dispatch = {}
    total_count = 0
    
    for cat, words_dict in st.session_state.selected_range.items():
        # 这里要重新从 checkboxes 的实际状态取值，确保万无一失
        selected_list = []
        for w in words_dict.keys():
            # 检查组件状态
            w_key = f"cb_{cat}_{w}"
            if st.session_state.get(w_key, True): # 默认为 True
                selected_list.append(w)
                
        final_dispatch[cat] = selected_list
        total_count += len(selected_list)
    
    # 将过滤后的名单存入 session_state 供其他页面读取
    st.session_state.active_pool = final_dispatch
    
    st.toast(f"已选择共计 {total_count} 个关键词进入随机池", icon="🎯")
    time.sleep(1)
    st.switch_page("pages/01_Graphic_Lab.py")
