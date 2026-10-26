

import re
import requests
import streamlit as st
from groq import Groq

# =====================================================
# VIRALLAB STUDIO
# =====================================================

st.set_page_config(
    page_title="ViralLab Studio",
    page_icon="🚀",
    layout="centered",
)

# --------------------- DESIGN ---------------------

st.markdown("""
<style>
@keyframes enter {
    from {opacity:0; transform:translateY(14px);}
    to {opacity:1; transform:translateY(0);}
}
@keyframes movebg {
    0% {background-position:0% 50%}
    50% {background-position:100% 50%}
    100% {background-position:0% 50%}
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
.hero {
    padding: 1.5rem;
    border: 1px solid #7669ad;
    border-radius: 20px;
    background: linear-gradient(120deg,#17152b,#292044,#102c3a,#17152b);
    background-size: 300% 300%;
    animation: movebg 12s ease infinite;
    margin-bottom: 1.5rem;
}
.panel {
    padding: 1.2rem;
    border: 1px solid #62578b;
    border-radius: 17px;
    background: rgba(120,110,170,.07);
    animation: enter .4s ease both;
    margin: .7rem 0 1rem;
}
.step-label {
    color: #c4b5fd;
    font-size: .8rem;
    font-weight: 700;
    letter-spacing: .08em;
}
div[data-testid="stImage"] img {
    border-radius: 15px;
    animation: enter .5s ease both;
}
.stButton button, .stDownloadButton button {
    border-radius: 12px;
    transition: transform .2s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-2px);
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------- QUESTIONS ---------------------

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
        "key": "style",
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
        "help": "ViralLab will try to generate a thumbnail automatically.",
        "options": [
            "Bold YouTube creator style",
            "Photorealistic tech review",
            "Minimal and professional",
            "Gaming and entertainment",
            "Educational and documentary",
        ],
    },
]

SECTION_NAMES = [
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

DEFAULTS = {
    "step": 0,
    "niche": "Gaming",
    "topic": "",
    "audience": "Students",
    "style": "Informative",
    "language": "English",
    "thumbnail_style": "Bold YouTube creator style",
    "extra_details": "",
    "strategy": "",
    "sections": {},
    "result_index": 0,
    "item_index": 0,
    "thumbnail": None,
    "thumbnail_ext": "jpg",
    "thumbnail_mime": "image/jpeg",
    "error": "",
    "warning": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------- NAVIGATION ---------------------

def next_step(step):
    question = QUESTIONS[step]
    key = question["key"]
    value = st.session_state.get("draft_" + key, st.session_state[key])

    st.session_state.error = ""

    if key == "topic" and not str(value).strip():
        st.session_state.error = "Please enter your video topic before continuing."
        return

    st.session_state[key] = value

    if step == len(QUESTIONS) - 1:
        st.session_state.extra_details = st.session_state.get(
            "draft_extra_details", ""
        )
        generate_content()
    else:
        st.session_state.step = step + 1


def previous_step(step):
    question = QUESTIONS[step]
    key = question["key"]

    st.session_state[key] = st.session_state.get(
        "draft_" + key, st.session_state[key]
    )
    st.session_state.error = ""
    st.session_state.step = max(0, step - 1)


def new_project():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def go_result(index):
    st.session_state.result_index = index
    st.session_state.item_index = 0


# --------------------- AI PROMPT ---------------------

def build_prompt():
    headings = "\n".join(SECTION_NAMES)

    return f"""
You are ViralLab, an expert YouTube growth strategist.

NICHE: {st.session_state.niche}
TOPIC: {st.session_state.topic}
TARGET AUDIENCE: {st.session_state.audience}
VIDEO STYLE: {st.session_state.style}
LANGUAGE: {st.session_state.language}

Create a useful, specific YouTube strategy.

Use these exact headings, each on its own line:
{headings}

Rules:
- Write in the selected language.
- Give exactly five different video ideas.
- Give exactly five different clickable titles.
- Make the opening hook compelling.
- Write a complete natural video script with an ending.
- Include a useful SEO description, keywords and hashtags.
- Include a realistic growth plan.
- Describe a visual thumbnail concept.
- Do not invent product specifications, prices or statistics.
- Use Markdown formatting.
- Do not put the whole response inside a code block.
- Do not repeat the same idea across sections.
""".strip()


def parse_sections(text):
    matches = []

    for name in SECTION_NAMES:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?(?:\d+[\.\):\-]\s*)?"
            + re.escape(name)
            + r"\s*:?\s*$"
        )
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), name))

    matches.sort(key=lambda item: item[0])
    result = {}

    for index, (start, end, name) in enumerate(matches):
        if name in result:
            continue

        next_start = (
            matches[index + 1][0]
            if index + 1 < len(matches)
            else len(text)
        )
        body = text[end:next_start].strip()

        if body:
            result[name] = body

    return result


def parse_items(text):
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


# --------------------- THUMBNAIL ---------------------

def image_prompt():
    concept = st.session_state.sections.get(
        "THUMBNAIL CONCEPT",
        "Create a striking visual about " + st.session_state.topic,
    )

    style_map = {
        "Bold YouTube creator style": "bold colors, strong contrast, dramatic lighting",
        "Photorealistic tech review": "photorealistic product photography, studio lighting",
        "Minimal and professional": "clean minimal design, elegant lighting",
        "Gaming and entertainment": "cinematic gaming atmosphere, dynamic composition",
        "Educational and documentary": "cinematic documentary photography",
    }

    extra = st.session_state.extra_details.strip()

    return f"""
Create a professional 16:9 YouTube thumbnail image.
Topic: {st.session_state.topic}
Niche: {st.session_state.niche}
Concept: {concept}
Visual style: {style_map.get(st.session_state.thumbnail_style, "cinematic lighting")}.
Use one clear focal subject and strong contrast.
Leave space for a title to be added later.
Do not render text, logos or watermarks.
Additional direction: {extra}
""".strip()


def generate_thumbnail(api_key):
    url = (
        "https://gen.pollinations.ai/image/"
        + requests.utils.quote(image_prompt(), safe="")
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
        ext, mime = "png", "image/png"
    elif "webp" in content_type:
        ext, mime = "webp", "image/webp"
    else:
        ext, mime = "jpg", "image/jpeg"

    return response.content, ext, mime


# --------------------- GENERATION ---------------------

def generate_content():
    topic = str(st.session_state.topic).strip()

    if not topic:
        st.session_state.error = "Your video topic is missing. Return to Step 2."
        st.session_state.step = 1
        return

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    pollinations_key = st.secrets.get("POLLINATIONS_API_KEY", "")

    if not groq_key:
        st.session_state.error = (
            "GROQ_API_KEY is missing. Add it under Streamlit Settings > Secrets."
        )
        return

    # Clear old results before starting a new generation.
    st.session_state.strategy = ""
    st.session_state.sections = {}
    st.session_state.result_index = 0
    st.session_state.item_index = 0
    st.session_state.thumbnail = None
    st.session_state.warning = ""

    try:
        with st.spinner("🧠 Creating your YouTube strategy..."):
            client = Groq(api_key=groq_key)

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise YouTube growth strategist.",
                    },
                    {"role": "user", "content": build_prompt()},
                ],
                temperature=0.6,
                max_completion_tokens=5000,
            )

            strategy = response.choices[0].message.content or ""

            if not strategy.strip():
                raise ValueError("The AI returned an empty response.")

            # Always save the complete response before parsing it.
            st.session_state.strategy = strategy
            parsed = parse_sections(strategy)

            if parsed:
                st.session_state.sections = parsed
            else:
                st.session_state.sections = {"COMPLETE STRATEGY": strategy}

    except Exception as exc:
        st.session_state.error = (
            "Strategy generation failed. Check the Groq API key, model "
            "availability, internet connection and usage limits. "
            f"Details: {str(exc)[:250]}"
        )
        return

    # Image generation is independent. Its failure cannot erase the strategy.
    if pollinations_key:
        try:
            with st.spinner("🎨 Generating your thumbnail..."):
                image, ext, mime = generate_thumbnail(pollinations_key)
                st.session_state.thumbnail = image
                st.session_state.thumbnail_ext = ext
                st.session_state.thumbnail_mime = mime
        except Exception as exc:
            st.session_state.warning = (
                "The strategy is ready, but thumbnail generation failed. "
                "Check your Pollinations key, account usage and model availability. "
                f"Details: {str(exc)[:180]}"
            )
    else:
        st.session_state.warning = (
            "Strategy generated. Add POLLINATIONS_API_KEY in Streamlit Secrets "
            "to enable automatic thumbnail generation."
        )


# --------------------- HEADER ---------------------

st.markdown("""
<div class="hero">
<h1>🚀 ViralLab Studio</h1>
<p>Your AI-powered YouTube content workspace.</p>
<p>Plan smarter. Create faster. Grow your channel.</p>
</div>
""", unsafe_allow_html=True)

st.caption("Powered by Groq for strategy and Pollinations for image generation.")

# --------------------- WIZARD ---------------------

if not st.session_state.strategy:
    step = st.session_state.step
    question = QUESTIONS[step]
    key = question["key"]
    draft_key = "draft_" + key

    st.progress((step + 1) / len(QUESTIONS))
    st.caption(f"STEP {step + 1} OF {len(QUESTIONS)}")

    st.markdown(
        f'<div class="panel">'
        f'<div class="step-label">YOUR CONTENT JOURNEY</div>'
        f'<h2>{question["title"]}</h2>'
        f'<p>{question["help"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.form(f"question_form_{step}", clear_on_submit=False):
        if question.get("type") == "text":
            st.text_input(
                "Video topic",
                key=draft_key,
                placeholder="Enter your video topic...",
                label_visibility="collapsed",
            )
        else:
            options = question["options"]
            current = st.session_state[key]
            index = options.index(current) if current in options else 0

            st.radio(
                question["title"],
                options,
                index=index,
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
                    on_click=previous_step,
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
                on_click=next_step,
                args=(step,),
            )

    if st.session_state.error:
        st.error(st.session_state.error)

# --------------------- RESULTS ---------------------

else:
    if st.session_state.error:
        st.error(st.session_state.error)

    if st.session_state.warning:
        st.warning(st.session_state.warning)

    st.success("Your strategy is ready!")

    # Fallback prevents an empty results screen.
    if not st.session_state.sections:
        st.session_state.sections = {
            "COMPLETE STRATEGY": st.session_state.strategy
        }

    names = list(st.session_state.sections.keys())
    idx = max(0, min(st.session_state.result_index, len(names) - 1))
    title = names[idx]
    body = st.session_state.sections.get(title, "").strip()

    if not body:
        body = st.session_state.strategy

    st.progress((idx + 1) / len(names))
    st.caption(f"RESULT SECTION {idx + 1} OF {len(names)}")

    st.markdown(
        f'<div class="panel">'
        f'<div class="step-label">YOUR AI RESULTS</div>'
        f'<h2>{title.title()}</h2>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Ideas and titles can be browsed individually.
    if title in ("FIVE VIDEO IDEAS", "FIVE CLICKABLE TITLES"):
        items = parse_items(body)

        if items:
            item_idx = max(0, min(st.session_state.item_index, len(items) - 1))

            st.caption(f"ITEM {item_idx + 1} OF {len(items)}")
            st.progress((item_idx + 1) / len(items))

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown(f"### {item_idx + 1}")
            st.markdown(items[item_idx])
            st.markdown('</div>', unsafe_allow_html=True)

            item_left, item_right = st.columns(2)

            with item_left:
                if item_idx > 0:
                    st.button(
                        "← Previous item",
                        key=f"previous_item_{idx}_{item_idx}",
                        use_container_width=True,
                        on_click=lambda: setattr(
                            st.session_state, "item_index", item_idx - 1
                        ),
                    )

            with item_right:
                if item_idx < len(items) - 1:
                    st.button(
                        "Next item →",
                        key=f"next_item_{idx}_{item_idx}",
                        type="primary",
                        use_container_width=True,
                        on_click=lambda: setattr(
                            st.session_state, "item_index", item_idx + 1
                        ),
                    )

            with st.expander("View all items"):
                st.markdown(body)
        else:
            st.markdown(body)
    else:
        st.markdown(body)

    st.download_button(
        "📥 Download This Section",
        data=body,
        file_name=title.lower().replace(" ", "_") + ".md",
        mime="text/markdown",
        key=f"section_download_{idx}",
        use_container_width=True,
    )

    st.divider()
    previous, following = st.columns(2)

    with previous:
        if idx > 0:
            st.button(
                "← Previous section",
                use_container_width=True,
                on_click=go_result,
                args=(idx - 1,),
            )

    with following:
        if idx < len(names) - 1:
            st.button(
                "Next section →",
                type="primary",
                use_container_width=True,
                on_click=go_result,
                args=(idx + 1,),
            )
        else:
            st.success("You've reached the end of your strategy.")

    with st.expander("📄 View complete strategy"):
        st.markdown(st.session_state.strategy)

    st.download_button(
        "📥 Download Complete Strategy",
        data=st.session_state.strategy,
        file_name="ViralLab_Complete_Strategy.md",
        mime="text/markdown",
        use_container_width=True,
    )

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
            "No thumbnail is available for this run. "
            "Your strategy is still available above."
        )

    st.button(
        "🔄 Start a New Project",
        use_container_width=True,
        on_click=new_project,
    )

st.divider()
st.caption(
    "ViralLab uses AI-generated content. Verify factual claims before publishing."
)
