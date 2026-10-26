
import re
import html
import requests
import streamlit as st
from groq import Groq

# ============================================================
# VIRALLAB STUDIO
# Step-by-step wizard + AI strategy + automatic thumbnail
# ============================================================

st.set_page_config(
    page_title="ViralLab Studio",
    page_icon="🚀",
    layout="centered",
)

# -------------------- DESIGN AND ANIMATIONS --------------------

st.markdown("""
<style>
@keyframes enter {
    from { opacity: 0; transform: translateY(16px) scale(.99); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes glow {
    0%,100% { box-shadow: 0 0 12px #8b5cf622; }
    50% { box-shadow: 0 0 24px #38bdf833; }
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.hero {
    padding: 1.6rem;
    border: 1px solid #7770b8;
    border-radius: 22px;
    background: linear-gradient(120deg,#17152b,#292044,#102c3a,#17152b);
    background-size: 300% 300%;
    animation: gradientMove 12s ease infinite, glow 5s ease infinite;
    margin-bottom: 1.5rem;
}
.motion-card {
    padding: 1.35rem;
    border-radius: 18px;
    border: 1px solid #62578b;
    background: rgba(120,110,170,.07);
    animation: enter .4s ease both;
    margin: .8rem 0 1rem;
}
.step-label {
    color: #c4b5fd;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
    font-size: .8rem;
}
.big-question {
    font-size: 1.6rem;
    font-weight: 750;
    line-height: 1.25;
    margin: .7rem 0;
}
div[data-testid="stExpander"] {
    border-radius: 13px;
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
    animation: enter .65s ease both;
}
hr { border-color: #ffffff20; }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------- CONSTANTS --------------------

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
            "Lifestyle", "Finance", "Fitness", "Travel", "Food", "Other",
        ],
    },
    {
        "key": "topic",
        "title": "What's your video topic?",
        "help": "Example: Best budget gaming phones in 2026.",
        "type": "text",
    },
    {
        "key": "audience",
        "title": "Who is your target audience?",
        "help": "Choose the people you want to reach.",
        "options": [
            "Students", "Beginners", "Gamers", "Tech enthusiasts",
            "Professionals", "General audience", "My own audience",
        ],
    },
    {
        "key": "video_style",
        "title": "Choose your video style",
        "help": "How will you present your video?",
        "options": [
            "Informative", "Tutorial", "Comparison", "Review",
            "Listicle", "Storytelling", "Entertainment",
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
        "help": "ViralLab will generate the thumbnail automatically.",
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
    "item_indices": {},
    "thumbnail": None,
    "thumbnail_ext": "jpg",
    "thumbnail_mime": "image/jpeg",
    "form_error": "",
    "generation_error": "",
    "generate_requested": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- WIZARD NAVIGATION --------------------

def save_answer_and_advance(step):
    """Save the current step before changing screens."""
    question = QUESTIONS[step]
    key = question["key"]
    draft_key = f"draft_{key}"

    st.session_state.form_error = ""

    value = st.session_state.get(draft_key, st.session_state.get(key, ""))

    if key == "topic" and not str(value).strip():
        st.session_state.form_error = (
            "Please enter your video topic before continuing."
        )
        return

    st.session_state[key] = value

    if step == len(QUESTIONS) - 1:
        extra = st.session_state.get("draft_extra_details", "")
        st.session_state.extra_details = extra
        st.session_state.generate_requested = True
    else:
        st.session_state.wizard_step = step + 1


def go_back(step):
    """Return to the previous step without deleting saved answers."""
    question = QUESTIONS[step]
    key = question["key"]
    draft_key = f"draft_{key}"

    if draft_key in st.session_state:
        st.session_state[key] = st.session_state[draft_key]

    if step == len(QUESTIONS) - 1:
        st.session_state.extra_details = st.session_state.get(
            "draft_extra_details", ""
        )

    st.session_state.form_error = ""
    st.session_state.wizard_step = max(0, step - 1)


def move_result(index):
    st.session_state.result_index = index


def move_item(section, index):
    st.session_state.item_indices[section] = index


def reset_project():
    """Clear the old project and all temporary answers."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()

# -------------------- AI PROMPT --------------------

def make_strategy_prompt():
    headings = "\n".join(SECTIONS)

    return f"""
You are ViralLab, an expert YouTube growth strategist.

NICHE: {st.session_state.niche}
VIDEO TOPIC: {st.session_state.topic}
TARGET AUDIENCE: {st.session_state.audience}
VIDEO STYLE: {st.session_state.video_style}
CONTENT LANGUAGE: {st.session_state.language}

Create a practical, specific YouTube content strategy.

RULES:
- Write in the selected content language.
- Use all nine headings below exactly as written.
- Put every heading on its own line.
- Do not rename, omit or duplicate headings.
- Give exactly five distinct video ideas.
- Give exactly five distinct clickable titles.
- Make the script natural and engaging, with a strong opening and ending.
- Include a relevant SEO description, keywords and hashtags.
- Give a practical growth plan for a new creator.
- Make the thumbnail concept visually descriptive.
- Do not invent product specifications, prices, statistics or test results.
- Use Markdown formatting, but do not put the complete answer in a code block.
- Avoid repeating the same content across sections.

HEADINGS:
{headings}
""".strip()


def split_strategy(text):
    """Find the nine expected sections in the generated response."""
    found = []

    for title in SECTIONS:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?(?:\d+[\.\):\-]\s*)?"
            + re.escape(title)
            + r"\s*:?\s*$"
        )
        match = pattern.search(text)

        if match:
            found.append((match.start(), match.end(), title))

    found.sort(key=lambda x: x[0])
    result = {}

    for index, (_, end, title) in enumerate(found):
        next_start = (
            found[index + 1][0]
            if index + 1 < len(found)
            else len(text)
        )
        result[title] = text[end:next_start].strip()

    return result


