import streamlit as st
import sys
import os
import random
import time
import urllib.parse

# ===========================
# 0. 基础设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

try:
    from streamlit import fragment
except ImportError:
    fragment = lambda x: x

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = set()

def load_local_text_data_force():
    data_path = os.path.join(parent_dir, "data", "text")
    local_db = {}
    if not os.path.exists(data_path): return {}
    try:
        files = os.listdir(data_path)
        target_files = [f for f in files if "text_" in f]
        for f in target_files:
            full_path = os.path.join(data_path, f)
            try:
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except:
                continue
            words = [line.strip() for line in content.split('\n') if line.strip()]
            local_db[f] = words
    except: pass
    return local_db

def toggle_selection(file_name):
    if file_name in st.session_state.selected_assets:
        st.session_state.selected_assets.remove(file_name)
    else:
        st.session_state.selected_assets.add(file_name)

def delete_asset(file_path, file_name):
    try:
        if os.path.exists(file_path): os.remove(file_path)
        if file_name in st.session_state.selected_assets:
            st.session_state.selected_assets.remove(file_name)
    except: pass

def toggle_all_selection(all_files_list):
    if len(st.session_state.selected_assets) == len(all_files_list) and len(all_files_list) > 0:
        st.session_state.selected_assets = set()
    else:
        st.session_state.selected_assets = set(all_files_list)

st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 12px !important; }
    [data-testid="column"] { min-width: 160px !important; flex: 1 1 160px !important; width: auto !important; max-width: 100% !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 2px !important; background-color: #0a0a0a; border: 1px solid #222; border-radius: 8px; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #555; }
    div[data-testid="stImage"] { margin-bottom: 2px !important; }
    div[data-testid="stImage"] img { border-radius: 6px !important; width: 100%; display: block; }
    button { width: 100%; border-radius: 6px !important; border: none !important; white-space: nowrap !important; }
    button[kind="primary"] { background-color: #1b3a1b !important; border: 1px solid #2e5c2e !important; color: #4CAF50 !important; font-weight: 600 !important; height: 36px !important; }
    button[kind="secondary"] { background-color: #161616 !important; color: #888 !important; height: 36px !important; border: 1px solid #222 !important; }
    .stMarkdown a { color: #4da6ff !important; text-decoration: underline !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## Text Studio")
c_up, c_view = st.columns([2, 1])
with c_up:
    uploaded_file = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg', 'webp'], key=f"uploader_{st.session_state.uploader_key}", label_visibility="collapsed")
with c_view:
    layout_mode = st.radio("Layout", ["PC", "Tablet", "Mobile"], horizontal=True, label_visibility="collapsed")
    col_count = {"PC": 5, "Tablet": 3, "Mobile": 2}[layout_mode]

if uploaded_file is not None:
    save_dir = "images"
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
    st.session_state.uploader_key += 1
    st.session_state.selected_assets.add(uploaded_file.name)
    st.toast(f"✅ Saved")
    time.sleep(0.5)
    st.rerun()

st.divider()

@fragment
def render_gallery_fragment(current_col_count):
    c_head, c_ctrl = st.columns([3, 1])
    raw_map = fetch_image_refs_auto()
    all_files = [v for v in raw_map.values() if v]
    valid_files = [f for f in all_files if os.path.exists(os.path.join("images", f))]
    valid_files.sort(key=lambda x: os.path.getmtime(os.path.join("images", x)), reverse=True)
    st.session_state.selected_assets = {f for f in st.session_state.selected_assets if f in valid_files}
    with c_head: st.subheader("Visual Library")
    with c_ctrl:
        if valid_files:
            btn_label = "❌ Uncheck All" if len(st.session_state.selected_assets) == len(valid_files) else "✅ Select All"
            st.button(btn_label, key="btn_toggle_all", on_click=toggle_all_selection, args=(valid_files,))
    if not valid_files: st.info("Library is empty.")
    else:
        cols = st.columns(current_col_count)
        for idx, file_name in enumerate(valid_files):
            with cols[idx % current_col_count]:
                with st.container(border=True):
                    st.image(os.path.join("images", file_name), use_container_width=True)
                    c_sel, c_del = st.columns([3, 1], gap="small")
                    with c_sel:
                        st.button("✅ Active" if file_name in st.session_state.selected_assets else "Select", key=f"s_{file_name}", type="primary" if file_name in st.session_state.selected_assets else "secondary", on_click=toggle_selection, args=(file_name,))
                    with c_del:
                        st.button("🗑", key=f"d_{file_name}", help="Delete", on_click=delete_asset, args=(os.path.join("images", file_name), file_name))
    if st.session_state.selected_assets:
        st.markdown(f"<div style='text-align:right; color:#4CAF50;'>✅ <b>{len(st.session_state.selected_assets)}</b> Selected</div>", unsafe_allow_html=True)

render_gallery_fragment(col_count)
st.divider()

local_db = load_local_text_data_force()
available_files = sorted(list(local_db.keys())) if local_db else ["text_en.txt"]
c_lang, c_word, c_qty, c_go = st.columns([1, 1, 0.8, 1])
with c_lang: target_file = st.selectbox("Word Bank", available_files, label_visibility="collapsed")
with c_word:
    current_words_pool = local_db.get(target_file, ["LOVE"])
    selected_word_opt = st.selectbox("Pick Word", [f"🎲 Random ({len(current_words_pool)})"] + current_words_pool, label_visibility="collapsed")
with c_qty: qty = st.number_input("Qty", 1, 10, 4, label_visibility="collapsed")
with c_go: run_btn = st.button("🚀 GENERATE", type="primary", use_container_width=True)
manual_word = st.text_input("Custom Text", placeholder="Input text here...", label_visibility="collapsed")

if run_btn:
    try:
        with st.spinner("Processing..."):
            results = []
            active_pool = list(st.session_state.selected_assets)
            
            # 🔥 这里我已经改好了，指向他自己的新家
            GITHUB_RAW_BASE = "https://raw.githubusercontent.com/domozheng/ultraT/main/images/"

            for i in range(qty):
                final_word = manual_word.strip() if manual_word.strip() else (random.choice(current_words_pool) if "Random" in selected_word_opt else selected_word_opt)
                img_val = random.choice(active_pool) if active_pool else ""
                url_part = f"{GITHUB_RAW_BASE}{urllib.parse.quote(img_val)} " if img_val else ""
                results.append({"image_file": img_val, "prompt_text": f"**方案{i+1}：** {url_part}Tattoo design of the word '{final_word}', clean white background, high contrast --iw 2 **"})
            st.session_state.text_solutions = results
            st.rerun()
    except Exception as e: st.error(str(e))

if "text_solutions" in st.session_state and st.session_state.text_solutions:
    for item in st.session_state.text_solutions:
        with st.container(border=True):
            col_img, col_text = st.columns([1, 4])
            with col_img:
                if item["image_file"]: st.image(os.path.join("images", item["image_file"]), use_container_width=True)
            with col_text: st.markdown(item['prompt_text'])
    if st.button("Import to Automation Queue", type="primary", use_container_width=True):
        if "global_queue" not in st.session_state: st.session_state.global_queue = []
        st.session_state.global_queue.extend([item["prompt_text"] + "\n" for item in st.session_state.text_solutions])
        st.toast(f"✅ Imported Tasks")
        time.sleep(1)
        st.switch_page("pages/03_Automation.py")