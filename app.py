
import re
import requests
import streamlit as st
from groq import Groq

# -------------------- APP CONFIG --------------------

st.set_page_config(
    page_title="ViralLab | YouTube Growth Studio",
    page_icon="🚀",
    layout="wide",
)

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #25283b, #161b2a);
        border: 1px solid #3b4056;
        margin-bottom: 1.5rem;
    }
    .muted {
        color: #aab0c2;
    }
    div[data-testid="stExpander"] {
        border-radius: 12px;
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

# -------------------- AI PROMPTS --------------------

def make_strategy_prompt(topic, niche, audience, style, language):
    headings = "\n".join(SECTIONS)

    return f"""
You are ViralLab, an expert YouTube content strategist.

Create a practical, specific YouTube content plan.

NICHE: {niche}
VIDEO TOPIC: {topic}
TARGET AUDIENCE: {audience}
VIDEO STYLE: {style}
OUTPUT LANGUAGE: {language}

IMPORTANT RULES:
- Write the actual content in {language}.
- Use the following nine headings EXACTLY as written below.
- Put each heading on its own line.
- Do not number or rename the headings.
- Do not repeat the same idea in multiple sections.
- Give exactly five distinct video ideas.
- Give exactly five distinct clickable titles.
- Make the script natural, engaging and suitable for the target audience.
- Include a strong opening hook and a clear ending in the script.
- Make the SEO description and hashtags relevant to the topic.
- Make the growth plan practical for a small or new creator.
- Never invent product specifications, prices, statistics or test results.
- Keep the thumbnail concept visual and suitable for a 16:9 image.
- Use Markdown formatting under each heading.
- Do not put the complete answer inside a code block.

Use these headings in this exact order:

{headings}
""".strip()


def split_strategy(text):
    """Split the generated strategy into its nine named sections."""
    found = []

    for title in SECTIONS:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?"
            r"(?:\d+[\.\):\-]\s*)?"
            + re.escape(title)
            + r"\s*:?\s*$"
        )

        match = pattern.search(text)

        if match:
            found.append((match.start(), match.end(), title))

    found.sort(key=lambda item: item[0])
    result = {}

    for index, (_, end, title) in enumerate(found):
        next_start = (
            found[index + 1][0]
            if index + 1 < len(found)
            else len(text)
        )

        result[title] = text[end:next_start].strip()

    return result


def make_thumbnail_prompt(topic, niche, audience, concept, style, extra):
    style_descriptions = {
        "Bold YouTube creator style":
            "bold composition, dramatic lighting, vibrant contrast",
        "Photorealistic tech review":
            "photorealistic products, realistic materials, studio lighting",
        "Minimal and professional":
            "minimal composition, clean background, elegant lighting",
        "Gaming and entertainment":
            "dynamic gaming atmosphere, cinematic lighting, energetic colors",
        "Educational and documentary":
            "clear visual storytelling, cinematic photography, thoughtful composition",
    }

    visual_style = style_descriptions.get(
        style, style_descriptions["Bold YouTube creator style"]
    )

    details = f" Additional visual direction: {extra}." if extra.strip() else ""

    return f"""
Create a professional 16:9 YouTube thumbnail image.

Video topic: {topic}
Content niche: {niche}
Target audience: {audience}
Thumbnail concept: {concept}

Visual direction: {visual_style}.
Create one clear focal subject, strong contrast, balanced composition,
good visual hierarchy and space for a title to be added later.
No text, no letters, no logos, no watermarks.
The image must communicate the topic clearly at small thumbnail size.
{details}
""".strip()


def generate_thumbnail(prompt, api_key):
    """Generate an image through the Pollinations image API."""
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
        raise ValueError(
            "The image service did not return an image. "
            "Check your Pollinations account and API response."
        )

    if "png" in content_type:
        extension = "png"
        mime_type = "image/png"
    elif "webp" in content_type:
        extension = "webp"
        mime_type = "image/webp"
    else:
        extension = "jpg"
        mime_type = "image/jpeg"

    return response.content, extension, mime_type


# -------------------- SESSION STATE --------------------

