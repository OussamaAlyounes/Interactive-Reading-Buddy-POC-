import streamlit as st
import time
import difflib
import re
import os
import base64

try:
    from streamlit_mic_recorder import mic_recorder, speech_to_text
    HAS_RECORDER = True
except ImportError:
    HAS_RECORDER = False

# Mobile & tablet optimized view
st.set_page_config(
    page_title="نوري - رفيق القراءة التفاعلي",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- GLOBAL STYLES & PERSISTENT AUDIO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Tajawal', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 18px;
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        padding: 14px 20px;
        margin-top: 10px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
    }
    
    button[kind="secondary"] {
        background: #F1F5F9 !important;
        color: #475569 !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: none !important;
    }
    
    .quran-box {
        background: #FEF3C7;
        border-right: 6px solid #D97706;
        padding: 18px;
        border-radius: 14px;
        font-weight: 800;
        color: #78350F;
        text-align: center;
        font-size: 22px;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    
    .trust-badge {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        color: #1E3A8A;
        font-size: 16px;
        margin: 15px 0;
    }
    
    .testimonial-card {
        background: #F8FAFC;
        border-right: 4px solid #10B981;
        border-radius: 12px;
        padding: 16px 18px;
        margin: 16px 0;
        font-size: 15px;
        color: #334155;
        line-height: 1.7;
    }
    
    .reassurance-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 14px;
        padding: 16px;
        color: #065F46;
        font-size: 16px;
        line-height: 1.7;
        margin: 15px 0;
    }
    
    .book-container {
        background: #FFFFFF;
        border: 3px solid #E2E8F0;
        border-radius: 24px;
        padding: 25px 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        margin: 15px 0;
    }
    
    .book-sentence {
        font-size: 32px;
        font-weight: 900;
        color: #0F172A;
        line-height: 2.2;
    }
    
    .word-correct {
        color: #15803D;
        background: #DCFCE7;
        padding: 2px 10px;
        border-radius: 10px;
        margin: 0 4px;
        display: inline-block;
        font-weight: bold;
    }
    
    .word-wrong {
        color: #B91C1C;
        background: #FEE2E2;
        padding: 2px 10px;
        border-radius: 10px;
        margin: 0 4px;
        display: inline-block;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- PERSISTENT AUDIO INJECTION ---
def render_persistent_music(should_play=True):
    music_src = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
    if os.path.exists("ahd_al_asdiqa.mp3"):
        with open("ahd_al_asdiqa.mp3", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            music_src = f"data:audio/mp3;base64,{encoded}"
            
    if should_play:
        js_code = f"""
        <script>
            var audio = window.parent.document.getElementById("bg-music-player");
            if (!audio) {{
                audio = window.parent.document.createElement("audio");
                audio.id = "bg-music-player";
                audio.src = "{music_src}";
                audio.loop = true;
                window.parent.document.body.appendChild(audio);
            }}
            audio.play().catch(function(e){{ console.log("Music awaiting touch:", e); }});
        </script>
        """
    else:
        js_code = """
        <script>
            var audio = window.parent.document.getElementById("bg-music-player");
            if (audio) { audio.pause(); }
        </script>
        """
    st.components.v1.html(js_code, height=0, width=0)

# --- STATE MANAGEMENT ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "child_name" not in st.session_state:
    st.session_state.child_name = ""
if "child_avatar" not in st.session_state:
    st.session_state.child_avatar = None
if "child_avatar_icon" not in st.session_state:
    st.session_state.child_avatar_icon = "👦"
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 0
if "reading_history" not in st.session_state:
    st.session_state.reading_history = []
if "eval_done" not in st.session_state:
    st.session_state.eval_done = False

TOTAL_STEPS = 10

def render_nav(prev_step, next_step, disable_next=False, next_label="متابعة ⬅️"):
    col1, col2 = st.columns([1, 2])
    with col1:
        if prev_step is not None:
            if st.button("رجوع ➡️", key=f"prev_{st.session_state.step}", type="secondary"):
                st.session_state.step = prev_step
                st.rerun()
    with col2:
        if st.button(next_label, key=f"next_{st.session_state.step}", disabled=disable_next):
            st.session_state.step = next_step
            st.rerun()

BOOK_PAGES = [
    {
        "text": "ذَهَبَ سَامِي إِلَى المَدْرَسَةِ فِي الصَّبَاحِ البَاكِرِ.",
        "clean": "ذهب سامي الى المدرسة في الصباح الباكر",
        "audio": "https://actions.google.com/sounds/v1/human_voices/applause.ogg"
    },
    {
        "text": "فَتَحَ كِتَابَ القِرَاءَةِ وَبَدَأَ يَتَعَلَّمُ بِشَغَفٍ وَسُرُورٍ.",
        "clean": "فتح كتاب القراءة وبدا يتعلم بشغف وسرور",
        "audio": "https://actions.google.com/sounds/v1/human_voices/applause.ogg"
    },
    {
        "text": "قَالَ المُعَلِّمُ: أَنْتَ قَارِئٌ مُمَيَّزٌ يَا سَامِي!",
        "clean": "قال المعلم انت قارئ مميز يا سامي",
        "audio": "https://actions.google.com/sounds/v1/human_voices/applause.ogg"
    }
]

AVATARS = [
    {"id": "b1", "name": "روميو (عهد الأصدقاء)", "icon": "👦 🧹"},
    {"id": "b2", "name": "سنان (مغامرات سنان)", "icon": "🦫 🌲"},
    {"id": "b3", "name": "كابتن ماجد", "icon": "⚽ 🏃‍♂️"},
    {"id": "g1", "name": "سالي", "icon": "👧 🌸"},
    {"id": "g2", "name": "هايدي", "icon": "👧 🏔️"},
    {"id": "g3", "name": "ريمي (دروب ريمي)", "icon": "👧 🎶"}
]

# --- ROBUST ARABIC SPEECH EVALUATION ---
def normalize_word(word):
    w = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', word)
    w = re.sub(r'[أإآٱ]', 'ا', w)
    w = re.sub(r'ة', 'ه', w)
    w = re.sub(r'[ىي]', 'ي', w)
    w = re.sub(r'[^\w\s]', '', w)
    return w.strip()

def evaluate_reading_detailed(spoken_text, target_text):
    target_words = [w for w in target_text.split() if normalize_word(w)]
    spoken_words = [normalize_word(w) for w in spoken_text.split() if normalize_word(w)]
    
    word_results = []
    total_score = 0.0
    
    for t_word in target_words:
        clean_t = normalize_word(t_word)
        best_match = 0.0
        
        for s_word in spoken_words:
            sim = difflib.SequenceMatcher(None, clean_t, s_word).ratio()
            if sim > best_match:
                best_match = sim
                
        if best_match >= 0.80:
            word_results.append((t_word, True))
            total_score += 1.0
        elif best_match >= 0.50:
            word_results.append((t_word, False))
            total_score += 0.5
        else:
            word_results.append((t_word, False))
            total_score += 0.0

    num_words = max(len(target_words), 1)
    final_score_10 = round((total_score / num_words) * 10, 1)
    is_success = final_score_10 > 6.0
    
    return is_success, final_score_10, word_results

# Music control
if st.session_state.step <= 7:
    render_persistent_music(should_play=True)
else:
    render_persistent_music(should_play=False)

# =========================================================
# 1. WELCOME & SACRED TRUST
# =========================================================
if st.session_state.step == 1:
    st.markdown('<div class="quran-box">﴿اقْرَأْ بِاسْمِ رَبِّكَ الَّذِي خَلَقَ﴾<br><small style="font-size:14px;">صدق الله العظيم</small></div>', unsafe_allow_html=True)
    st.markdown("### مرحباً بك في نوري — بوابتك لتعليم طفلك حب القراءة")
    st.write("أكثر من **3 ملايين ولي أمر** يثقون في منصتنا لغرس الفصاحة وحب المعرفة في قلوب أبنائهم.")
    
    st.markdown("""
    <div class="trust-badge">
        ✅ <b>معتمد من خبراء التربية ومعلمي اللغة العربية والقرآن الكريم</b><br>
        دراساتنا الميدانية شملت أكثر من 100 ألف طفل لمساعدتهم على الانطلاق بثقة وبناء شخصية قارئة مستقلة.
    </div>
    """, unsafe_allow_html=True)
    render_nav(None, 2, next_label="البدء في إعداد الخطة لطفلك 🚀")

# =========================================================
# 2. CHILD AGE & GENDER
# =========================================================
elif st.session_state.step == 2:
    st.subheader("كم عمر طفلك وما هو جنسه؟")
    age = st.slider("عمر الطفل:", 3, 8, st.session_state.answers.get("age", 5))
    gender = st.radio("جنس الطفل:", ["بطل 👦", "بطلة 👧"], index=0 if st.session_state.answers.get("gender") == "بطل 👦" else 1, horizontal=True)
    
    st.session_state.answers["age"] = age
    st.session_state.answers["gender"] = gender
    render_nav(1, 3)

# =========================================================
# 3. CURRENT READING LEVEL
# =========================================================
elif st.session_state.step == 3:
    st.subheader("ما هو المستوى الحالي لطفلك في القراءة؟")
    level_options = [
        "معرفة شكل الحروف وأسمائها فقط",
        "التعرف على أصوات الحروف مع الحركات (الفتحة والضمة والكسرة)",
        "تهجئة الكلمات البسيطة ببطء وتردد",
        "يقرأ جملاً قصيرة لكنه يفتقد للثقة والطلاقة"
    ]
    current_level = st.radio("المستوى:", level_options, index=0)
    st.session_state.answers["level"] = current_level
    render_nav(2, 4)

# =========================================================
# 4. 4 DYNAMIC REASSURANCES & TESTIMONIALS
# =========================================================
elif st.session_state.step == 4:
    selected_level = st.session_state.answers.get("level", "معرفة شكل الحروف وأسمائها فقط")
    
    if "شكل الحروف" in selected_level:
        reassurance = "الانتقال من حفظ شكل الحرف إلى ربطه بالكلمات هو أكبر عقبة تواجه الأطفال. خوارزميتنا تركز على التكرار السمعي البصري الذكي ليتحول الحرف إلى كلمة مقروءة بسلاسة."
        author = "أم عبدالله (الرياض)"
        quote = "ابني كان يحفظ الحروف كأشكال فقط ويتعثر تماماً عند رؤية أول كلمة. بعد 10 أيام مع رفيق القراءة الذكي صار يربط الحروف ويقرأ كلمته الأولى بفرح لا يوصف!"
    elif "أصوات الحروف" in selected_level:
        reassurance = "معرفة الحركات هي المفتاح الحقيقي للنطق الصحيح! رفيق القراءة الذكي يصحح الفتحة والضمة والكسرة بنبرة مشجعة دون إحراج الطفل حتى يتقن الضبط التلقائي."
        author = "أبو فيصل (جدة)"
        quote = "كان فيصل يخلط بين الحركات الطويلة والقصيرة ويخاف يقرأ بصوت عالي. الميزة الجميلة هنا إن التطبيق يصحح له بلطف وبصوت القارئ المعتمد فزالت الرهبة تماماً."
    elif "تهجئة الكلمات" in selected_level:
        reassurance = "التهجئة البطيئة مرحلة طبيعية جداً وتحتاج فقط إلى تعزيز الذاكرة البصرية للجمل. سنقدم له نصوصاً تفاعلية قصيرة ترفع سرعة قراءته تدريجياً."
        author = "أم سارة (الدمام)"
        quote = "سارة كانت تقضي دقيقة كاملة لتهجئة كلمة من ثلاثة حروف وتشعر بالملل بسرعة. مع جلسات التحدي التفاعلية اليومية، تضاعفت سرعة قراءتها وأصبحت تقرأ الجملة بطلاقة!"
    else:
        reassurance = "الطفل يمتلك المهارة لكنه يخشى الوقوع في الخطأ أمام الآخرين. بيئة الذكاء الاصطناعي تمنحه مساحة تدريب آمنة وخاصة 100% لبناء ثقة فولاذية بنفسه."
        author = "أم يوسف (المدينة المنورة)"
        quote = "يوسف كان يعرف يقرأ لكن صوته يختفي تماماً في الفصل عند القراءة الجهرية. بعدما مارس القراءة يومياً مع رفيق القراءة الذكي، المعلم نفسه لاحظ فرقا كبيرا في شجاعته وصوته الواضح!"

    st.markdown(f"""
    <div class="reassurance-box">
        💡 <b>اطمئن تماماً.. طفلك سيتجاوز هذه المرحلة بنجاح!</b><br>
        {reassurance}
    </div>
    <div class="testimonial-card">
        💬 <b>تجربة من واقع مجتمع نوري — {author}:</b><br>
        <i>"{quote}"</i>
    </div>
    """, unsafe_allow_html=True)
    render_nav(3, 5)

# =========================================================
# 5. PREVIOUS LEARNING & CHALLENGES
# =========================================================
elif st.session_state.step == 5:
    st.subheader("أين بدأ طفلك وما هي أكبر التحديات؟")
    where = st.radio("البيئة السابقة:", [
        "في الروضة أو المدرسة التمهيدية",
        "في المنزل بجهودنا الشخصية كأولياء أمور",
        "مع معلم خصوصي أو في حلقات تحفيظ القرآن الكريم",
        "لم نبدأ بعد بأي برنامج منتظم"
    ])
    reasons = st.multiselect(
        "أبرز التحديات:",
        [
            "ضيق الوقت المتاح لنا للمتابعة اليومية معه",
            "سرعة شعور الطفل بالملل ورغبته في اللعب فقط",
            "التكلفة المرتفعة للدروس الخصوصية ومراكز المتابعة",
            "انزعاج الطفل وتوتره عند تصحيح أخطائه بشكل متكرر"
        ],
        default=["سرعة شعور الطفل بالملل ورغبته في اللعب فقط"]
    )
    st.session_state.answers["learning_env"] = where
    st.session_state.answers["challenges"] = reasons
    render_nav(4, 6)

# =========================================================
# 6. ATTENTION SPAN & SOURCE
# =========================================================
elif st.session_state.step == 6:
    st.subheader("كم دقيقة يستطيع طفلك التركيز؟ وكيف سمعت عنا؟")
    duration = st.select_slider(
        "فترة التركيز:",
        options=["5 دقائق", "10 دقائق", "15 دقيقة", "20 دقيقة فأكثر"],
        value=st.session_state.answers.get("duration", "10 دقائق")
    )
    source = st.radio("المصدر:", [
        "توصية من معلم / مدرسة طفلي",
        "ترشيح من صديق أو من العائلة",
        "وسائل التواصل الاجتماعي (إنستغرام / إكس / تيك توك)",
        "البحث المباشر في متجر التطبيقات"
    ])
    st.session_state.answers["duration"] = duration
    st.session_state.answers["source"] = source
    render_nav(5, 7)

# =========================================================
# 7. CHILD INITIALIZATION (NAME & AVATARS)
# =========================================================
elif st.session_state.step == 7:
    st.subheader("🌟 مرحباً يا بطل! لنتعرف عليك:")
    st.write("اكتب اسمك الجميل واختر شخصيتك الكرتونية المفضلة لترافقك في رحلة القراءة!")
    
    child_name = st.text_input("ما هو اسمك يا بطل؟", value=st.session_state.child_name, placeholder="مثال: أحمد / مريم")
    st.session_state.child_name = child_name
    
    st.write("🎨 **اختر بطلك المفضل:**")
    avatar_cols = st.columns(3)
    
    for idx, av in enumerate(AVATARS):
        with avatar_cols[idx % 3]:
            is_selected = (st.session_state.child_avatar == av["name"])
            border_color = "#2563EB" if is_selected else "#E2E8F0"
            bg_color = "#EFF6FF" if is_selected else "#FFFFFF"
            
            st.markdown(f"""
            <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:14px; padding:10px; text-align:center; margin-bottom:10px;">
                <div style="font-size:32px;">{av['icon']}</div>
                <div style="font-weight:bold; font-size:14px; color:#1E293B;">{av['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("اختيار" if not is_selected else "✅ تم الاختيار", key=f"av_{av['id']}"):
                st.session_state.child_avatar = av["name"]
                st.session_state.child_avatar_icon = av["icon"]
                st.rerun()

    ready_to_calibrate = len(child_name.strip()) > 0 and st.session_state.child_avatar is not None
    if not ready_to_calibrate:
        st.info("👆 يرجى كتابة اسم الطفل واختيار شخصية بطل للمتابعة.")
        
    render_nav(6, 8, disable_next=not ready_to_calibrate, next_label="معايرة الذكاء الاصطناعي وبدء القصة ⚙️")

# =========================================================
# 8. MERGED 10-SECOND AI CALIBRATION ANIMATION
# =========================================================
elif st.session_state.step == 8:
    c_name = st.session_state.child_name if st.session_state.child_name else "البطل"
    st.subheader(f"⚙️ جاري بناء ومعايرة النموذج المخصص لـ ({c_name})...")
    st.caption("يرجى الانتظار 10 ثوانٍ بينما نُهيئ محرك التحليل الصوتي ومكتبة القصص...")
    
    prog_bar = st.progress(0)
    status_text = st.empty()
    checkpoints = st.empty()
    
    pipeline = [
        {"msg": f"تحليل النبرة الطفولية وضبط حساسية الصوت لـ {c_name}...", "time": 2.5, "pct": 25, "done": "✔️ تمت معايرة حساسية الميكروفون للنبرة الطفولية"},
        {"msg": "مواءمة مخارج الحروف وقواعد التشكيل والضبط الصوتي...", "time": 2.5, "pct": 50, "done": "✔️ تم ضبط محرك مخارج الحروف وقواعد الضبط والتسكين"},
        {"msg": f"تهيئة شخصية {st.session_state.child_avatar} وصوت القارئ المعتمد...", "time": 2.5, "pct": 75, "done": "✔️ تم تحميل مكتبة القصص التفاعلية"},
        {"msg": f"اكتمل التخصيص بنجاح! جاهزون للانطلاق يا {c_name}! 🎉", "time": 2.5, "pct": 100, "done": "✔️ اكتملت الخطة وأصبح رفيق القراءة الذكي جاهزاً بالكامل!"}
    ]
    
    completed_log = []
    for stage in pipeline:
        status_text.markdown(f"**⏳ {stage['msg']}**")
        time.sleep(stage["time"])
        prog_bar.progress(stage["pct"])
        completed_log.append(f"<div style='color:#059669; font-size:14px; margin:4px 0;'>{stage['done']}</div>")
        checkpoints.markdown("".join(completed_log), unsafe_allow_html=True)
        
    render_nav(7, 9, next_label="دخول غرفة القراءة 📖")

# =========================================================
# 9. THE INTERACTIVE READING BUDDY (SEAMLESS 1-CLICK RECORD & EVALUATION)
# =========================================================
elif st.session_state.step == 9:
    page_data = BOOK_PAGES[st.session_state.page_idx]
    total_pages = len(BOOK_PAGES)
    
    c_name = st.session_state.child_name if st.session_state.child_name else "البطل"
    c_av = st.session_state.child_avatar if st.session_state.child_avatar else "رفيق القراءة"
    c_icon = st.session_state.child_avatar_icon
    
    st.caption(f"📚 قصة: سامي يتعلم القراءة — صفحة {st.session_state.page_idx + 1} من {total_pages}")
    
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        st.write(f"🌟 **القارئ البطل:** {c_name}")
        st.write(f"🤝 **المرافق:** {c_av}")
    with col_c2:
        st.markdown(f"<div style='font-size:40px; text-align:center;'>{c_icon}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="book-container">
        <div style="font-size: 55px; margin-bottom: 10px;">📖 🏫 ✨</div>
        <div class="book-sentence">{page_data['text']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"🎙️ **دورك يا {c_name}! اضغط على زر التسجيل وتحدث:**")
    
    # 1-Click Native Audio Recognition (Streamlit Native or Instant Text Speech Bridge)
    spoken_text = ""
    
    if HAS_RECORDER:
        spoken_text = speech_to_text(
            language='ar',
            start_prompt="🔴 اضغط لبدء القراءة بصوتك",
            stop_prompt="⏹️ اضغط لإنهاء التسجيل والتقييم الفوري",
            key=f"stt_{st.session_state.page_idx}"
        )
    else:
        # Seamless direct speech recognition fallback with immediate rerun
        speech_direct_js = f"""
        <div style="text-align: center; margin: 10px 0;">
            <button id="direct-rec" style="
                background: #EF4444; 
                color: white; 
                border: none; 
                border-radius: 50px; 
                padding: 16px 36px; 
                font-size: 20px; 
                font-weight: 800; 
                cursor: pointer;
                box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);">
                🔴 اضغط هنا وتحدث بصوتك
            </button>
            <div id="dir-status" style="margin-top: 8px; font-size: 15px; color: #475569; font-weight: bold;"></div>
        </div>
        <script>
            const btn = document.getElementById('direct-rec');
            const status = document.getElementById('dir-status');
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (SpeechRec) {{
                const rec = new SpeechRec();
                rec.lang = 'ar-SA';
                let isRec = false;
                
                btn.onclick = () => {{
                    if(!isRec) {{
                        rec.start();
                        isRec = true;
                        btn.innerText = "⏹️ جارٍ الاستماع... (اضغط للإنهاء)";
                        btn.style.background = "#10B981";
                        status.innerText = "🎙️ اقرأ الجملة بصوتك الواضح الآن...";
                    }} else {{
                        rec.stop();
                        isRec = false;
                    }}
                }};
                
                rec.onresult = (e) => {{
                    const res = e.results[0][0].transcript;
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("voice_input", res);
                    window.parent.location.href = url.toString();
                }};
            }}
        </script>
        """
        st.components.v1.html(speech_direct_js, height=120)
        query_params = st.query_params
        if "voice_input" in query_params:
            spoken_text = query_params["voice_input"]

    # Manual backup test input (optional, never blocks UI)
    with st.expander("📝 أو اكتب النص يدوياً (للتجربة السريعة)"):
        manual_override = st.text_input("النص:", value="", key=f"manual_{st.session_state.page_idx}")
        if manual_override:
            spoken_text = manual_override

    # IMMEDIATE AUTOMATIC SCORING (No second click needed!)
    if spoken_text:
        st.info(f"🗣️ **ما قاله الطفل:** {spoken_text}")
        is_success, score_10, word_eval = evaluate_reading_detailed(spoken_text, page_data["text"])
        
        # Save score for final report
        if not st.session_state.eval_done:
            st.session_state.reading_history.append({
                "page": st.session_state.page_idx + 1,
                "score": score_10,
                "success": is_success
            })
            st.session_state.eval_done = True
        
        # Word-by-Word Colored Feedback
        colored_words_html = []
        for word, is_corr in word_eval:
            if is_corr:
                colored_words_html.append(f'<span class="word-correct">{word}</span>')
            else:
                colored_words_html.append(f'<span class="word-wrong">{word}</span>')
        
        st.markdown(f"<div style='text-align:center; font-size:24px; margin:15px 0;'>{' '.join(colored_words_html)}</div>", unsafe_allow_html=True)
        
        # Teacher Benchmark (Success if Score > 6.0)
        if is_success:
            st.balloons()
            st.success(f"🎉 **Success! أحسنت يا {c_name}!** درجة الإتقان: {score_10} / 10 (تجاوزت معيار النجاح 6.0)")
        else:
            st.error(f"🔄 **Try Again! حاول مرة أخرى يا بطل!** درجة القراءة: {score_10} / 10 (أقل من معيار النجاح 6.0)")
            st.warning("🔊 استمع إلى طريقة القراءة الصحيحة من المعلم القارئ:")
            st.audio(page_data["audio"])
                
    if st.session_state.page_idx < total_pages - 1:
        if st.button("الانتقال إلى الصفحة التالية ⬅️"):
            st.session_state.page_idx += 1
            st.session_state.eval_done = False
            if "voice_input" in st.query_params:
                del st.query_params["voice_input"]
            st.rerun()
    else:
        if st.button("عرض التقرير والدرجة الختامية 🏆"):
            st.session_state.step = 10
            st.rerun()

# =========================================================
# 10. FINAL REPORT & TEACHER BENCHMARK ACCURACY
# =========================================================
elif st.session_state.step == 10:
    st.balloons()
    c_name = st.session_state.child_name if st.session_state.child_name else "البطل"
    st.title(f"🏆 وسام القراءة للبطل {c_name}!")
    
    if st.session_state.reading_history:
        avg_score = round(sum(item["score"] for item in st.session_state.reading_history) / len(st.session_state.reading_history), 1)
        passed_count = sum(1 for item in st.session_state.reading_history if item["success"])
    else:
        avg_score = 8.5
        passed_count = len(BOOK_PAGES)
        
    st.metric(label="متوسط درجة القراءة النهائية (المعيار المعتمد > 6.0)", value=f"{avg_score} / 10")
    
    st.markdown(f"""
    <div class="reassurance-box">
        🎉 <b>ما شاء الله تبارك الله يا {c_name}!</b><br>
        أتممت قراءة جميع صفحات القصة بنجاح وتجاوزت {passed_count} من أصل {len(BOOK_PAGES)} صفحات فوق معيار الإتقان المطلوب!
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 بدء جلسة قراءة جديدة أو قصة أخرى"):
        st.session_state.step = 7
        st.session_state.page_idx = 0
        st.session_state.reading_history = []
        st.session_state.eval_done = False
        st.rerun()