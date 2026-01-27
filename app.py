import streamlit as st
import json
import os
import sys
import time
import pandas as pd
from openai import OpenAI
from github import Github 

# ===========================
# 0. 基础路径 & 引入模块
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from engine_manager import render_sidebar, WAREHOUSE, init_data
from style_manager import apply_pro_style

# ========================================================
# 1. GitHub 同步核心逻辑 (已移除 Text 路径搜索)
# ========================================================

def find_remote_file_path(repo, category):
    """在 GitHub 仓库里找真实文件路径 (仅搜索 graphic 和 common 目录)"""
    clean_cat = category.strip().lower()
    candidates = [
        f"{clean_cat}.txt",
        f"styles_{clean_cat}.txt",
        f"{clean_cat}s.txt",
        f"styles_{clean_cat}s.txt"
    ]
    
    # 仅搜索 graphic 目录 (已删除 data/text)
    for d in ["data/graphic", "data/common"]:
        try:
            contents = repo.get_contents(d)
            for file in contents:
                if file.name.lower() in candidates:
                    return file.path
        except:
            continue
    # 如果找不到，默认保存到 graphic
    return f"data/graphic/{category}.txt"

def save_category_to_disk(category, new_list):
    """
    连接 GitHub 并提交修改 (方案 A：直接写回仓库)
    """
    try:
        # 从 Streamlit Secrets 获取权限
        secrets = st.secrets["general"] if "general" in st.secrets else st.secrets
        token = secrets["GITHUB_TOKEN"]
        repo_name = secrets["REPO_NAME"]
        branch = secrets.get("BRANCH", "main")
    except KeyError:
        st.error("❌ Secrets 配置缺失！请检查 GITHUB_TOKEN 和 REPO_NAME")
        return False

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        file_path = find_remote_file_path(repo, category)
        content_str = "\n".join([str(x).strip() for x in new_list if str(x).strip()])
        
        st.toast(f"⏳ 正在同步 GitHub: {file_path}...", icon="☁️")
        
        try:
            # 获取现有文件 sha 进行更新
            contents = repo.get_contents(file_path, ref=branch)
            repo.update_file(
                path=contents.path,
                message=f"Update {category} via Web UI",
                content=content_str,
                sha=contents.sha,
                branch=branch
            )
            st.toast(f"✅ 同步成功！GitHub 记录已更新", icon="🎉")
            return True
        except:
            # 文件不存在则新建
            repo.create_file(
                path=file_path,
                message=f"Create {category} via Web UI",
                content=content_str,
                branch=branch
            )
            st.toast(f"✅ 新建成功！文件已同步至 GitHub", icon="✨")
            return True
            
    except Exception as e:
        st.error(f"💥 GitHub 同步失败: {e}")
        return False

# ===========================
# 2. 页面初始化
# ===========================
st.set_page_config(layout="wide", page_title="ultraT Engine V2")
apply_pro_style()

if "db_all" not in st.session_state:
    init_data()

render_sidebar()

# 初始化 AI 客户端
client = None
if "DEEPSEEK_KEY" in st.secrets:
    try:
        client = OpenAI(
            api_key=st.secrets["DEEPSEEK_KEY"],
            base_url="https://api.deepseek.com"
        )
    except:
        pass

if "ai_results" not in st.session_state: st.session_state.ai_results = []
if "input_text" not in st.session_state: st.session_state.input_text = ""

# ===========================
# 3. 界面布局
# ===========================
st.markdown("## ultraT Engine V2") 
st.markdown("---")

col_ingest, col_warehouse = st.columns([2, 1])

# ---------------------------------------------------------
# 左侧：智能解析 (AI Parser)
# ---------------------------------------------------------
with col_ingest:
    st.markdown("### Smart Ingest (DeepSeek Parser)")
    
    st.session_state.input_text = st.text_area(
        "Raw Input",
        st.session_state.input_text,
        height=200,
        placeholder="粘贴产品需求、拍摄灵感或场景关键词...",
        label_visibility="collapsed"
    )

    if st.button("✨ Start Analysis", use_container_width=True, type="primary"):
        if not st.session_state.input_text:
            st.warning("Input is empty.")
        elif not client:
            st.error("DeepSeek API Key missing.")
        else:
            with st.spinner("AI 正在解构灵感..."):
                prompt = f"""
                任务：将描述文本拆解为结构化关键词。
                
                【输出格式】
                请直接返回纯 JSON 数据，格式如下：
                {{
                    "Subject": ["词1", "词2"],
                    "Action": ["词1"],
                    "Mood": ["词1"],
                    "StyleSystem": ["词1"]
                }}
                
                可用Key: Subject, Action, Mood, StyleSystem, Technique, Color, Texture, Composition, Accent

                输入文本：{st.session_state.input_text}
                """
                
                try:
                    res_obj = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    res = res_obj.choices[0].message.content
                    clean_json = res.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    parsed = []
                    for cat, words in data.items():
                        target_key = next((k for k in WAREHOUSE if k.lower() in cat.lower()), None)
                        if target_key and isinstance(words, list):
                            for w in words:
                                parsed.append({"cat": target_key, "val": w.strip()})
                    st.session_state.ai_results = parsed

                except Exception as e:
                    st.error(f"Analysis Error: {e}")

    # 展示 AI 解析结果
    if st.session_state.ai_results:
        st.divider()
        st.subheader("Analysis Results")
        selected_to_import = []
        res_cols = st.columns(3)
        for i, item in enumerate(st.session_state.ai_results):
            with res_cols[i % 3]:
                if st.checkbox(f"**{item['cat']}** : {item['val']}", key=f"res_{i}", value=True):
                    selected_to_import.append(item)
        
        if st.button("📥 Import to Warehouse & Sync to GitHub", use_container_width=True):
            changed_cats = set()
            for item in selected_to_import:
                cat, val = item["cat"], item["val"]
                if val not in st.session_state.db_all.get(cat, []):
                    st.session_state.db_all.setdefault(cat, []).append(val)
                    changed_cats.add(cat)
            
            if changed_cats:
                for c in changed_cats:
                    save_category_to_disk(c, st.session_state.db_all[c])
                st.session_state.ai_results = []
                st.rerun()

# ---------------------------------------------------------
# 右侧：仓库管理 (Warehouse)
# ---------------------------------------------------------
with col_warehouse:
    st.markdown("### Warehouse")
    valid_cats = [k for k, v in st.session_state.db_all.items() if isinstance(v, list)]
    target_cat = st.selectbox("Category", valid_cats, label_visibility="collapsed")
    current_words = st.session_state.db_all.get(target_cat, [])

    with st.container(height=500, border=True):
        for i, word in enumerate(current_words):
            r1, r2 = st.columns([0.8, 0.2])
            with r1:
                if st.button(word, key=f"w_{target_cat}_{i}", use_container_width=True):
                    st.session_state.input_text += f" {word}"
                    st.rerun()
            with r2:
                if st.button("✕", key=f"d_{target_cat}_{i}", use_container_width=True):
                    new_list = [w for w in current_words if w != word]
                    st.session_state.db_all[target_cat] = new_list
                    save_category_to_disk(target_cat, new_list)
                    st.rerun()

    st.divider()
    c_in, c_btn = st.columns([3, 1])
    with c_in:
        new_word = st.text_input("Add", placeholder="New tag...", label_visibility="collapsed")
    with c_btn:
        if st.button("Add", use_container_width=True):
            if new_word and new_word not in current_words:
                current_words.append(new_word)
                st.session_state.db_all[target_cat] = current_words
                save_category_to_disk(target_cat, current_words)
                st.rerun()
