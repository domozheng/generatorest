import streamlit as st
import sys
import os
import random
import time
from openai import OpenAI

# ===========================
# 0. 环境路径设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置与初始化
# ===========================
st.set_page_config(layout="wide", page_title="Graphic Lab | AI KV Engine")
apply_pro_style()
render_sidebar()
init_data()

client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"], base_url="https://api.deepseek.com")
    except:
        pass

# ==========================================
# 2. 核心智能抽取引擎 (适配筛选系统)
# ==========================================
def smart_pick(category, count=1):
    """
    智能挑选函数：
    1. 优先从 st.session_state.active_pool (用户手动筛选的范围) 中抽取
    2. 如果没设置筛选范围，则从全局 db_all 中抽取
    """
    # 优先检查筛选后的活动池
    active_pool = st.session_state.get("active_pool", {})
    items = active_pool.get(category, [])
    
    # 如果活动池为空，则回退到全局数据库
    if not items:
        db = st.session_state.get("db_all", {})
        items = db.get(category, [])
        
    if not items: return []
    
    actual_count = min(count, len(items))
    return random.sample(items, actual_count)

# ===========================
# 3. 界面交互
# ===========================
st.markdown("## Work Space")
st.caption("基于选定关键词范围生成KV方案")

# 检查当前筛选状态
active_pool = st.session_state.get("active_pool", {})
if not active_pool:
    st.warning("你未选择关键词范围，将从全局随机组合关键词")
else:
    st.info(f"点击按钮以在筛选范围中随机组合关键词")

c1, c2 = st.columns([3, 1])
with c1:
    user_idea = st.text_input("Core Idea", placeholder="输入核心创意点", label_visibility="collapsed")
with c2:
    qty = st.number_input("Batch", 1, 8, 4, label_visibility="collapsed")

# ===========================
# 4. 执行生成 (DeepSeek 商业视觉润色)
# ===========================
if st.button("开始提示词生成", type="primary", use_container_width=True):
    
    st.session_state.graphic_solutions = [] 
    placeholders = []   
    skeletons = []      
    
    for i in range(qty):
        ph = st.empty()
        placeholders.append(ph)
        
        # 核心逻辑：从智能抽取的词库中拼装
        r_style = smart_pick("StyleSystem", 1)
        r_subject = smart_pick("Subject", 1)
        r_tech = smart_pick("Technique", 1)
        r_color = smart_pick("Color", 1)
        r_mood = smart_pick("Mood", 1)
        
        # 语义拼装
        sk_parts = []
        if user_idea: sk_parts.append(user_idea.strip())
        if r_subject: sk_parts.append(r_subject[0])
        if r_style: sk_parts.append(r_style[0])
        if r_tech: sk_parts.append(r_tech[0])
        if r_mood: sk_parts.append(r_mood[0])
        
        sk = ", ".join(sk_parts)
        skeletons.append(sk)
        
        with ph.container(border=True):
            st.markdown(f"**草案{i+1}：** `{sk}`")
            st.caption("提示词生成中...") 
    
    # --- DeepSeek 创意总监指令 (DJI/GoPro 风格适配) ---
    sys_prompt = """你是一名曾服务于 DJI 和 GoPro 和 Apple等顶级消费电子公司的资深创意总监。
    任务：将给定的【视觉关键词骨架】转化为极具冲击力的产品 Key Visual (KV) 预热海报描述词。
    规则：
    1. 必须保留用户输入的卖点关键词，并作为核心视觉。
    2. 整体服务于关键词中提到的核心卖点和核心创意点。
    3. 语言风格：冷硬、极简、高级感。必须包含 Cinema Grade、Rim Lighting 或 Industrial Design 等专业术语。
    """

    final_results = []

    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        
        user_prompt = f"【视觉骨架】：{sk} \n 请基于此骨架生成一段 100 字以内的专业 KV 描述词，以 '**方案{idx}：**' 开头。"
        
        try:
            ph.empty()
            with ph.container(border=True):
                if client:
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": sys_prompt},{"role": "user", "content": user_prompt}],
                        temperature=0.85, 
                        stream=True 
                    )
                    full_response = st.write_stream(stream)
                else:
                    full_response = f"**方案{idx}：** {sk} (AI Offline)"
                    st.write(full_response)
        except Exception as e:
            full_response = f"**方案{idx}：** {sk} (Error)"
            ph.markdown(full_response)

        final_results.append(full_response)

    st.session_state.graphic_solutions = final_results

# ===========================
# 5. 结果处理
# ===========================
if "graphic_solutions" in st.session_state and st.session_state.graphic_solutions:
    st.markdown("---")
    
    c_send, c_clear = st.columns([3, 1])
    with c_send:
        if st.button("发送至自动化流水线", type="primary", use_container_width=True):
            if "global_queue" not in st.session_state:
                st.session_state.global_queue = []
            st.session_state.global_queue.extend(st.session_state.graphic_solutions)
            st.toast(f"已添加 {len(st.session_state.graphic_solutions)} 组方案到队列")
            time.sleep(0.5)
            st.switch_page("pages/03_Automation.py")
            
    with c_clear:
        if st.button("清空所有结果", use_container_width=True):
            st.session_state.graphic_solutions = []
            st.rerun()
