
import re
import requests
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="ViralLab Studio",
    page_icon="🚀",
    layout="centered",
)

# -------------------- ANIMATED DESIGN --------------------

st.markdown("""
<style>
@keyframes enter {
    from { opacity: 0; transform: translateY(18px) scale(.985); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes pulse {
    0%,100% { box-shadow: 0 0 12px #8b5cf622; }
    50% { box-shadow: 0 0 28px #38bdf844; }
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.hero {
    padding: 1.7rem;
    border: 1px solid #7770b8;
    border-radius: 22px;
    background: linear-gradient(120deg,#17152b,#292044,#102c3a,#17152b);
    background-size: 300% 300%;
    animation: gradientMove 12s ease infinite, pulse 5s ease infinite;
    margin-bottom: 1.4rem;
}
.motion-card {
    padding: 1.4rem;
    border-radius: 18px;
    border: 1px solid #62578b;
    background: rgba(120,110,170,.07);
    animation: enter .45s ease both;
    margin: .7rem 0 1rem;
}
.step-number {
    color: #c4b5fd;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.big-question {
    font-size: 1.65rem;
    font-weight: 750;
    margin: .6rem 0 1rem;
}
.result-number {
    font-size: 1rem;
    color: #c4b5fd;
    font-weight: 700;
}
div[data-testid="stExpander"] {
    border-radius: 12px;
    border: 1px solid #ffffff22;
}
.stButton button, .stDownloadButton button {
    border-radius: 12px;
    transition: transform .2s ease, box-shadow .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px #8b5cf633;
}
div[data-testid="stImage"] img {
    border-radius: 16px;
    animation: enter .7s ease both;
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

SECTIONS = [
    "CONTENT ANGLE",
    "FIVE VIDEO IDEAS",
    "FIVE CLICKABLE TITLES",
    "THUMBNAIL CONCEPT",
    "OPENING HOOK",
    "COMPLETE VIDEO SCRIPT",
    "SEO DESCRIPTION",
    "KEYWORDS AND HASHTAGS",
    "GROWTH PLAN",
]

QUESTIONS = [
    {
        "key": "niche",
        "title": "Choose your content niche",
        "help": "What kind of videos do you create?",
        "options": [
            "Gaming", "Technology", "Education", "Entertainment",
            "Lifestyle", "Finance", "Fitness", "Travel", "Food", "Other"
        ],
    },
    {
        "key": "topic",
        "title": "What's your video topic?",
        "help": "Be specific. For example: Best budget gaming phones in 2026.",
        "type": "text",
    },
    {
        "key": "audience",
        "title": "Who is your target audience?",
        "help": "Choose the people you want your video to reach.",
        "options": [
            "Students", "Beginners", "Gamers", "Tech enthusiasts",
            "Professionals", "General audience", "My own audience"
        ],
    },
    {
        "key": "video_style",
        "title": "Choose your video style",
        "help": "How do you want to present your video?",
        "options": [
            "Informative", "Tutorial", "Comparison", "Review",
            "Listicle", "Storytelling", "Entertainment"
        ],
    },
    {
        "key": "language",
        "title": "Choose your content language",
        "help": "The strategy and script will use this language.",
        "options": ["English", "Hindi", "Hinglish", "Bengali", "Punjabi"],
    },
    {
        "key": "thumbnail_style",
        "title": "Choose your thumbnail style",
        "help": "ViralLab will generate a thumbnail automatically.",
        "options": [
            "Bold YouTube creator style",
            "Photorealistic tech review",
            "Minimal and professional",
            "Gaming and entertainment",
            "Educational and documentary",
        ],
    },
]

DEFAULTS = {
    "wizard_step": 0,
    "niche": "Gaming",
    "topic": "",
    "audience": "Students",
    "video_style": "Informative",
    "language": "English",
    "thumbnail_style": "Bold YouTube creator style",
    "extra_details": "",
    "strategy": "",
    "sections": {},
    "result_order": [],
    "result_index": 0,
    "thumbnail": None,
    "thumbnail_ext": "jpg",
    "thumbnail_mime": "image/jpeg",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def set_wizard_step(step):
    st.session_state.wizard_step = step


def set_result_index(index):
    st.session_state.result_index = index


def make_prompt():
    headings = "\n".join(SECTIONS)
    return f"""
You are ViralLab, an expert YouTube growth strategist.

Niche: {st.session_state.niche}
Topic: {st.session_state.topic}
Audience: {st.session_state.audience}
Video style: {st.session_state.video_style}
Language: {st.session_state.language}

Create a useful, specific content plan. Write the content in the selected
language. Use Markdown, but do not put the complete answer in a code block.

Use these nine headings EXACTLY, in this order, each on its own line:
{headings}

Requirements:
- Exactly five distinct video ideas.
- Exactly five distinct clickable titles.
- No repeated ideas or duplicated lines.
- Include a strong opening hook.
- Give a complete, natural video script with an ending.
- Include an SEO description, relevant keywords and hashtags.
- Give a practical growth plan for a new creator.
- Make the thumbnail concept visually descriptive.
- Do not invent prices, specifications, statistics or test results.
""".strip()


def split_strategy(text):
    found = []
    for title in SECTIONS:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?(?:\d+[\.\):\-]\s*)?"
            + re.escape(title) + r"\s*:?\s*$"
        )
        match = pattern.search(text)
        if match:
            found.append((match.start(), match.end(), title))

    found.sort()
    output = {}
    for i, (_, end, title) in enumerate(found):
        next_start = found[i + 1][0] if i + 1 < len(found) else len(text)
        output[title] = text[end:next_start].strip()
    return output


def split_items(text):
    """Separate numbered ideas/titles into individual result cards."""
    lines = text.splitlines()
    items = []
    current = []

    for line in lines:
        match = re.match(r"^\s*(?:[-*]\s+|\d+[\.\)]\s+)(.+)", line)
        if match:
            if current:
                items.append("\n".join(current).strip())
            current = [match.group(1).strip()]
        elif current:
            current.append(line)

    if current:
        items.append("\n".join(current).strip())

    return [item for item in items if item]


def make_image_prompt():
    concept = st.session_state.sections.get(
        "THUMBNAIL CONCEPT",
        f"A compelling visual about {st.session_state.topic}",
    )
    styles = {
        "Bold YouTube creator style":
            "bold colors, dramatic contrast, strong focal point",
        "Photorealistic tech review":
            "photorealistic materials, professional studio lighting",
        "Minimal and professional":
            "minimal composition, clean background, elegant lighting",
        "Gaming and entertainment":
            "dynamic gaming atmosphere, cinematic lighting",
        "Educational and documentary":
            "cinematic photography, clear visual storytelling",
    }
    return f"""
Create a professional 16:9 YouTube thumbnail.
Topic: {st.session_state.topic}
Niche: {st.session_state.niche}
Audience: {st.session_state.audience}
Concept: {concept}
Visual style: {styles.get(st.session_state.thumbnail_style, "cinematic lighting")}
Use one clear focal subject, strong contrast, and space for a title.
No text, no letters, no logos, no watermarks.
"""


def generate_image(prompt, key):
    url = "https://gen.pollinations.ai/image/" + requests.utils.quote(
        prompt, safe=""
    )
    response = requests.get(
        url,
        params={
            "model": "black-forest-labs/flux.2-klein-4b",
            "width": 1280,
            "height": 720,
        },
        headers={"Authorization": f"Bearer {key}"},
        timeout=180,
    )
    response.raise_for_status()
    mime = response.headers.get("Content-Type", "").lower()
    if not mime.startswith("image/"):
        raise ValueError("The image service did not return an image.")

    if "png" in mime:
        ext, mime = "png", "image/png"
    elif "webp" in mime:
        ext, mime = "webp", "image/webp"
    else:
        ext, mime = "jpg", "image/jpeg"

    return response.content, ext, mime


def run_generation():
    if not st.session_state.topic.strip():
        st.error("Please enter your video topic.")
        return

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    image_key = st.secrets.get("POLLINATIONS_API_KEY", "")

    if not groq_key:
        st.error("GROQ_API_KEY is missing from Streamlit Secrets.")
        return

    st.session_state.strategy = ""
    st.session_state.sections = {}
    st.session_state.result_order = []
    st.session_state.result_index = 0
    st.session_state.thumbnail = None

    try:
        with st.spinner("🧠 Step 1: Building your strategy..."):
            client = Groq(api_key=groq_key)
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise YouTube content strategist.",
                    },
                    {"role": "user", "content": make_prompt()},
                ],
                temperature=0.6,
                max_completion_tokens=5000,
            )
            strategy = completion.choices[0].message.content or ""
            if not strategy.strip():
                st.error("The AI returned an empty strategy. Try again.")
                return

        st.session_state.strategy = strategy
        st.session_state.sections = split_strategy(strategy)
        st.session_state.result_order = [
            title for title in SECTIONS
            if st.session_state.sections.get(title)
        ]

        if image_key:
            try:
                with st.spinner("🎨 Step 2: Creating your thumbnail..."):
                    image, ext, mime = generate_image(
                        make_image_prompt(), image_key
                    )
                    st.session_state.thumbnail = image
                    st.session_state.thumbnail_ext = ext
                    st.session_state.thumbnail_mime = mime
            except Exception as exc:
                st.warning(
                    "Strategy is ready, but thumbnail generation failed. "
                    f"Check your Pollinations account and key. Details: {exc}"
                )
        else:
            st.warning(
                "Strategy is ready. Add POLLINATIONS_API_KEY to Streamlit "
                "Secrets to enable automatic thumbnails."
            )

        st.success("Your content plan is ready!")
    except Exception as exc:
        st.error(f"Strategy generation failed: {exc}")


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
  <h1>🚀 ViralLab Studio</h1>
  <p>Your AI-powered YouTube content workspace.</p>
  <p>Plan smarter. Create faster. Grow your channel.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- INPUT WIZARD --------------------

if not st.session_state.strategy:
    step = st.session_state.wizard_step
    question = QUESTIONS[step]

    st.progress((step + 1) / len(QUESTIONS))
    st.caption(f"STEP {step + 1} OF {len(QUESTIONS)}")

    st.markdown('<div class="motion-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="step-number">YOUR CONTENT JOURNEY</div>'
        f'<div class="big-question">{question["title"]}</div>'
        f'<p>{question["help"]}</p>',
        unsafe_allow_html=True,
    )

    key = question["key"]

    if question.get("type") == "text":
        st.text_input(
            "Video topic",
            key=key,
            placeholder="Enter your video topic...",
            label_visibility="collapsed",
        )
    else:
        st.radio(
            question["title"],
            question["options"],
            key=key,
            label_visibility="collapsed",
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if key == "thumbnail_style":
        st.text_input(
            "Optional thumbnail details",
            key="extra_details",
            placeholder="Optional: red and blue lighting, phone, etc.",
        )

    left, right = st.columns(2)

    with left:
        if step > 0:
            st.button(
                "← Back",
                use_container_width=True,
                on_click=set_wizard_step,
                args=(step - 1,),
            )

    with right:
        if step < len(QUESTIONS) - 1:
            st.button(
                "Next →",
                type="primary",
                use_container_width=True,
                on_click=set_wizard_step,
                args=(step + 1,),
            )
        else:
            st.button(
                "✨ Generate My Content",
                type="primary",
                use_container_width=True,
                on_click=run_generation,
            )

# -------------------- RESULTS WIZARD --------------------

else:
    st.success("Your strategy and thumbnail workflow is complete.")
    st.progress(1.0)

    order = st.session_state.result_order

    if order:
        idx = min(st.session_state.result_index, len(order) - 1)
        title = order[idx]
        body = st.session_state.sections[title]

        st.caption(f"CONTENT SECTION {idx + 1} OF {len(order)}")
        st.markdown(
            f'<div class="motion-card">'
            f'<div class="step-number">YOUR AI RESULTS</div>'
            f'<div class="big-question">{title.title()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Five ideas and five titles are shown one at a time.
        if title in ("FIVE VIDEO IDEAS", "FIVE CLICKABLE TITLES"):
            items = split_items(body)
            if items:
                if f"item_index_{title}" not in st.session_state:
                    st.session_state[f"item_index_{title}"] = 0

                item_key = f"item_index_{title}"
                item_idx = min(st.session_state[item_key], len(items) - 1)

                st.progress((item_idx + 1) / len(items))
                st.caption(f"ITEM {item_idx + 1} OF {len(items)}")

                st.markdown(
                    f'<div class="motion-card">'
                    f'<div class="result-number">#{item_idx + 1}</div>'
                    f'<div style="font-size:1.15rem;line-height:1.7">'
                    f'{items[item_idx].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                prev, next_col = st.columns(2)
                with prev:
                    if item_idx > 0:
                        st.button(
                            "← Previous",
                            key=f"prev_{title}",
                            use_container_width=True,
                            on_click=set_result_index,
                            args=(idx,),
                        )
                        if st.session_state[item_key] > 0:
                            st.button(
                                "← Previous item",
                                key=f"previtem_{title}",
                                use_container_width=True,
                                on_click=lambda k=item_key: st.session_state.__setitem__(
                                    k, max(0, st.session_state[k] - 1)
                                ),
                            )

                with next_col:
                    if item_idx < len(items) - 1:
                        st.button(
                            "Next item →",
                            key=f"nextitem_{title}",
                            type="primary",
                            use_container_width=True,
                            on_click=lambda k=item_key, n=len(items): st.session_state.__setitem__(
                                k, min(n - 1, st.session_state[k] + 1)
                            ),
                        )
                    else:
                        st.caption("You've viewed all items in this section.")

                st.download_button(
                    "📥 Download this section",
                    data=body,
                    file_name=title.lower().replace(" ", "_") + ".md",
                    mime="text/markdown",
                    key=f"download_{title}",
                )
            else:
                st.markdown(body)
        else:
            st.markdown(body)
            st.download_button(
                "📥 Download this section",
                data=body,
                file_name=title.lower().replace(" ", "_") + ".md",
                mime="text/markdown",
                key=f"download_{title}",
            )

        st.divider()
        prev_section, next_section = st.columns(2)

        with prev_section:
            if idx > 0:
                st.button(
                    "← Previous section",
                    use_container_width=True,
                    on_click=set_result_index,
                    args=(idx - 1,),
                )

        with next_section:
            if idx < len(order) - 1:
                st.button(
                    "Next section →",
                    type="primary",
                    use_container_width=True,
                    on_click=set_result_index,
                    args=(idx + 1,),
                )
            else:
                st.success("You've reached the end of your strategy.")

    st.divider()
    st.header("🎨 Your AI Thumbnail")

    if st.session_state.thumbnail:
        st.image(
            st.session_state.thumbnail,
            caption="AI-generated thumbnail",
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Download Thumbnail",
            data=st.session_state.thumbnail,
            file_name="ViralLab_Thumbnail." + st.session_state.thumbnail_ext,
            mime=st.session_state.thumbnail_mime,
            use_container_width=True,
        )
    else:
        st.info(
            "No thumbnail was generated this time. Your strategy is still "
            "available above. Check Pollinations usage and credentials."
        )

    st.download_button(
        "📥 Download Complete Strategy",
        data=st.session_state.strategy,
        file_name="ViralLab_Complete_Strategy.md",
        mime="text/markdown",
        use_container_width=True,
    )

    if st.button("🔄 Start a New Project", use_container_width=True):
        for key, value in DEFAULTS.items():
            st.session_state[key] = value
        st.rerun()

st.divider()
st.caption(
    "ViralLab uses AI-generated content. Verify factual claims before publishing."
                    )
