import re
import html
import requests
import streamlit as st
from groq import Groq

# ==========================================================
# VIRALLAB STUDIO
# Robust input wizard, strategy results, and image generation
# ==========================================================

st.set_page_config(
    page_title="ViralLab Studio",
    page_icon="🚀",
    layout="centered",
)

# -------------------- ANIMATED DESIGN --------------------

st.markdown("""
<style>
@keyframes reveal {
    from {opacity: 0; transform: translateY(14px);}
    to {opacity: 1; transform: translateY(0);}
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 1.5rem;
    border-radius: 20px;
    border: 1px solid #7669ad;
    background: linear-gradient(120deg,#17152b,#292044,#102c3a,#17152b);
    background-size: 300% 300%;
    animation: gradient 12s ease infinite;
    margin-bottom: 1.3rem;
}
.motion-card {
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid #62578b;
    background: rgba(120,110,170,.07);
    animation: reveal .4s ease both;
    margin: .7rem 0 1rem;
}
.step-label {
    color: #c4b5fd;
    font-size: .8rem;
    font-weight: 700;
    letter-spacing: .08em;
}
.big-question {
    font-size: 1.55rem;
    font-weight: 750;
    margin: .6rem 0;
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
    border-radius: 15px;
    animation: reveal .6s ease both;
}
hr {border-color: #ffffff20;}
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
            "Lifestyle", "Finance", "Fitness", "Travel", "Food", "Other"
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
            "Professionals", "General audience", "My own audience"
        ],
    },
    {
        "key": "video_style",
        "title": "Choose your video style",
        "help": "How will you present your video?",
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
        "help": "Your thumbnail will be generated automatically.",
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
    "result_index": 0,
    "item_indices": {},
    "thumbnail": None,
    "thumbnail_ext": "jpg",
    "thumbnail_mime": "image/jpeg",
    "error": "",
    "generation_requested": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- WIZARD FUNCTIONS --------------------

def save_and_next(step):
    question = QUESTIONS[step]
    key = question["key"]
    draft = st.session_state.get("draft_" + key, st.session_state.get(key, ""))

    st.session_state.error = ""

    if key == "topic" and not str(draft).strip():
        st.session_state.error = "Please enter your video topic before continuing."
        return

    st.session_state[key] = draft

    if step == len(QUESTIONS) - 1:
        st.session_state.extra_details = st.session_state.get(
            "draft_extra_details", ""
        )
        st.session_state.generation_requested = True
    else:
        st.session_state.wizard_step = step + 1


def go_back(step):
    question = QUESTIONS[step]
    key = question["key"]

    if "draft_" + key in st.session_state:
        st.session_state[key] = st.session_state["draft_" + key]

    if step == len(QUESTIONS) - 1:
        st.session_state.extra_details = st.session_state.get(
            "draft_extra_details", ""
        )

    st.session_state.error = ""
    st.session_state.wizard_step = max(0, step - 1)


def reset_project():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def go_to_result(index):
    st.session_state.result_index = index


def go_to_item(section, index):
    st.session_state.item_indices[section] = index


# -------------------- STRATEGY PROMPT --------------------

def make_strategy_prompt():
    headings = "\n".join(SECTIONS)

    return f"""
You are ViralLab, an expert YouTube growth strategist.

Niche: {st.session_state.niche}
Topic: {st.session_state.topic}
Audience: {st.session_state.audience}
Video style: {st.session_state.video_style}
Language: {st.session_state.language}

Write the strategy in the selected language.

Use these nine headings EXACTLY, each on its own line:
{headings}

Rules:
- Give exactly five different video ideas.
- Give exactly five different clickable titles.
- Do not repeat ideas or titles.
- Include a strong opening hook.
- Write a complete natural script with an ending.
- Include a relevant SEO description, keywords, and hashtags.
- Give a practical growth plan for a new creator.
- Describe a clear visual thumbnail concept.
- Do not invent prices, specifications, statistics, or test results.
- Use Markdown formatting.
- Do not wrap the entire response in a code block.
""".strip()


def split_strategy(text):
    """Split headings when possible; never require a perfect AI response."""
    matches = []

    for title in SECTIONS:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?(?:\d+[\.\):\-]\s*)?"
            + re.escape(title)
            + r"\s*:?\s*$"
        )

        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), title))

    matches.sort(key=lambda x: x[0])

    result = {}
    seen = set()

    for i, (_, end, title) in enumerate(matches):
        if title in seen:
            continue

        seen.add(title)

        next_start = len(text)
        for j in range(i + 1, len(matches)):
            if matches[j][0] > end:
                next_start = matches[j][0]
                break

        body = text[end:next_start].strip()
        if body:
            result[title] = body

    return result


def split_items(text):
    """Split numbered or bulleted lists into separate cards."""
    items = []
    current = []

    for line in text.splitlines():
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
            "minimal composition, clean background, elegant lighting",
        "Gaming and entertainment":
            "dynamic gaming atmosphere and cinematic lighting",
        "Educational and documentary":
            "cinematic photography and clear visual storytelling",
    }

    extra = st.session_state.extra_details.strip()
    extra_text = f" Extra direction: {extra}." if extra else ""

    return f"""
Create a professional 16:9 YouTube thumbnail.

Topic: {st.session_state.topic}
Niche: {st.session_state.niche}
Audience: {st.session_state.audience}
Concept: {concept}
Visual style: {styles.get(st.session_state.thumbnail_style, "cinematic lighting")}.

Use one clear focal subject, strong contrast and balanced composition.
Leave space for a title to be added later.
No text, letters, logos, or watermarks.
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


# -------------------- GENERATION WORKFLOW --------------------

def run_generation():
    topic = str(st.session_state.topic).strip()

    if not topic:
        st.session_state.error = (
            "Your topic is empty. Please go back to Step 2 and enter it."
        )
        st.session_state.wizard_step = 1
        st.session_state.generation_requested = False
        return

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    image_key = st.secrets.get("POLLINATIONS_API_KEY", "")

    if not groq_key:
        st.session_state.error = (
            "GROQ_API_KEY is missing from Streamlit Secrets."
        )
        st.session_state.generation_requested = False
        return

    # Clear previous project output before generating a new one.
    st.session_state.strategy = ""
    st.session_state.sections = {}
    st.session_state.result_index = 0
    st.session_state.item_indices = {}
    st.session_state.thumbnail = None

    try:
        with st.spinner("🧠 Generating your YouTube strategy..."):
            client = Groq(api_key=groq_key)

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise YouTube strategist. "
                            "Follow the headings and formatting requirements."
                        ),
                    },
                    {"role": "user", "content": make_strategy_prompt()},
                ],
                temperature=0.6,
                max_completion_tokens=5000,
            )

            strategy = response.choices[0].message.content or ""

            if not strategy.strip():
                raise ValueError("The AI returned an empty strategy.")

            # Save the entire answer before trying to parse sections.
            st.session_state.strategy = strategy

            parsed = split_strategy(strategy)
            st.session_state.sections = parsed

            # If parsing fails, make the full strategy a visible result.
            if not parsed:
                st.session_state.sections = {
                    "COMPLETE STRATEGY": strategy
                }

    except Exception as exc:
        st.session_state.error = (
            "Strategy generation failed. Check the Groq key, model "
            "availability, network connection, and usage limits. "
            f"Details: {str(exc)[:250]}"
        )
        st.session_state.generation_requested = False
        return

    # Image errors must never erase the strategy.
    if image_key:
        try:
            with st.spinner("🎨 Generating your thumbnail..."):
                image, extension, mime = generate_image(
                    make_image_prompt(), image_key
                )
                st.session_state.thumbnail = image
                st.session_state.thumbnail_ext = extension
                st.session_state.thumbnail_mime = mime

        except Exception as exc:
            st.session_state.error = (
                "Your strategy is ready, but thumbnail generation failed. "
                "Check the Pollinations key, account usage, and connection. "
                f"Details: {str(exc)[:200]}"
            )
    else:
        st.session_state.error = (
            "Your strategy is ready. Add POLLINATIONS_API_KEY in "
            "Streamlit Secrets to enable automatic thumbnails."
        )

    st.session_state.generation_requested = False


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
  <h1>🚀 ViralLab Studio</h1>
  <p>Your AI-powered YouTube content workspace.</p>
  <p>Plan smarter. Create faster. Grow your channel.</p>
