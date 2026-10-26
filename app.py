
import re
import requests
import streamlit as st
from groq import Groq
from requests.exceptions import RequestException

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="ViralLab | YouTube Growth Strategist",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0e1117;
    color: #f5f5f5;
}
h1 {
    color: #ff4b5c;
}
.stButton > button {
    background: #ff4b5c;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    width: 100%;
}
div[data-testid="stExpander"] {
    border: 1px solid #343844;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

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


def split_strategy(text):
    """Split AI output using tolerant heading matching."""
    found = []

    for heading in SECTIONS:
        pattern = re.compile(
            r"(?im)^\s*(?:#{1,6}\s*)?(?:\d+[\.\)]\s*)?"
            + re.escape(heading)
            + r"\s*:?\s*$"
        )
        match = pattern.search(text)

        if match:
            found.append(
                (match.start(), heading, match.end())
            )

    found.sort(key=lambda item: item[0])

    # Ignore duplicate or out-of-order heading matches.
    unique = []
    seen = set()

    for item in found:
        if item[1] not in seen:
            unique.append(item)
            seen.add(item[1])

    result = []

    for i, (start, heading, body_start) in enumerate(unique):
        end = (
            unique[i + 1][0]
            if i + 1 < len(unique)
            else len(text)
        )
        body = text[body_start:end].strip()
        result.append((heading, body))

    return result


def make_prompt(niche, topic, audience, style, language):
    return f"""
You are an expert YouTube strategist and scriptwriter.

Create a detailed, useful YouTube content plan.

CHANNEL NICHE: {niche}
VIDEO TOPIC: {topic}
TARGET AUDIENCE: {audience}
VIDEO STYLE: {style}
OUTPUT LANGUAGE: {language}

FORMATTING RULES:
- Use exactly the nine headings below, each on its own line.
- Keep the headings in English exactly as written.
- Do not number the headings.
- Write the rest of the content in the requested language.
- Make the script natural to speak aloud.
- Do not use tables.
- Do not invent current prices, specifications, release dates,
  benchmarks, or other facts.
- Mark unverified claims clearly and tell the creator to verify them.
- Do not claim that titles will definitely go viral or rank first.

CONTENT ANGLE
Explain the audience's problem and the video's unique value.

FIVE VIDEO IDEAS
Give five distinct ideas, each with a short explanation.

FIVE CLICKABLE TITLES
Give five interesting and honest title options.

THUMBNAIL CONCEPT
Describe the composition, main subject, colors, emotion,
background, and 2-4 words of thumbnail text.

OPENING HOOK
Write an engaging opening of approximately 15 seconds.

COMPLETE VIDEO SCRIPT
Write a complete script with an opening, introduction,
detailed main points, transitions, examples, conclusion,
and call to action. Use timestamps where appropriate.

SEO DESCRIPTION
Write a ready-to-use YouTube description with a natural CTA.

KEYWORDS AND HASHTAGS
Suggest relevant keywords and a concise set of hashtags.

GROWTH PLAN
Give five practical recommendations for improving the video.

Be specific, helpful, and ready for a creator to edit and publish.
"""


# --------------------------------------------------
# HEADER AND INPUTS
# --------------------------------------------------

st.title("🎬 ViralLab")
st.subheader("Your AI YouTube Growth Strategist")
st.write(
    "Plan videos, generate scripts, create thumbnail concepts, "
    "and build a practical publishing strategy."
)

with st.form("strategy_form"):
    col1, col2 = st.columns(2)

    with col1:
        niche = st.text_input(
            "Channel niche",
            placeholder="Technology, gaming, education..."
        )
        topic = st.text_input(
            "Video topic",
            placeholder="Best budget gaming phones"
        )

    with col2:
        audience = st.text_input(
            "Target audience",
            placeholder="Indian students and gamers"
        )
        style = st.selectbox(
            "Video style",
            [
                "Educational",
                "Entertainment",
                "Tutorial",
                "Review",
                "Storytelling"
            ]
        )

    language = st.selectbox(
        "Output language",
        ["English", "Hindi", "Hinglish"]
    )

    submitted = st.form_submit_button(
        "🚀 Generate My AI Strategy"
    )


# --------------------------------------------------
# GROQ AI TEXT GENERATION
# --------------------------------------------------

if submitted:
    if not topic.strip():
        st.warning("Please enter a video topic.")
    else:
        api_key = st.secrets.get("GROQ_API_KEY", "")

        if not api_key:
            st.error(
                "GROQ_API_KEY is missing. Add it in "
                "Streamlit app settings under Secrets."
            )
        else:
            prompt = make_prompt(
                niche.strip() or "General",
                topic.strip(),
                audience.strip() or "General viewers",
                style,
                language
            )

            try:
                client = Groq(api_key=api_key)

                with st.spinner(
                    "Groq is building your strategy..."
                ):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a practical, creative "
                                    "YouTube strategist. Follow the "
                                    "requested headings exactly."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.6,
                        max_completion_tokens=5000
                    )

                strategy = (
                    response.choices[0].message.content or ""
                ).strip()

                if strategy:
                    st.session_state["strategy"] = strategy
                    st.session_state["strategy_topic"] = topic.strip()
                    st.session_state["strategy_niche"] = (
                        niche.strip() or "General"
                    )
                    st.session_state.pop("thumbnail_bytes", None)
                    st.success("Your AI strategy is ready!")
                else:
                    st.error(
                        "The AI returned an empty response. Try again."
                    )

            except Exception as error:
                st.error(
                    "Groq could not generate the strategy. "
                    "Check your API key, model access, usage limits, "
                    "and Streamlit logs."
                )
                st.caption(
                    f"Technical error: {type(error).__name__}"
                )


