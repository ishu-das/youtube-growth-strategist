
import streamlit as st

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
st.subheader("Your YouTube Growth Strategist")
st.write("Generate video ideas, clickable titles, thumbnail tips, and a script outline.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    niche = st.text_input(
        "Channel niche",
        placeholder="e.g. Gaming, Tech, Education"
    )
    topic = st.text_input(
        "Video topic",
        placeholder="e.g. Best budget gaming phones"
    )

with col2:
    audience = st.text_input(
        "Target audience",
        placeholder="e.g. Beginners, students, gamers"
    )
    style = st.selectbox(
        "Video style",
        ["Educational", "Entertainment", "Tutorial", "Review", "Storytelling"]
    )

if st.button("🚀 Generate My Strategy"):
    niche = niche.strip() or "General"
    topic = topic.strip() or "your next video"
    audience = audience.strip() or "beginners"

    st.success("Your content strategy is ready!")

    st.header("💡 Video Ideas")
    ideas = [
        f"5 Mistakes People Make About {topic}",
        f"I Tried {topic}: Here's What I Learned",
        f"The Beginner's Guide to {topic}",
        f"{topic}: What I Wish I Knew Earlier",
        f"The Truth About {topic}"
    ]

    for i, idea in enumerate(ideas, 1):
        st.write(f"**{i}.** {idea}")

    st.header("🔥 Clickable Title Ideas")
    titles = [
        f"{topic}: What Nobody Tells You",
        f"Stop Making These {topic} Mistakes",
        f"I Tested {topic} So You Don't Have To"
    ]

    for title in titles:
        st.write(f"📌 {title}")

    st.header("🖼️ Thumbnail Strategy")
    st.write(
        "Use one clear subject, strong contrast, an expressive face "
        "or relevant object, and 2–4 large readable words. "
        "Make sure the thumbnail honestly represents the video."
    )

    st.header("📝 Video Script Outline")
    st.markdown(f"""
**Video style:** {style}

**1. Hook (first 5–10 seconds)**  
Ask a surprising question or show an interesting result related to **{topic}**.

**2. Introduction**  
Tell viewers what they will learn and why it matters to them.

**3. Main content**  
Explain three useful points about **{topic}** for **{audience}**.

**4. Payoff**  
Summarize the most useful lesson or demonstrate the result.

**5. Call to action**  
Invite viewers to comment with their experience and subscribe if they found the video useful.
""")

    st.header("📈 Growth Tips")
    st.write(f"""
- **Niche:** {niche}
- **Audience:** {audience}
- Make the opening interesting immediately.
- Deliver on the promise made by your title.
- Review audience retention and click-through rate after publishing.
""")

    st.caption(
        "Note: This version uses templates, not a live AI model. "
        "Real AI-generated strategies require an AI API integration."
    )
    