for key, default in {
    "strategy": "",
    "sections": {},
    "thumbnail": None,
    "thumbnail_ext": "jpg",
    "thumbnail_mime": "image/jpeg",
    "last_topic": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
    <h1>🚀 ViralLab Studio</h1>
    <p>Your AI-powered YouTube content workspace.</p>
    <p class="muted">
        Plan videos, write scripts, improve discoverability
        and generate thumbnail concepts in one workflow.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption("Powered by Groq for strategy and Pollinations for image generation.")

# -------------------- INPUT FORM --------------------

with st.form("viral_lab_form"):
    st.subheader("🎯 Plan your next video")

    col1, col2 = st.columns(2)

    with col1:
        niche = st.selectbox(
            "Content niche",
            [
                "Gaming",
                "Technology",
                "Education",
                "Entertainment",
                "Lifestyle",
                "Finance",
                "Fitness",
                "Travel",
                "Food",
                "Other",
            ],
        )

        topic = st.text_input(
            "Video topic",
            placeholder="e.g. Best budget gaming phones in 2026",
        )

        audience = st.text_input(
            "Target audience",
            value="Indian students and casual viewers",
        )

    with col2:
        style = st.selectbox(
            "Video style",
            [
                "Informative",
                "Tutorial",
                "Comparison",
                "Review",
                "Listicle",
                "Storytelling",
                "Entertainment",
            ],
        )

        language = st.selectbox(
            "Content language",
            [
                "English",
                "Hindi",
                "Hinglish",
                "Bengali",
                "Punjabi",
            ],
        )

        thumbnail_style = st.selectbox(
            "Thumbnail visual style",
            [
                "Bold YouTube creator style",
                "Photorealistic tech review",
                "Minimal and professional",
                "Gaming and entertainment",
                "Educational and documentary",
            ],
        )

    extra_details = st.text_input(
        "Optional thumbnail details",
        placeholder="e.g. red and blue lighting, smartphone, dark background",
    )

    submitted = st.form_submit_button(
        "✨ Generate Strategy + Thumbnail",
        type="primary",
        use_container_width=True,
    )


# -------------------- GENERATION WORKFLOW --------------------

if submitted:
    if not topic.strip():
        st.error("Please enter a video topic first.")
        st.stop()

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    pollinations_key = st.secrets.get("POLLINATIONS_API_KEY", "")

    if not groq_key:
        st.error("GROQ_API_KEY is missing from Streamlit Secrets.")
        st.stop()

    st.session_state.strategy = ""
    st.session_state.sections = {}
    st.session_state.thumbnail = None
    st.session_state.last_topic = topic.strip()

    with st.spinner("🧠 Creating your YouTube strategy..."):
        try:
            client = Groq(api_key=groq_key)

            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise YouTube growth strategist. "
                            "Follow all requested headings and formatting rules."
                        ),
                    },
                    {
                        "role": "user",
                        "content": make_strategy_prompt(
                            topic.strip(),
                            niche,
                            audience.strip(),
                            style,
                            language,
                        ),
                    },
                ],
                temperature=0.6,
                max_completion_tokens=5000,
            )

            strategy = completion.choices[0].message.content or ""

            if not strategy.strip():
                st.error("The AI returned an empty strategy. Please try again.")
                st.stop()

            st.session_state.strategy = strategy
            st.session_state.sections = split_strategy(strategy)

        except Exception as exc:
            st.error(f"Strategy generation failed: {exc}")
            st.stop()

    st.success("Your strategy is ready!")

    if pollinations_key:
        concept = st.session_state.sections.get(
            "THUMBNAIL CONCEPT",
            f"A compelling visual for a YouTube video about {topic}.",
        )

        image_prompt = make_thumbnail_prompt(
            topic.strip(),
            niche,
            audience.strip(),
            concept,
            thumbnail_style,
            extra_details,
        )

        with st.spinner("🎨 Creating your thumbnail... This may take a while."):
            try:
                image_bytes, extension, mime_type = generate_thumbnail(
                    image_prompt,
                    pollinations_key,
                )

                st.session_state.thumbnail = image_bytes
                st.session_state.thumbnail_ext = extension
                st.session_state.thumbnail_mime = mime_type

                st.success("Your thumbnail is ready!")

            except requests.RequestException as exc:
                st.warning(
                    "Your strategy is ready, but thumbnail generation "
                    f"failed because of a network or API error: {exc}"
                )
            except Exception as exc:
                st.warning(
                    "Your strategy is ready, but the thumbnail could not "
                    f"be generated: {exc}"
                )
    else:
        st.warning(
            "Your strategy is ready. Add POLLINATIONS_API_KEY to "
            "Streamlit Secrets to enable automatic thumbnail generation."
        )


# -------------------- RESULTS DASHBOARD --------------------

if st.session_state.strategy:
    st.divider()
    st.header("✨ Your AI-Generated Strategy")
    st.caption(
        "Explore each section below. Download individual sections "
        "or the complete strategy."
    )

    st.download_button(
        "📥 Download Complete Strategy",
        data=st.session_state.strategy,
        file_name="ViralLab_YouTube_Strategy.md",
        mime="text/markdown",
        use_container_width=True,
    )

    sections = st.session_state.sections

    if len(sections) < len(SECTIONS):
        st.info(
            "Some section headings were not detected. "
            "The complete strategy is still available below."
        )

    for title in SECTIONS:
        body = sections.get(title)

        if not body:
            continue

        with st.expander(title.title(), expanded=False):
            st.markdown(body)

            st.download_button(
                f"📥 Download {title.title()}",
                data=body,
                file_name=title.lower().replace(" ", "_") + ".md",
                mime="text/markdown",
                key=f"download_{title}",
            )

    with st.expander("📄 View complete strategy"):
        st.markdown(st.session_state.strategy)

    # -------------------- THUMBNAIL --------------------

    st.divider()
    st.header("🎨 AI Thumbnail")

    if st.session_state.thumbnail:
        st.image(
            st.session_state.thumbnail,
            caption="Your generated YouTube thumbnail",
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download Thumbnail",
            data=st.session_state.thumbnail,
            file_name=(
                "ViralLab_Thumbnail."
                + st.session_state.thumbnail_ext
            ),
            mime=st.session_state.thumbnail_mime,
            use_container_width=True,
        )

    else:
        st.info(
            "No thumbnail is available for this generation. "
            "Your strategy is safe. Check the Pollinations API key, "
            "account balance and usage limits before trying again."
        )

st.divider()
st.caption(
    "ViralLab uses AI-generated content. Verify product specifications, "
    "prices, statistics and other factual claims before publishing."
        )