def split_numbered_items(text):
    """Split numbered lists into separate cards."""
    items = []
    current = []

    for line in text.splitlines():
        match = re.match(
            r"^\s*(?:[-*]\s+|\d+[\.\)]\s+)(.+)",
            line,
        )

        if match:
            if current:
                items.append("\n".join(current).strip())
            current = [match.group(1).strip()]
        elif current:
            current.append(line)

    if current:
        items.append("\n".join(current).strip())

    return [item for item in items if item]


# -------------------- IMAGE GENERATION --------------------

def make_image_prompt():
    concept = st.session_state.sections.get(
        "THUMBNAIL CONCEPT",
        f"A compelling visual about {st.session_state.topic}.",
    )

    styles = {
        "Bold YouTube creator style":
            "bold composition, dramatic lighting, vibrant contrast",
        "Photorealistic tech review":
            "photorealistic materials and professional studio lighting",
        "Minimal and professional":
            "minimal composition, clean background and elegant lighting",
        "Gaming and entertainment":
            "dynamic gaming atmosphere and cinematic lighting",
        "Educational and documentary":
            "cinematic photography and clear visual storytelling",
    }

    extra = st.session_state.extra_details.strip()
    extra_text = f" Additional direction: {extra}." if extra else ""

    return f"""
Create a professional 16:9 YouTube thumbnail image.

Topic: {st.session_state.topic}
Niche: {st.session_state.niche}
Audience: {st.session_state.audience}
Thumbnail concept: {concept}
Visual style: {styles.get(st.session_state.thumbnail_style, "cinematic lighting")}.

Use one clear focal subject, strong contrast and a balanced composition.
Leave space for a title to be added later.
Do not render text, letters, logos or watermarks.
{extra_text}
""".strip()


def generate_image(prompt, api_key):
    url = (
        "https://gen.pollinations.ai/image/"
        + requests.utils.quote(prompt, safe="")
    )

    response = requests.get(
        url,
        params={
            "model": "black-forest-labs/flux.2-klein-4b",
            "width": 1280,
            "height": 720,
        },
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=180,
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if not content_type.startswith("image/"):
        raise ValueError("The image service did not return an image.")

    if "png" in content_type:
        extension, mime = "png", "image/png"
    elif "webp" in content_type:
        extension, mime = "webp", "image/webp"
    else:
        extension, mime = "jpg", "image/jpeg"

    return response.content, extension, mime


# -------------------- GENERATE BOTH OUTPUTS --------------------

def run_generation():
    topic = str(st.session_state.topic).strip()

    if not topic:
        st.session_state.generate_requested = False
        st.session_state.form_error = (
            "Your video topic is missing. Please go back to Step 2 and enter it."
        )
        st.session_state.wizard_step = 1
        return

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    image_key = st.secrets.get("POLLINATIONS_API_KEY", "")

    if not groq_key:
        st.session_state.generation_error = (
            "GROQ_API_KEY is missing from Streamlit Secrets."
        )
        st.session_state.generate_requested = False
        return

    # Clear old results before starting a new generation.
    st.session_state.strategy = ""
    st.session_state.sections = {}
    st.session_state.result_order = []
    st.session_state.result_index = 0
    st.session_state.item_indices = {}
    st.session_state.thumbnail = None
    st.session_state.generation_error = ""

    try:
        with st.spinner("🧠 Creating your YouTube strategy..."):
            client = Groq(api_key=groq_key)

            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise YouTube strategist. "
                            "Follow all headings and formatting requirements."
                        ),
                    },
                    {
                        "role": "user",
                        "content": make_strategy_prompt(),
                    },
                ],
                temperature=0.6,
                max_completion_tokens=5000,
            )

            strategy = completion.choices[0].message.content or ""

            if not strategy.strip():
                raise ValueError(
                    "The AI returned an empty strategy. Please try again."
                )

            st.session_state.strategy = strategy
            st.session_state.sections = split_strategy(strategy)
            st.session_state.result_order = [
                title for title in SECTIONS
                if st.session_state.sections.get(title)
            ]

        # Strategy is saved before attempting the image, so image failure
        # cannot erase the strategy.
        if image_key:
            try:
                with st.spinner("🎨 Generating your thumbnail..."):
                    image, extension, mime = generate_image(
                        make_image_prompt(), image_key
                    )

                    st.session_state.thumbnail = image
                    st.session_state.thumbnail_ext = extension
                    st.session_state.thumbnail_mime = mime

            except requests.RequestException:
                st.session_state.generation_error = (
                    "The strategy is ready, but the image service could not "
                    "complete the request. Check your connection, Pollinations "
                    "key, account balance and usage limits."
                )
            except Exception:
                st.session_state.generation_error = (
                    "The strategy is ready, but thumbnail generation failed. "
                    "Check the Pollinations key and account usage, then try again."
                )
        else:
            st.session_state.generation_error = (
                "The strategy is ready. Add POLLINATIONS_API_KEY in "
                "Streamlit Secrets to enable automatic thumbnails."
            )

    except Exception as exc:
        # Avoid printing secret values or full request headers.
        message = str(exc)
        st.session_state.generation_error = (
            "Strategy generation failed. Check your Groq API key, model "
            "availability, network connection and usage limits. "
            f"Details: {message[:300]}"
        )

    finally:
        st.session_state.generate_requested = False


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
    <h1>🚀 ViralLab Studio</h1>
    <p>Your AI-powered YouTube content workspace.</p>
    <p>Plan smarter. Create faster. Grow your channel.</p>
