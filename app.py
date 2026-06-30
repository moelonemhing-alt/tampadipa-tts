import streamlit as st
import asyncio
import edge_tts
import os

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
    .counter-box {
        background-color: #161925;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #2e344d;
        text-align: center;
    }
    .counter-title {
        color: #7d85a6;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: bold;
    }
    .counter-value {
        color: #00ffaa;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🎙️ Tam Pa Di Pa (တမ္ပဒီပ)")
st.caption("မြန်မာ AI အဆင့်မြင့် အသံထုတ်ယူရေး စနစ်")
st.write("---")

# ၁။ အမျိုးသားအသံ ၃ မျိုးနှင့် အမျိုးသမီးအသံ ၃ မျိုး Preset သတ်မှတ်ခြင်း
voice_presets = {
    "မနီလာ 👩 (အသံကြည်လင် - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": 0, "rate": 0},
    "မပုလဲ 👧 (ချိုသာပျိုပို - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": 10, "rate": 5},
    "မမြ 👵 (အေးဆေးတည်ငြိမ် - အမျိုးသမီး)": {"voice": "my-MM-NilarNeural", "pitch": -5, "rate": -8},
    "ကိုသီဟ 👨 (အသံခန့်ညား - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": 0, "rate": 0},
    "ကိုဇော် 👦 (သွက်လက်တက်ကြွ - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": 5, "rate": 8},
    "ကိုမင်း 👴 (တည်ငြိမ်ရင့်ကျက် - အမျိုးသား)": {"voice": "my-MM-ThihaNeural", "pitch": -8, "rate": -8}
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

# ၃။ ဖုန်းဖြင့် အလွယ်တကူနှိပ်နိုင်ရန် အပေါင်း (+) အနှုတ် (-) ပါဝင်သော Speed နှင့် Pitch စနစ်
col_adj1, col_adj2 = st.columns(2)
with col_adj1:
    user_speed = st.number_input("အမြန်နှုန်း (SPEED)", min_value=-10, max_value=10, value=-4, step=1)
with col_adj2:
    user_pitch = st.number_input("အသံ အတက်/အကျ (PITCH)", min_value=-10, max_value=10, value=0, step=1)

# Text Area ရှင်းလင်းရန် Session State ကိုင်တွယ်ခြင်း
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

# ၄။ စာသားထည့်သွင်းရန် နေရာ
st.write("### စာသားထည့်သွင်းပါ")

col_btn1, col_btn2 = st.columns([6, 1])
with col_btn2:
    if st.button("ဖျက်မည်"):
        st.session_state.text_input = ""
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

# စာလုံးရေတွက်စနစ် တွက်ချက်ခြင်းများ
words_count = len(text.split()) if text.strip() else 0
chars_count = len(text)
lines_count = len(text.splitlines()) if text.strip() else 0

# စာလုံးရေတွက်ကွက်များ ပြသခြင်း (Word Limit, Words, Characters, Lines)
col_count1, col_count2, col_count3, col_count4 = st.columns(4)
with col_count1:
    st.markdown('<div class="counter-box"><div class="counter-title">Word Limit</div><div class="counter-value">∞</div></div>', unsafe_allow_html=True)
with col_count2:
    st.markdown(f'<div class="counter-box"><div class="counter-title">Words</div><div class="counter-value">{words_count}</div></div>', unsafe_allow_html=True)
with col_count3:
    st.markdown(f'<div class="counter-box"><div class="counter-title">Characters</div><div class="counter-value">{chars_count}</div></div>', unsafe_allow_html=True)
with col_count4:
    st.markdown(f'<div class="counter-box"><div class="counter-title">Lines</div><div class="counter-value">{lines_count}</div></div>', unsafe_allow_html=True)

st.write("")

# အသံပြောင်းလဲပေးမည့် အဆင်သင့်လုပ်ဆောင်ချက် (Asynchronous Function)
async def generate_speech(text, voice_id, pitch_str, rate_str):
    communicate = edge_tts.Communicate(text, voice_id, pitch=pitch_str, rate=rate_str)
    submaker = edge_tts.SubMaker()
    audio_data = bytearray()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        # ဝါကျအဖြတ်အတောက်အလိုက် သပ်ရပ်သော ၁ ကြောင်းချင်းစီ SRT ထုတ်ရန်
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

# ၅။ အသံဖိုင်နှင့် အကွက်တိကျသော SRT ထုတ်ယူခြင်း
if st.button("အသံထုတ်ယူမည်"):
    if not text.strip():
        st.warning("ကျေးဇူးပြု၍ စာသားအရင်ရိုက်ထည့်ပါ!")
    else:
        with st.spinner("AI အသံနှင့် စာတန်းထိုး ပြုလုပ်နေပါသည်..."):
            # ပေါင်းစပ်တန်ဖိုးများကို တွက်ချက်ခြင်း
            final_pitch = vp["pitch"] + ep["pitch"] + (user_pitch * 3) # ၁ စကေးလျှင် 3Hz တိုး/လျှော့သည်
            final_rate = vp["rate"] + ep["rate"] + (user_speed * 5)   # ၁ စကေးလျှင် 5% တိုး/လျှော့သည်
            
            # edge-tts အတွက် လိုအပ်သော format ပုံစံပြောင်းခြင်း (Hz သို့ ပြောင်းလဲထားပါသည်)
            pitch_str = f"{final_pitch:+.0f}Hz"
            rate_str = f"{final_rate:+.0f}%"
            
            try:
                audio_bytes, srt_content = run_async(
                    generate_speech(text, vp["voice"], pitch_str, rate_str)
                )
                
                # အသံဖိုင်ကို Player ဖြင့် ဝဘ်ဆိုက်ပေါ်တွင် နားဆင်စေခြင်း
                st.audio(audio_bytes, format="audio/mp3")
                
                # Download ခလုတ်များအား ဘေးချင်းယှဉ် ပြသခြင်း
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button(
                        label="Download MP3 🎵",
                        data=audio_bytes,
                        file_name="tampadipa_audio.mp3",
                        mime="audio/mp3"
                    )
                with dl_col2:
                    st.download_button(
                        label="Download SRT 📝",
                        data=srt_content,
                        file_name="tampadipa_subs.srt",
                        mime="text/plain"
                    )
                st.success("အောင်မြင်စွာ ထုတ်လုပ်ပြီးပါပြီ!")
            except Exception as e:
                st.error(f"အမှားအယွင်း ဖြစ်ပွားခဲ့ပါသည်: {e}")
