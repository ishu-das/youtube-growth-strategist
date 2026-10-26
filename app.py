
import streamlit as st
from groq import Groq
from groq import APIStatusError, APIConnectionError

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
</style>
""", unsafe_allow_html=True)

st.title("🎬 ViralLab")
st.subheader("Your AI YouTube Growth Strategist")
st.write(
    "Create custom video ideas, titles, thumbnail concepts, "
    "scripts, SEO descriptions, and growth strategies."
)

st.divider()

left, right = st.columns(2)

with left:
    niche = st.text_input(
        "Channel niche",
        placeholder="e.g. Technology, Gaming, Education"
    )
    topic = st.text_input(
        "Video topic",
        placeholder="e.g. Best budget gaming phones"
    )

with right:
    audience = st.text_input(
        "Target audience",
        placeholder="e.g. Indian students and gamers"
    )
    style = st.selectbox(
        "Video style",
        ["Educational", "Entertainment", "Tutorial",
         "Review", "Storytelling"]
    )

language = st.selectbox(
    "Output language",
    ["English", "Hindi", "Hinglish"]
)

if st.button("🚀 Generate My AI Strategy"):
    if not topic.strip():
        st.warning("Enter a video topic first.")
    else:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=api_key)

            prompt = f"""

You are an expert YouTube content strategist.

Create a practical strategy for this video.

Channel niche: {niche.strip() or "General"}
Topic: {topic.strip()}
Target audience: {audience.strip() or "General viewers"}
Video style: {style}
Language: {language}

FORMATTING RULES:
- Use the nine exact headings below, each on its own line.
- Keep headings in English even if the content is Hindi or Hinglish.
- Do not add numbering to the headings.
- Do not use a table for video ideas.
- Never invent current prices, product specifications, or statistics.
- Mark facts that need verification.

CONTENT ANGLE
Explain the viewer's problem and the video's unique value.

FIVE VIDEO IDEAS
Give five distinct ideas with short explanations.

FIVE CLICKABLE TITLES
Write five compelling but honest titles.

THUMBNAIL CONCEPT
Describe the visual, composition, colors, and 2-4 words of text.

OPENING HOOK
Write an engaging opening of approximately 15 seconds.

COMPLETE VIDEO SCRIPT
Write a complete, natural script with an introduction, main points,
examples, transitions, conclusion, and call to action.

SEO DESCRIPTION
Write a ready-to-use YouTube description.

KEYWORDS AND HASHTAGS
Suggest relevant search phrases and hashtags.

GROWTH PLAN
Give five practical recommendations for this video.

"""

            with st.spinner(
                "Groq is generating your YouTube strategy..."
            ):
                result = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful, creative, "
                                "practical YouTube strategist."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_completion_tokens=5000
                )

            strategy = result.choices[0].message.content

            if strategy:
                st.session_state["strategy"] = strategy
                st.success("Your AI strategy is ready!")
            else:
                st.error("The AI returned an empty response.")

        except KeyError:
            st.error(
                "API key missing. Add GROQ_API_KEY in "
                "Streamlit app Secrets settings."
            )
        except APIStatusError as error:
            if error.status_code == 429:
                st.error(
                    "The API rate limit or usage quota was reached. "
                    "Check your Groq Console limits and try later."
                )
            elif error.status_code in (401, 403):
                st.error(
                    "The API key is invalid or does not have access. "
                    "Check your Groq key and account."
                )
            elif error.status_code == 404:
                st.error(
                    "The selected model may be unavailable. "
                    "Check the active models in Groq Console."
                )
            else:
                st.error(
                    f"Groq returned an API error "
                    f"(HTTP {error.status_code}). Check the app logs."
                )
        except APIConnectionError:
            st.error(
                "Could not connect to Groq. Check the connection "
                "and try again."
            )
        except Exception as error:
            st.error(
                f"Unexpected error: {type(error).__name__}. "
                "Check Manage app → Logs."
            )

if "strategy" in st.session_state:
    st.divider()
    st.header("✨ Your AI-Generated Strategy")

    strategy = st.session_state["strategy"]

    st.download_button(
        "📥 Download Full Strategy",
        data=strategy,
        file_name="virallab_strategy.md",
        mime="text/markdown",
        key="download_full_strategy"
    )

    st.caption("Copy any section below with one tap.")

sections = [
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

import re

found = []
for i, heading in enumerate(sections):
    pattern = re.compile(
        r"(?im)^\s*(?:#+\s*)?(?:\d+\.\s*)?"
        + re.escape(heading)
        + r"\s*:?\s*$"
    )
    match = pattern.search(strategy)
    if match:
        found.append((match.start(), heading, match.end()))
        
    if not found:
        st.markdown(strategy)
        st.info(
            "The AI used different headings this time. "
            "You can still download the full strategy above."
        )
    else:
        found.sort(key=lambda item: item[0])

        for i, (start, heading, body_start) in enumerate(found):
            end = (
                found[i + 1][0]
                if i + 1 < len(found)
                else len(strategy)
            )
            content = strategy[body_start:end].strip()

            with st.expander(heading, expanded=(i == 0)):
                st.markdown(content or "_No content in this section._")

                st.text_area(
                    "Copyable text",
                    value=content,
                    height=180,
                    key=f"copy_text_{i}"
                )

                st.caption(
                    "Tap inside the text, then use Select all → Copy."
                )

    st.divider()
    st.success("Strategy saved in this session.")
    