</div>
""", unsafe_allow_html=True)

st.caption("Powered by Groq for strategy and Pollinations for images.")

# Process the request after the final wizard form submits.
if st.session_state.generate_requested and not st.session_state.strategy:
    run_generation()

# -------------------- INPUT WIZARD --------------------

if not st.session_state.strategy:
    step = st.session_state.wizard_step
    question = QUESTIONS[step]
    key = question["key"]
    draft_key = f"draft_{key}"

    st.progress((step + 1) / len(QUESTIONS))
    st.caption(f"STEP {step + 1} OF {len(QUESTIONS)}")

    st.markdown(
        f'<div class="motion-card">'
        f'<div class="step-label">YOUR CONTENT JOURNEY</div>'
        f'<div class="big-question">{html.escape(question["title"])}</div>'
        f'<p>{html.escape(question["help"])}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Every step has its own form. Submitting the form saves the answer
    # explicitly before navigating, preventing the topic from being lost.
    with st.form(key=f"wizard_form_{step}", clear_on_submit=False):
        if question.get("type") == "text":
            st.text_input(
                "Video topic",
                key=draft_key,
                value=None if draft_key in st.session_state else st.session_state[key],
                placeholder="Enter your video topic...",
                label_visibility="collapsed",
            )
        else:
            options = question["options"]
            current_value = st.session_state.get(key, options[0])
            default_index = (
                options.index(current_value)
                if current_value in options else 0
            )

            st.radio(
                question["title"],
                options,
                index=default_index,
                key=draft_key,
                label_visibility="collapsed",
            )

        if key == "thumbnail_style":
            st.text_input(
                "Optional thumbnail details",
                key="draft_extra_details",
                value=(
                    None if "draft_extra_details" in st.session_state
                    else st.session_state.extra_details
                ),
                placeholder="Optional: red and blue lighting, phone, etc.",
            )

        left, right = st.columns(2)

        with left:
            if step > 0:
                st.form_submit_button(
                    "← Back",
                    use_container_width=True,
                    on_click=go_back,
                    args=(step,),
                )

        with right:
            label = (
                "✨ Generate My Content"
                if step == len(QUESTIONS) - 1
                else "Next →"
            )

            st.form_submit_button(
                label,
                type="primary",
                use_container_width=True,
                on_click=save_answer_and_advance,
                args=(step,),
            )

    if st.session_state.form_error:
        st.error(st.session_state.form_error)

    if st.session_state.generation_error:
        st.error(st.session_state.generation_error)

# -------------------- STEP-BY-STEP RESULTS --------------------

else:
    st.success("Your strategy has been generated.")

    if st.session_state.generation_error:
        st.warning(st.session_state.generation_error)

    order = st.session_state.result_order

    if order:
        idx = min(
            st.session_state.result_index,
            len(order) - 1,
        )
        title = order[idx]
        body = st.session_state.sections[title]

        st.progress((idx + 1) / len(order))
        st.caption(f"RESULT SECTION {idx + 1} OF {len(order)}")

        st.markdown(
            f'<div class="motion-card">'
            f'<div class="step-label">YOUR AI RESULTS</div>'
            f'<div class="big-question">{html.escape(title.title())}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Show ideas and titles one at a time.
  
