import streamlit as st
import json
import urllib.parse
import re
import os
import sys

# ===========================
# 0. 环境路径设置
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import render_sidebar, init_data
from style_manager import apply_pro_style

# ===========================
# 1. 页面配置与初始化
# ===========================
st.set_page_config(layout="wide", page_title="Automation Central")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# 2. 队列数据同步
# ===========================
if "global_queue" not in st.session_state:
    st.session_state.global_queue = []

# 已移除：原本从 Text Studio 自动同步结果的补丁代码

current_queue_text = ""
if st.session_state.global_queue:
    current_queue_text = "\n\n".join(st.session_state.global_queue)

# ===========================
# 3. 界面布局
# ===========================
st.markdown("## Automation Central")
st.caption("Universal AI Platform Adaptor (Safe Wait Mode)")

col_info, col_clear = st.columns([4, 1])
with col_info:
    st.markdown(f"**Pending Tasks:** {len(st.session_state.global_queue)}")
with col_clear:
    if st.button("Clear Queue", use_container_width=True):
        st.session_state.global_queue = []
        # 已移除：对 text_solutions 的清空引用
        st.rerun()

user_input = st.text_area(
    "Queue Preview", 
    value=current_queue_text, 
    height=350, 
    placeholder="Waiting for tasks from Graphic Lab...",
    label_visibility="collapsed"
)

# 同步手动编辑的内容到 Session State
if user_input != current_queue_text:
    st.session_state.global_queue = [t.strip() for t in user_input.split('\n\n') if t.strip()]

st.divider()

# ===========================
# 4. 核心逻辑 (30秒安全等待脚本)
# ===========================
if st.button("Generate Safe-Wait Script (60s Delay)", type="primary", use_container_width=True):
    task_list = []
    if user_input:
        if "**方案" in user_input:
            segments = re.split(r"\*\*方案\d+：\*\*", user_input)
            for seg in segments:
                clean = seg.strip()
                clean = clean.split("(Invalid")[0].split("(Connection")[0].strip()
                if len(clean) > 2:
                    task_list.append(clean.replace("\n", " "))
        else:
            task_list = [t.strip() for t in user_input.split('\n\n') if len(t.strip()) > 5]

    if task_list:
        encoded_data = urllib.parse.quote(json.dumps(task_list))
        
        # --- JS 自动化脚本 ---
        js_code = f"""(async function() {{
            console.clear();
            console.log("%c Safe Automation Started (30s Delay) ", "background: #000; color: #0f0; font-size: 14px");
            window.kill = false;
            const tasks = JSON.parse(decodeURIComponent("{encoded_data}"));
            
            function showStatus(text, color = "#333") {{
                let el = document.getElementById('magic-status-bar');
                if (!el) {{
                    el = document.createElement('div');
                    el.id = 'magic-status-bar';
                    el.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; padding:8px 16px; border-radius:4px; font-family:sans-serif; font-size:13px; font-weight:bold; color:#fff; box-shadow:0 5px 15px rgba(0,0,0,0.3); transition: all 0.3s;";
                    document.body.appendChild(el);
                }}
                el.textContent = text;
                el.style.backgroundColor = color;
            }}

            function getInputBox() {{
                const selectors = ['#prompt-textarea', '[contenteditable="true"]', 'textarea', '[data-testid="text-input"]', '.chat-input-textarea', '.rich-textarea'];
                for (let s of selectors) {{
                    let el = document.querySelector(s);
                    if (el) return el;
                }}
                return null;
            }}

            function getSendBtn() {{
                let btn = document.querySelector('[data-testid="send-button"]');
                if (btn) return btn;
                btn = document.querySelector('button[aria-label="Send prompt"]') || 
                      document.querySelector('button[aria-label="发送"]') ||
                      document.querySelector('button[aria-label="Send"]');
                if (btn) return btn;
                let allBtns = Array.from(document.querySelectorAll('button'));
                return allBtns.find(b => {{
                    let t = (b.innerText || b.ariaLabel || "").toLowerCase();
                    let html = b.innerHTML;
                    if (t.includes('stop') || t.includes('停止')) return false;
                    return t.includes('send') || t.includes('发送') || html.includes('path') || html.includes('svg');
                }});
            }}

            function isBusy() {{
                let stopBtn = document.querySelector('[aria-label="Stop generating"]') || 
                              document.querySelector('.stop-button') || 
                              document.querySelector('button[aria-label="停止"]') ||
                              document.querySelector('button[aria-label="Stop"]');
                if (stopBtn) return true;

                let sendBtn = getSendBtn();
                if (sendBtn && sendBtn.disabled) return true;
                
                if (document.querySelector('.result-streaming')) return true;
                return false;
            }}

            showStatus("Loaded " + tasks.length + " tasks", "#444"); 
            
            for (let i = 0; i < tasks.length; i++) {{
                if (window.kill) {{ showStatus("🛑 Stopped", "#d32f2f"); break; }}
                
                let box = getInputBox();
                if (!box) {{ 
                    showStatus("Waiting for Input Box...", "#f57c00");
                    await new Promise(r => setTimeout(r, 2000));
                    box = getInputBox();
                }}
                
                if (box) {{
                    showStatus("Writing Task " + (i+1) + "/" + tasks.length, "#1976d2");
                    box.focus();
                    
                    let success = false;
                    try {{ success = document.execCommand('insertText', false, tasks[i]); }} catch(e){{}}
                    
                    if (!success) {{
                        if (box.tagName === 'DIV' || box.contentEditable === "true") {{
                            box.innerText = tasks[i]; 
                        }} else {{
                            box.value = tasks[i];
                        }}
                        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                    
                    await new Promise(r => setTimeout(r, 1000)); 

                    let sendBtn = getSendBtn();
                    if (sendBtn && !sendBtn.disabled) {{
                        sendBtn.click();
                    }} else {{
                        box.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                    }}
                }}
                
                if (i < tasks.length - 1) {{
                    showStatus("Starting...", "#616161");
                    await new Promise(r => setTimeout(r, 5000));
                    
                    let waitSec = 0;
                    while(true) {{
                        if (window.kill) break;
                        if (isBusy()) {{
                            showStatus("Generating (" + waitSec + "s)...", "#7b1fa2");
                            await new Promise(r => setTimeout(r, 1000));
                            waitSec++;
                        }} else {{
                            await new Promise(r => setTimeout(r, 2000));
                            if (!isBusy()) break; 
                        }}
                    }}

                    // 强制 60s 冷却
                    for (let s = 60; s > 0; s--) {{
                         if (window.kill) break;
                         showStatus("☕ Cooldown: " + s + "s", "#f57c00");
                         await new Promise(r => setTimeout(r, 1000));
                    }}
                }}
            }}
            if(!window.kill) showStatus("All Done!", "#2e7d32");
        }})();"""

        st.success(f"✅ Ready! ({len(task_list)} Tasks Parsed)")
        
        with st.expander("Get Safe-Wait Script", expanded=True):
            st.code(js_code, language="javascript")
        st.caption("Tip: Copy the code, F12 on AI Platform, paste into Console and Enter.")
    else:
        st.error("No valid tasks found in the queue.")
