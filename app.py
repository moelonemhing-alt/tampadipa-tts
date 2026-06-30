import streamlit as st
import asyncio
import edge_tts
import os
from datetime import datetime, timedelta

# Web App Page Config သတ်မှတ်ခြင်း (App နာမည်ကို "Tam Pa Di Pa" ဟု ပေးထားပါသည်)
st.set_page_config(
    page_title="Tam Pa Di Pa - AI Text-To-Speech", 
    page_icon="🎙️", 
    layout="centered"
)

# Professional UI ဖြစ်စေရန် Dark Theme CSS ကုဒ်များ ထည့်သွင်းခြင်း
st.markdown("""
<style>
    .reportview-container, .main {
        background-color: #0f111a;
        color: #ffffff;
    }
    .stTextArea textarea {
        background-color: #161925 !important;
        color: #ffffff !important;
        border: 1px solid #2e344d !important;
        border-radius: 8px !important;
        font-size: 16px;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #e01e5a, #8a2be2);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 25px;
        width: 100%;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(224, 30, 90, 0.3);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #ff3377, #9d3eff);
        color: white;
        box-shadow: 0 6px 20px rgba(224, 30, 90, 0.5);
    }
    /* Streamlit widgets border style */
    div[data-testid="stTextInput"] input {
        background-color: #161925 !important;
        color: white !important;
        border: 1px solid #2e344d !important;
    }
    .counter-box {
        background-color: #161925;
        border: 1px solid #2e344d;
        border-radius: 6px;
        text-align: center;
    }
    .counter-title {
        color: #7d85a6;
        text-transform: uppercase;
        font-weight: bold;
    }
    .counter-value {
        color: #00ffaa;
        font-weight: bold;
    }
    .history-box {
        background-color: #161925;
        border: 1px solid #2e344d;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# စနစ်မှတ်ဉာဏ် (Session States) တည်ဆောက်ခြင်း
if "history" not in st.session_state:
    st.session_state.history = []

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "srt_content" not in st.session_state:
    st.session_state.srt_content = None

if "text_input" not in st.session_state:
    st.session_state.text_input = ""

if "user_speed" not in st.session_state:
    st.session_state.user_speed = 0

if "user_pitch" not in st.session_state:
    st.session_state.user_pitch = 0

# သမိုင်းမှတ်တမ်းကို ၂၄ နာရီ (၁ ရက်) သာ သိမ်းဆည်းရန်နှင့် ကျော်လွန်က Auto ဖျက်ရန် လုပ်ဆောင်ချက်
def cleanup_old_history():
    now = datetime.now()
    st.session_state.history = [
        item for item in st.session_state.history
        if now - item["timestamp"] < timedelta(days=1)
    ]

cleanup_old_history()

# စာသားဖျက်သိမ်းသည့် လုပ်ဆောင်ချက်
def clear_text():
    st.session_state.text_input = ""
    st.session_state.audio_bytes = None
    st.session_state.srt_content = None

# အပေါင်းအနှုတ်ခလုတ်များ နှိပ်လျှင် တန်ဖိုးပြောင်းလဲပေးမည့် စနစ်များ
def speed_minus():
    if st.session_state.user_speed > -10:
        st.session_state.user_speed -= 1

def speed_plus():
    if st.session_state.user_speed < 10:
        st.session_state.user_speed += 1

def pitch_minus():
    if st.session_state.user_pitch > -10:
        st.session_state.user_pitch -= 1

def pitch_plus():
    if st.session_state.user_pitch < 10:
        st.session_state.user_pitch += 1

# App Header
st.title("🎙️ Tam Pa Di Pa (တမ္ပဒီပ)")
st.caption("မြန်မာ AI အဆင့်မြင့် အသံထုတ်ယူရေး စနစ်")
st.write("---")

# ၁။ အမျိုးသားအသံ ၃ မျိုးနှင့် အမျိုးသမီးအသံ ၃ မျိုး Preset သတ်မှတ်ခြင်း
# (အသံများ သိသာစွာ ကွဲပြားစေရန် Pitch, Rate တန်ဖိုးများကို သိသိသာသာ မြှင့်တင်ပြင်ဆင်ပေးထားပါသည်)
voice_presets = {
    "မနီလာ 👩 (အသံကြည်လင် - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": 0, "rate": 0},
    "မပုလဲ 👧 (ချိုသာပျိုပို - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": 30, "rate": 10},
    "မမြ 👵 (အေးဆေးတည်ငြိမ် - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": -25, "rate": -10},
    "ကိုသီဟ 👨 (အသံခန့်ညား - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": 0, "rate": 0},
    "ကိုဇော် 👦 (သွက်လက်တက်ကြွ - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": 25, "rate": 12},
    "ကိုမင်း 👴 (တည်ငြိမ်ရင့်ကျက် - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": -25, "rate": -12}
}

# ၂။ စကားပြော စိတ်ခံစားမှု စတိုင် ၁၁ မျိုး Preset သတ်မှတ်ခြင်း
emotion_presets = {
    "ပုံမှန်အသံ 😐": {"pitch": 0, "rate": 0},
    "စိတ်လှုပ်ရှား 🥰": {"pitch": 10, "rate": 15},
    "တည်ငြိမ် 😌": {"pitch": -5, "rate": -15},
    "သတင်း 💼": {"pitch": 0, "rate": 5},
    "ဇာတ်ကြောင်း 📖": {"pitch": -3, "rate": -10},
    "ပျော်ရွှင် 😊": {"pitch": 8, "rate": 10},
    "လေးနက် 😠": {"pitch": -8, "rate": -5},
    "တီးတိုး 🤫": {"pitch": -15, "rate": -20},
    "ဝမ်းနည်း 😢": {"pitch": -10, "rate": -25},
    "ရွှဲ့ပြော 🙄": {"pitch": 5, "rate": 0},
    "ဒေါသထွက် 🤬": {"pitch": 12, "rate": 20},
    "ကြောက်လန့် 😨": {"pitch": 15, "rate": 25}
}

# UI ဝစ်ဂျက်များ စတင်တည်ဆောက်ခြင်း
selected_voice_name = st.selectbox("အသံရွေးချယ်ပါ -", list(voice_presets.keys()))
selected_emotion_name = st.selectbox("စကားပြော စိတ်ခံစားမှု စတိုင်များ -", list(emotion_presets.keys()))

vp = voice_presets[selected_voice_name]
ep = emotion_presets[selected_emotion_name]

# ⚙️ သင့်ပုံထဲကအတိုင်း အပေါင်း (+) အနှုတ် (-) နှင့် Slider Layout ပြုလုပ်ခြင်း
st.write("⚙️ **အမြန်နှုန်း (SPEED)**")
col_s1, col_s2, col_s3, col_s4 = st.columns([1, 5, 1, 1.5])
with col_s1:
    st.button("➖", key="speed_dec_btn", on_click=speed_minus)
with col_s2:
    st.slider("SPEED_SLIDER", min_value=-10, max_value=10, key="user_speed", label_visibility="collapsed")
with col_s3:
    st.button("➕", key="speed_inc_btn", on_click=speed_plus)
with col_s4:
    st.markdown(f'<div style="background-color:#e01e5a; color:white; font-weight:bold; border-radius:8px; text-align:center; padding:10px; font-size:16px;">{st.session_state.user_speed}</div>', unsafe_allow_html=True)

st.write("🔊 **အသံ အတက်/အကျ (PITCH)**")
col_p1, col_p2, col_p3, col_p4 = st.columns([1, 5, 1, 1.5])
with col_p1:
    st.button("➖", key="pitch_dec_btn", on_click=pitch_minus)
with col_p2:
    st.slider("PITCH_SLIDER", min_value=-10, max_value=10, key="user_pitch", label_visibility="collapsed")
with col_p3:
    st.button("➕", key="pitch_inc_btn", on_click=pitch_plus)
with col_p4:
    st.markdown(f'<div style="background-color:#8a2be2; color:white; font-weight:bold; border-radius:8px; text-align:center; padding:10px; font-size:16px;">{st.session_state.user_pitch}</div>', unsafe_allow_html=True)

# 📂 ဒေါင်းလုဒ်ဆွဲမည့် ဖိုင်အမည်သတ်မှတ်ရန် နေရာ
st.write("### 📂 ဖိုင်အမည် သတ်မှတ်ရန်")
file_name_input = st.text_input(
    "ဒေါင်းလုဒ်ဆွဲမည့် ဖိုင်အမည်ကို ဤနေရာတွင် ရိုက်ထည့်ပါ -",
    value="tampadipa",
    key="file_name_widget"
)
# ဖိုင်နာမည် အဆင်ပြေစေရန် စစ်ဆေးခြင်း
safe_file_name = "".join([c for c in file_name_input if c.isalnum() or c in (" ", "_", "-")]).strip()
if not safe_file_name:
    safe_file_name = "tampadipa"

# စာသားထည့်သွင်းရန် နေရာ
st.write("### စာသားထည့်သွင်းပါ")

col_btn1, col_btn2 = st.columns([6, 1.3])
with col_btn2:
    if st.button("ဖျက်မည်", key="clear_text_btn"):
        clear_text()
        st.rerun()

text = st.text_area(
    label="မြန်မာစာသားများ ရိုက်ထည့်ပါ သို့မဟုတ် ကူးထည့်ပါ...",
    value=st.session_state.text_input,
    placeholder="ဤနေရာတွင် စာသားများကို ရိုက်ထည့်ပါ...",
    height=200,
    label_visibility="collapsed",
    key="text_area_widget"
)
st.session_state.text_input = text

# စာလုံးရေတွက်စနစ်များ (တိုက်ရိုက်အလုပ်လုပ်ပါသည်)
words_count = len(text.split()) if text.strip() else 0
chars_count = len(text)
lines_count = len(text.splitlines()) if text.strip() else 0

# ဖုန်းတွင်ပါ အမြဲတမ်း ဘေးတိုက် (Horizontal) ပေါ်နေစေရန် Flex-Box သုံး၍ ရေးသားခြင်း
st.markdown(f"""
<div style="display: flex; flex-direction: row; justify-content: space-between; gap: 5px; width: 100%; margin-top: 5px; margin-bottom: 10px;">
    <div class="counter-box" style="flex: 1; padding: 5px 2px;">
        <div class="counter-title" style="font-size: 8px;">Word Limit</div>
        <div class="counter-value" style="font-size: 13px;">∞</div>
    </div>
    <div class="counter-box" style="flex: 1; padding: 5px 2px;">
        <div class="counter-title" style="font-size: 8px;">Words</div>
        <div class="counter-value" style="font-size: 13px;">{words_count}</div>
    </div>
    <div class="counter-box" style="flex: 1; padding: 5px 2px;">
        <div class="counter-title" style="font-size: 8px;">Characters</div>
        <div class="counter-value" style="font-size: 13px;">{chars_count}</div>
    </div>
    <div class="counter-box" style="flex: 1; padding: 5px 2px;">
        <div class="counter-title" style="font-size: 8px;">Lines</div>
        <div class="counter-value" style="font-size: 13px;">{lines_count}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# အသံပြောင်းလဲပေးမည့် အဆင်သင့်လုပ်ဆောင်ချက်
async def generate_speech(text, voice_id, pitch_str, rate_str):
    communicate = edge_tts.Communicate(text, voice_id, pitch=pitch_str, rate=rate_str)
    submaker = edge_tts.SubMaker()
    audio_data = bytearray()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            submaker.feed(chunk)
            
    return bytes(audio_data), submaker.get_srt()

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# အသံဖိုင်နှင့် အကွက်တိကျသော SRT ထုတ်ယူခြင်း
if st.button("အသံထုတ်ယူမည်", key="generate_audio_btn"):
    if not text.strip():
        st.warning("ကျေးဇူးပြု၍ စာသားအရင်ရိုက်ထည့်ပါ!")
    else:
        with st.spinner("AI အသံနှင့် စာတန်းထိုး ပြုလုပ်နေပါသည်..."):
            # အသံစတိုင် တွက်ချက်မှုစနစ် (Hz သို့ ပြောင်းလဲထားပါသည်)
            final_pitch = vp["pitch"] + ep["pitch"] + (st.session_state.user_pitch * 5)
            final_rate = vp["rate"] + ep["rate"] + (st.session_state.user_speed * 5)
            
            pitch_str = f"{final_pitch:+.0f}Hz"
            rate_str = f"{final_rate:+.0f}%"
            
            try:
                audio_bytes, srt_content = run_async(
                    generate_speech(text, vp["voice"], pitch_str, rate_str)
                )
                
                # ဒေါင်းလုဒ်လုပ်လျှင် မပျောက်သွားစေရန် မှတ်ဉာဏ်ထဲ သိမ်းဆည်းခြင်း
                st.session_state.audio_bytes = audio_bytes
                st.session_state.srt_content = srt_content
                
                # 📜 သမိုင်းမှတ်တမ်း (History) ထဲတွင် ထည့်သွင်းခြင်း
                st.session_state.history.insert(0, {
                    "text_preview": text[:50] + "..." if len(text) > 50 else text,
                    "full_text": text,
                    "timestamp": datetime.now(),
                    "voice": selected_voice_name,
                    "audio_bytes": audio_bytes,
                    "srt_content": srt_content
                })
                
                st.rerun()  # သန့်ရှင်းစွာ ပြန်လည်ပြသရန်
            except Exception as e:
                st.error(f"အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်: {e}")

# ထွက်ပေါ်လာသော အသံဖိုင်နှင့် ဒေါင်းလုဒ်ခလုတ်များ ပြသခြင်း (အမြဲတည်ရှိနေပါသည်)
if st.session_state.audio_bytes and st.session_state.srt_content:
    st.write("---")
    st.write("### 🎵 ထွက်ပေါ်လာသောအသံဖိုင်")
    st.audio(st.session_state.audio_bytes, format="audio/mp3")
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="Download MP3 🎵",
            data=st.session_state.audio_bytes,
            file_name=f"{safe_file_name}.mp3",
            mime="audio/mp3",
            key="mp3_download_btn"
        )
    with dl_col2:
        st.download_button(
            label="Download SRT 📝",
            data=st.session_state.srt_content,
            file_name=f"{safe_file_name}.srt",
            mime="text/plain",
            key="srt_download_btn"
        )
    st.success("အောင်မြင်စွာ ထုတ်လုပ်ပြီးပါပြီ!")

