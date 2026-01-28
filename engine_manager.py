import streamlit as st
import os

# ==========================================
# 1. 本地仓库映射 (已移除 Text Studio 相关路径)
# ==========================================
WAREHOUSE = {
    # --- Graphic Core ---
    "Subject":       "data/graphic/subjects.txt",
    "Action":        "data/graphic/actions.txt",
    "Lighting":        "data/graphic/lighting.txt",
    "LensLanguage":     "data/graphic/lens_language.txt",
    
    # --- Style Matrix ---
    "Reference":   "data/graphic/styles_reference.txt",
    "Color":         "data/graphic/styles_color.txt",
    "Scene":       "data/graphic/styles_scene.txt",
    "Composition":   "data/graphic/styles_composition.txt",
    "Elements":        "data/graphic/styles_elements.txt",
    "LookLike":        "data/graphic/styles_lookLike.txt",
    
    # --- Atmosphere ---
    "Mood":          "data/common/moods.txt",
    "Usage":         "data/common/usage.txt"
}

# ==========================================
# 2. 数据读取与初始化
# ==========================================
def read_local_file(filepath):
    """直接读取本地 txt 文件"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except:
            return []
    return []

def init_data():
    if "db_all" not in st.session_state:
        st.session_state.db_all = {}
        
    for key, path in WAREHOUSE.items():
        if key not in st.session_state.db_all or not st.session_state.db_all[key]:
            data = read_local_file(path)
            st.session_state.db_all[key] = data if data else []

# ==========================================
# 3. 数据保存
# ==========================================
def save_data(file_key, new_list):
    target_key = None
    for k, v in WAREHOUSE.items():
        if v == file_key:
            target_key = k
            break
            
    if target_key:
        st.session_state.db_all[target_key] = new_list
    
    os.makedirs(os.path.dirname(file_key), exist_ok=True)
    try:
        with open(file_key, "w", encoding="utf-8") as f:
            f.write("\n".join(new_list))
    except Exception as e:
        st.error(f"Save failed: {e}")

# ==========================================
# 4. 侧边栏 (已清理 Text 统计)
# ==========================================
def render_sidebar():
    with st.sidebar:
        logo_path = "images/logo/logo.svg"
        
        if os.path.exists(logo_path):
            st.logo(logo_path, icon_image=logo_path)
        
        if "db_all" in st.session_state:
            db = st.session_state.db_all
            
            # --- Part 1: Graphic ---
            st.markdown("### Graphic Core")
            st.markdown(f"""
            **Subject:** {len(db.get('Subject', []))}  
            **Action:** {len(db.get('Action', []))}
            **Lighting:** {len(db.get('Lighting', []))}
            **LensLanguage:** {len(db.get('LensLanguage', []))}
            """)
            
            st.markdown("---")
            
            # --- Part 2: Style ---
            st.markdown("### Style Matrix")
            st.markdown(f"""
            **Reference:** {len(db.get('Reference', []))}  
            **Scene:** {len(db.get('Scene', []))}  
            **Color:** {len(db.get('Color', []))}  
            **Composition:** {len(db.get('Composition', []))}  
            **Elements:** {len(db.get('Elements', []))}
            **Usage:** {len(db.get('Usage', []))}
            """)
            
            st.markdown("---")
            
            # --- Part 3: Atmosphere ---
            st.markdown("### Atmosphere")
            st.markdown(f"**Mood:** {len(db.get('Mood', []))}")

# ==========================================
# 5. 图库扫描
# ==========================================
def fetch_image_refs_auto():
    refs = {}
    local_img_dir = "images"
    
    if os.path.exists(local_img_dir):
        try:
            files = os.listdir(local_img_dir)
            valid_exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
            
            for file in files:
                if file.lower().endswith(valid_exts):
                    key_name = os.path.splitext(file)[0]
                    refs[f"📂 {key_name}"] = file 
        except Exception:
            pass
            
    if not refs:
        refs["(No Local Images)"] = ""
        
    return refs
