import streamlit as st
import requests
import os
import tempfile
import time
import hashlib
import random
import math

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip
)

from moviepy.video.fx.all import fadein, fadeout

from gtts import gTTS

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CineStory AI Director",
    page_icon="🎬",
    layout="wide"
)

# =========================================================
# CSS - NETFLIX UI
# =========================================================

st.markdown("""
<style>

.stApp{
    background:linear-gradient(to bottom,#000000,#0f172a);
    color:white;
}

.main-title{
    text-align:center;
    font-size:72px;
    font-weight:900;
    color:#ffffff;
    margin-top:10px;
    text-shadow:0 0 30px rgba(239,68,68,0.7);
}

.sub-title{
    text-align:center;
    font-size:22px;
    color:#cbd5e1;
    margin-bottom:30px;
}

.loading-box{
    background:rgba(255,255,255,0.05);
    border-radius:25px;
    padding:30px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.08);
    box-shadow:0 0 35px rgba(239,68,68,0.25);
}

.loading-img{
    animation:float 3s ease-in-out infinite;
}

@keyframes float{
    0%{transform:translateY(0px);}
    50%{transform:translateY(-12px);}
    100%{transform:translateY(0px);}
}

.stButton>button{
    height:70px;
    border-radius:20px;
    font-size:22px;
    font-weight:bold;
    background:linear-gradient(to right,#dc2626,#7c3aed);
    color:white;
    border:none;
}

.stButton>button:hover{
    transform:scale(1.02);
    transition:0.3s;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🎬 CineStory AI Director</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">حوّل قصتك إلى فيلم سينمائي احترافي بالذكاء الاصطناعي</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🎥 إعدادات الفيلم")

    total_duration = st.slider(
        "مدة الفيديو بالدقائق",
        1,
        20,
        5
    )

    num_scenes = st.slider(
        "عدد المشاهد",
        4,
        40,
        12
    )

    resolution = st.selectbox(
        "الجودة",
        [
            "1080p",
            "4K"
        ]
    )

    motion_style = st.selectbox(
        "AI Camera",
        [
            "Cinematic",
            "Action",
            "Drone",
            "Documentary"
        ]
    )

    add_music = st.checkbox(
        "🎵 موسيقى سينمائية",
        value=True
    )

    add_subtitles = st.checkbox(
        "📝 ترجمة تلقائية",
        value=True
    )

    gpu_render = st.checkbox(
        "⚡ GPU Rendering",
        value=True
    )

# =========================================================
# STORY
# =========================================================

story = st.text_area(
    "✍️ اكتب قصتك",
    height=350,
    placeholder="اكتب قصة سينمائية طويلة..."
)

# =========================================================
# CACHE
# =========================================================

if "image_cache" not in st.session_state:
    st.session_state.image_cache = {}

# =========================================================
# HASH
# =========================================================

def get_hash(text):

    return hashlib.md5(
        text.encode()
    ).hexdigest()

# =========================================================
# AI STORY DIRECTOR
# =========================================================

def split_story(story_text, num):

    paragraphs = []

    chunk = max(
        250,
        len(story_text) // num
    )

    for i in range(0, len(story_text), chunk):

        paragraphs.append(
            story_text[i:i+chunk]
        )

    return paragraphs[:num]

# =========================================================
# AI PROMPT ENHANCER
# =========================================================

def enhance_prompt(scene):

    return f"""
ultra realistic cinematic movie frame,
Netflix movie scene,
Hollywood action scene,
dramatic lighting,
epic atmosphere,
35mm film,
ARRI Alexa,
cinematic shadows,
depth of field,
masterpiece,
4k,
highly detailed,
realistic skin,
dynamic action,
movie composition,
{scene}
"""

# =========================================================
# IMAGE GENERATOR
# =========================================================

def generate_image(scene, index):

    cache_key = get_hash(scene)

    if cache_key in st.session_state.image_cache:
        return st.session_state.image_cache[cache_key]

    prompt = enhance_prompt(scene)

    encoded = requests.utils.quote(prompt)

    seed = random.randint(
        1,
        99999999
    )

    url = (
        f"https://image.pollinations.ai/prompt/"
        f"{encoded}"
        f"?width=1920"
        f"&height=1080"
        f"&seed={seed}"
        f"&enhance=true"
        f"&nologo=true"
    )

    try:

        response = requests.get(
            url,
            timeout=90
        )

        if response.status_code == 200:

            with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                delete=False
            ) as f:

                f.write(response.content)

                st.session_state.image_cache[cache_key] = f.name

                return f.name

    except Exception as e:

        st.error(f"خطأ توليد الصورة: {e}")

    return None

# =========================================================
# CAMERA MOVEMENT AI
# =========================================================

def create_clip(image_path, duration, motion):

    clip = ImageClip(image_path)

    clip = clip.set_duration(duration)

    if motion == "Cinematic":

        clip = clip.resize(
            lambda t: 1 + 0.08 * (t / duration)
        )

    elif motion == "Action":

        clip = clip.resize(
            lambda t: 1 + 0.18 * (t / duration)
        )

        clip = clip.rotate(
            lambda t: math.sin(t * 2) * 1.2
        )

    elif motion == "Drone":

        clip = clip.resize(
            lambda t: 1 + 0.04 * math.sin(t)
        )

        clip = clip.set_position(
            lambda t: (
                -30 * (t / duration),
                -10
            )
        )

    else:

        clip = clip.resize(
            lambda t: 1 + 0.05 * math.sin(t)
        )

    clip = fadein(clip, 1)
    clip = fadeout(clip, 1)

    return clip

# =========================================================
# ARABIC VOICE
# =========================================================

def generate_voice(text):

    try:

        tts = gTTS(
            text=text,
            lang="ar",
            slow=False,
            tld="com"
        )

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as f:

            tts.save(f.name)

            return f.name

    except Exception as e:

        st.error(f"خطأ الصوت: {e}")

        return None

# =========================================================
# VIDEO EXPORT
# =========================================================

def export_video(images, audio_path):

    audio = AudioFileClip(audio_path)

    scene_duration = max(
        5,
        audio.duration / len(images)
    )

    clips = []

    for img in images:

        clip = create_clip(
            img,
            scene_duration,
            motion_style
        )

        clips.append(clip)

    final = concatenate_videoclips(
        clips,
        method="compose"
    )

    final = final.set_audio(audio)

    output = "cinestory_ai_director.mp4"

    codec = "libx264"

    if gpu_render:
        codec = "h264_nvenc"

    bitrate = "8000k"

    if resolution == "4K":
        bitrate = "20000k"

    final.write_videofile(
        output,
        fps=24,
        codec=codec,
        audio_codec="aac",
        bitrate=bitrate,
        threads=8
    )

    final.close()
    audio.close()

    for c in clips:
        c.close()

    return output

# =========================================================
# MAIN BUTTON
# =========================================================

if st.button(
    "🚀 إنشاء الفيلم السينمائي",
    use_container_width=True
):

    if len(story.strip()) < 100:

        st.error("اكتب قصة أطول")

    else:

        scenes = split_story(
            story,
            num_scenes
        )

        st.success(
            f"✅ تم إنشاء {len(scenes)} مشهد"
        )

        progress = st.progress(0)

        image_paths = []

        loading = st.empty()

        for i, scene in enumerate(scenes):

            loading.markdown(
                f"""
<div class="loading-box">

<img
class="loading-img"
src="https://cdn-icons-png.flaticon.com/512/3416/3416079.png"
width="120"
/>

<h2>
🎬 جاري إنشاء المشهد {i+1}/{len(scenes)}
</h2>

<p style="color:#c4b5fd;font-size:18px;">
{scene[:180]}
</p>

</div>
                """,
                unsafe_allow_html=True
            )

            img = generate_image(
                scene,
                i
            )

            if img:
                image_paths.append(img)

            progress.progress(
                (i + 1) / len(scenes)
            )

        loading.empty()

        # =====================================================
        # VOICE
        # =====================================================

        audio_path = generate_voice(story)

        # =====================================================
        # VIDEO
        # =====================================================

        if image_paths and audio_path:

            with st.spinner("🎬 GPU Rendering الفيديو..."):

                video = export_video(
                    image_paths,
                    audio_path
                )

            st.success("✅ تم إنشاء الفيلم بنجاح")

            st.video(video)

            with open(video, "rb") as f:

                st.download_button(
                    "⬇️ تحميل الفيلم",
                    f,
                    file_name="cinestory_ai.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        # =====================================================
        # CLEANUP
        # =====================================================

        for file in image_paths + [audio_path]:

            try:

                if file and os.path.exists(file):
                    os.unlink(file)

            except:
                pass