# --------------------------------------------------
# DISPLAY THE GENERATED STRATEGY
# --------------------------------------------------

if "strategy" in st.session_state:
    strategy = st.session_state["strategy"]

    st.divider()
    st.header("✨ Your AI-Generated Strategy")

    st.download_button(
        "📥 Download Full Strategy",
        data=strategy,
        file_name="virallab_strategy.md",
        mime="text/markdown",
        key="download_strategy"
    )

    sections = split_strategy(strategy)

    if sections:
        st.caption(
            "Open any section. Use the copy icon in its text block "
            "to copy the content."
        )

        for index, (heading, body) in enumerate(sections):
            with st.expander(
                heading.title(),
                expanded=(index == 0)
            ):
                if body:
                    st.markdown(body)
                    st.code(body, language=None)
                else:
                    st.info("No content was returned for this section.")

        if len(sections) < len(SECTIONS):
            st.info(
                f"Recognized {len(sections)} of {len(SECTIONS)} "
                "sections. The full strategy is still available "
                "to download above."
            )
    else:
        st.warning(
            "The headings could not be separated. "
            "The complete strategy is shown below."
        )
        st.markdown(strategy)

    with st.expander("📄 View complete strategy"):
        st.markdown(strategy)

    # --------------------------------------------------
    # OPTIONAL ACTUAL THUMBNAIL IMAGE GENERATION
    # --------------------------------------------------

    st.divider()
    st.header("🖼️ Thumbnail Image Generator")

    st.write(
        "Create a 16:9 thumbnail image based on your video topic. "
        "Image generation requires a separate Pollinations API key."
    )

    thumbnail_style = st.selectbox(
        "Thumbnail visual style",
        [
            "Photorealistic tech review",
            "Gaming neon",
            "Minimal and premium",
            "Bold YouTube creator style",
            "Cinematic storytelling"
        ],
        key="thumbnail_style"
    )

    thumbnail_subject = st.text_input(
        "Extra thumbnail details (optional)",
        placeholder="A phone, dramatic lighting, blue background...",
        key="thumbnail_subject"
    )

    if st.button("🎨 Generate Thumbnail Image"):
        image_key = st.secrets.get(
            "POLLINATIONS_API_KEY", ""
        )

        if not image_key:
            st.warning(
                "Image generation is optional. To enable it, create "
                "a key at enter.pollinations.ai and add "
                "POLLINATIONS_API_KEY to Streamlit Secrets."
            )
        else:
            image_prompt = (
                "Create a polished 16:9 YouTube thumbnail image "
                "for the topic: "
                + st.session_state.get("strategy_topic", "YouTube video")
                + ". Channel niche: "
                + st.session_state.get("strategy_niche", "General")
                + ". Visual style: "
                + thumbnail_style
                + ". Extra details: "
                + (thumbnail_subject.strip() or "strong visual contrast")
                + ". One clear focal subject, strong composition, "
                "high contrast, professional lighting, crisp details. "
                "Leave clean space for a title to be added later. "
                "Avoid logos, watermarks, and tiny text."
            )

            try:
                with st.spinner(
                    "Generating the thumbnail image. This may take a while..."
                ):
                    image_response = requests.get(
                        "https://gen.pollinations.ai/image/"
                        + requests.utils.quote(image_prompt, safe=""),
                        params={
                            "model": "black-forest-labs/flux.2-klein-4b",
                            "width": 1280,
                            "height": 720
                        },
                        headers={
                            "Authorization": f"Bearer {image_key}"
                        },
                        timeout=180
                    )

                    image_response.raise_for_status()

                    content_type = image_response.headers.get(
                        "Content-Type", ""
                    )

                    if not content_type.startswith("image/"):
                        raise ValueError(
                            "The image service did not return an image."
                        )

                    image_bytes = image_response.content

                    if not image_bytes:
                        raise ValueError(
                            "The image service returned an empty file."
                        )

                    st.session_state["thumbnail_bytes"] = image_bytes

                st.success("Thumbnail image generated!")

            except RequestException as error:
                st.error(
                    "Image generation failed. Check the image API "
                    "key, available credits, model access, and connection."
                )
                st.caption(
                    f"Technical error: {type(error).__name__}"
                )
            except Exception as error:
                st.error(
                    "Could not process the generated image. "
                    "Check the API response and app logs."
                )
                st.caption(
                    f"Technical error: {type(error).__name__}"
                )

    if "thumbnail_bytes" in st.session_state:
        st.image(
            st.session_state["thumbnail_bytes"],
            caption="Your generated thumbnail concept",
            use_container_width=True
        )

        st.download_button(
            "⬇️ Download Thumbnail",
            data=st.session_state["thumbnail_bytes"],
            file_name="virallab_thumbnail.jpg",
            mime="image/jpeg",
            key="download_thumbnail"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "ViralLab uses Groq for text generation and optionally "
    "Pollinations for image generation. AI output may contain "
    "errors. Verify product specifications, prices, and current "
    "claims before publishing."
        )