</div>
""", unsafe_allow_html=True)

st.caption("Powered by Groq for strategy and Pollinations for image generation.")

# Run generation only after the final form has submitted.
if st.session_state.generation_requested and not st.session_state.strategy:
    run_generation()

# -------------------- INPUT WIZARD --------------------

if not st.session_state.strategy:
    step = st.session_state.wizard_step
    question = QUESTIONS[step]
    key = question["key"]
    draft_key = "draft_" + key

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

    with st.form(f"wizard_form_{step}", clear_on_submit=False):
        if question.get("type") == "text":
            st.text_input(
                "Video topic",
                key=draft_key,
                placeholder="Enter your video topic...",
                label_visibility="collapsed",
            )
        else:
            options = question["options"]
            current = st.session_state.get(key, options[0])
            selected_index = options.index(current) if current in options else 0

            st.radio(
                question["title"],
                options,
                index=selected_index,
                key=draft_key,
                label_visibility="collapsed",
            )

        if key == "thumbnail_style":
            st.text_input(
                "Optional thumbnail details",
                key="draft_extra_details",
                placeholder="e.g. dramatic lighting, blue background",
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
            button_label = (
                "✨ Generate My Content"
                if step == len(QUESTIONS) - 1
                else "Next →"
            )
            st.form_submit_button(
                button_label,
                type="primary",
                use_container_width=True,
                on_click=save_and_next,
                args=(step,),
            )

    if st.session_state.error:
        st.error(st.session_state.error)

# -------------------- RESULTS --------------------

else:
    if st.session_state.error:
        st.warning(st.session_state.error)

    st.success("Your strategy has been generated.")

    # Always create a usable result list.
    sections = st.session_state.sections
    if not sections:
        sections = {"COMPLETE STRATEGY": st.session_state.strategy}
        st.session_state.sections = sections

    section_names = list(sections.keys())
    idx = max(0, min(st.session_state.result_index, len(section_names) - 1))
    title = section_names[idx]
    body = sections.get(title, "").strip()

    st.progress((idx + 1) / len(section_names))
    st.caption(f"RESULT SECTION {idx + 1} OF {len(section_names)}")

    st.markdown(
        f'<div class="motion-card">'
        f'<div class="step-label">YOUR AI RESULTS</div>'
        f'<div class="big-question">{html.escape(title.title())}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # If a parsed section is empty, show the full strategy instead.
    if not body:
        body = st.session_state.strategy

    # Ideas and titles can be viewed one at a time.
    if title in ("FIVE VIDEO IDEAS", "FIVE CLICKABLE TITLES"):
        items = split_items(body)

        if items:
            item_index = max(
                0,
                min(st.session_state.item_indices.get(title, 0), len(items) - 1),
            )

            st.progress((item_index + 1) / len(items))
            st.caption(f"ITEM {item_index + 1} OF {len(items)}")

            st.markdown('<div class="motion-card">', unsafe_allow_html=True)
            st.markdown(f"### {item_index + 1}")
            st.markdown(items[item_index])
            st.markdown('</div>', unsafe_allow_html=True)

            item_left, item_right = st.columns(2)

            with item_left:
                if item_index > 0:
                    st.button(
                        "← Previous item",
                        key=f"prev_item_{title}_{item_index}",
                        use_container_width=True,
                        on_click=go_to_item,
                        args=(title, item_index - 1),
                    )

            with item_right:
                if item_index < len(items) - 1:
                    st.button(
                        "Next item →",
                        key=f"next_item_{title}_{item_index}",
                        type="primary",
                        use_container_width=True,
                        on_click=go_to_item,
                        args=(title, item_index + 1),
                    )

            # Full list remains accessible even if the AI formatting differs.
            with st.expander("View all items in this section"):

