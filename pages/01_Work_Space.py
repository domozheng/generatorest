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
# 2. 核心智能抽取引擎 (已修改为严格模式)
# ==========================================
def smart_pick(category, count=1):
    """
    智能挑选函数 (逻辑修正版)：
    1. 如果用户设定了筛选范围 (active_pool 存在)：
       - 严格从 active_pool 里取词。
       - 如果 active_pool 里该分类为空（用户全不选），则返回空列表 []。
       - ❌ 绝不回退到全局数据库。
       
    2. 如果用户完全没设定过范围 (active_pool 不存在)：
       - 为了防止程序跑空，才回退到全局 db_all 随机抽取。
    """
    # 获取活动池，如果没设置过，默认为 None
    active_pool = st.session_state.get("active_pool", None)

    if active_pool is not None:
        # 【严格模式】用户已经锁定了范围
        # 直接获取，如果是空的，items 就是空列表
        items = active_pool.get(category, [])
    else:
        # 【全随机模式】用户没设置范围，使用全局库保底
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
active_pool = st.session_state.get("active_pool", None)

if active_pool is None:
    st.warning("⚠️ 提示：你尚未锁定关键词范围，目前处于【全局全随机】模式。")
else:
    # 简单的统计，让用户知道哪些类目是“空”的（即不会被生成的）
    empty_cats = [k for k, v in active_pool.items() if not v]
    if empty_cats:
        st.info(f"🎯 范围已锁定。注意：以下类目因未勾选任何词，将不会参与生成：{', '.join(empty_cats)}")
    else:
        st.success(f"🎯 范围已锁定，所有类目均有备选词。")

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
        # 如果 smart_pick 返回空列表，对应的变量就是 None 或空
        r_subject = smart_pick("Subject", 1)
        r_reference = smart_pick("Reference", 1)
        r_scene = smart_pick("Scene", 1)
        r_action = smart_pick("Action", 1)
        r_lighting = smart_pick("Lighting", 1)
        r_lensLanguage = smart_pick("LensLanguage", 1)
        r_elements = smart_pick("Elements", 1)
        r_composition = smart_pick("Composition", 1)
        r_color = smart_pick("Color", 1)
        r_mood = smart_pick("Mood", 1)
        r_usage = smart_pick("Usage", 1)
        r_lookLike = smart_pick("LookLike", 1)
        
        # 语义拼装 (Only append if the list is valid)
        sk_parts = []
        if user_idea: sk_parts.append(user_idea.strip())
        if r_subject: sk_parts.append(r_subject[0])
        if r_reference: sk_parts.append(r_reference[0])
        if r_scene: sk_parts.append(r_scene[0])
        if r_action: sk_parts.append(r_action[0])
        if r_lighting: sk_parts.append(r_lighting[0])
        if r_lensLanguage: sk_parts.append(r_lensLanguage[0])
        if r_elements: sk_parts.append(r_elements[0])
        if r_composition: sk_parts.append(r_composition[0])
        if r_color: sk_parts.append(r_color[0])
        if r_mood: sk_parts.append(r_mood[0])
        if r_usage: sk_parts.append(r_usage[0])
        if r_lookLike: sk_parts.append(r_lookLike[0])
        
        # 只有当骨架不为空时才生成
        if sk_parts:
            sk = ", ".join(sk_parts)
            skeletons.append(sk)
            
            with ph.container(border=True):
                st.markdown(f"**草案{i+1}：** `{sk}`")
                st.caption("提示词生成中...")
        else:
            with ph.container(border=True):
                st.warning(f"**草案{i+1}：** 关键词为空，请至少勾选一个类目或输入 Core Idea。")
    
    # --- DeepSeek 创意总监指令 (DJI/GoPro 风格适配) ---
    sys_prompt = """你是一名曾服务于 DJI 和 GoPro 和 Apple等顶级消费电子公司的资深创意总监。
    任务：将给定的【关键词】转化为极具冲击力的产品 Key Visual (KV) 预热海报描述词。
    规则：
    1. 必须保留用户输入的关键词，并理解关键词的属性分类
    2. 将不同类别的描述词按：【这是一张【图片属性（如：线稿图）】，图中描述了用“镜头语言”拍摄的“主体”在“地点”发生了“动作”】这一基本顺序的框架填充
    3. 整体服务于关键词中提到的核心卖点和核心创意点（如有提到）
    """

    final_results = []

    # 仅处理有效的骨架
    for i, sk in enumerate(skeletons):
        idx = i + 1
        ph = placeholders[i]
        
        user_prompt = f"【视觉骨架】：{sk} \n 请基于此骨架生成一段 150 字以内的专业 KV 描述词，以 '**方案{idx}：**' 开头。"
        
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