# ၅။ သမိုင်းမှတ်တမ်းပြသသည့် ကဏ္ဍ (History Section)
if st.session_state.history:
    st.write("---")
    with st.expander("📜 History (လွန်ခဲ့သော ၂၄ နာရီအတွင်း ထုတ်လုပ်မှုများ)"):
        for idx, item in enumerate(st.session_state.history):
            st.markdown(f"""
            <div class="history-box">
                <div style="font-size: 13px; font-weight: bold; color: #00ffaa;">{item['voice']}</div>
                <div style="font-size: 11px; color: #7d85a6; margin-bottom: 5px;">{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div style="font-size: 14px; background-color: #0f111a; padding: 8px; border-radius: 4px; margin-bottom: 8px; border: 1px solid #2e344d;">{item['text_preview']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # မှတ်တမ်းတစ်ခုချင်းစီအလိုက် လုပ်ဆောင်ချက်ခလုတ်များ
            hist_col1, hist_col2, hist_col3 = st.columns([1.2, 1, 1])
            with hist_col1:
                # စာသားပြန်လည်ရယူရန်ခလုတ်
                if st.button("စာသားပြန်ယူမည်", key=f"reload_hist_btn_{idx}"):
                    st.session_state.text_input = item["full_text"]
                    st.session_state.audio_bytes = item["audio_bytes"]
                    st.session_state.srt_content = item["srt_content"]
                    st.rerun()
            with hist_col2:
                st.download_button(
                    label="MP3 🎵",
                    data=item["audio_bytes"],
                    file_name=f"{safe_file_name}_history_{idx}.mp3",
                    mime="audio/mp3",
                    key=f"dl_mp3_hist_btn_{idx}"
                )
            with hist_col3:
                st.download_button(
                    label="SRT 📝",
                    data=item["srt_content"],
                    file_name=f"{safe_file_name}_history_{idx}.srt",
                    mime="text/plain",
                    key=f"dl_srt_hist_btn_{idx}"
                )
