
st.markdown("""
<style>
/* ---------- VIRALLAB MOTION SYSTEM ---------- */

:root {
    --accent: #8b5cf6;
    --accent-blue: #38bdf8;
    --glass: rgba(255, 255, 255, 0.045);
    --glass-border: rgba(255, 255, 255, 0.12);
}

/* Main page entrance */
@keyframes pageReveal {
    from {
        opacity: 0;
        transform: translateY(18px);
        filter: blur(4px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }
}

/* Animated hero background */
@keyframes gradientFlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Soft glowing accent */
@keyframes glowPulse {
    0%, 100% {
        box-shadow: 0 0 16px rgba(139, 92, 246, 0.08);
    }
    50% {
        box-shadow: 0 0 28px rgba(56, 189, 248, 0.19);
    }
}

/* Smooth content entrance */
@keyframes contentReveal {
    from {
        opacity: 0;
        transform: translateY(12px) scale(0.99);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Main layout */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
    animation: pageReveal 0.65s ease-out both;
}

/* Hero section */
.hero {
    position: relative;
    overflow: hidden;
    padding: 1.8rem;
    border-radius: 22px;
    border: 1px solid rgba(167, 139, 250, 0.28);
    background: linear-gradient(
        125deg,
        #17182c,
        #252044,
        #102a3b,
        #17182c
    );
    background-size: 300% 300%;
    animation: gradientFlow 12s ease infinite,
               glowPulse 5s ease-in-out infinite;
    margin-bottom: 1.5rem;
    transition: border-color 0.3s ease;
}

.hero:hover {
    border-color: rgba(56, 189, 248, 0.6);
}

.hero h1 {
    letter-spacing: -0.04em;
    animation: contentReveal 0.8s ease-out both;
}

.hero p {
    animation: contentReveal 0.8s ease-out 0.12s both;
}

/* Expander cards */
div[data-testid="stExpander"] {
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    background: var(--glass);
    overflow: hidden;
    transition:
        border-color 0.3s ease,
        box-shadow 0.3s ease,
        transform 0.3s ease;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(139, 92, 246, 0.55);
    box-shadow: 0 5px 24px rgba(139, 92, 246, 0.08);
}

/* Animate content when a section opens */
div[data-testid="stExpander"] details[open]
div[data-testid="stExpanderDetails"] {
    animation: contentReveal 0.38s ease-out both;
    transform-origin: top center;
}

/* Buttons */
.stButton button,
.stDownloadButton button,
button[kind="primaryFormSubmit"] {
    border-radius: 12px;
    transition:
        transform 0.22s ease,
        box-shadow 0.22s ease,
        border-color 0.22s ease;
}

.stButton button:hover,
.stDownloadButton button:hover,
button[kind="primaryFormSubmit"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 22px rgba(139, 92, 246, 0.2);
}

/* Input controls */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 11px;
    transition: box-shadow 0.25s ease;
}

.stTextInput input:focus {
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25);
}

/* Generated thumbnail */
div[data-testid="stImage"] img {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    animation: contentReveal 0.7s ease-out both;
    transition:
        transform 0.35s ease,
        box-shadow 0.35s ease;
}

div[data-testid="stImage"] img:hover {
    transform: scale(1.012);
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.25);
}

/* Download and result areas */
div[data-testid="stDownloadButton"] {
    transition: transform 0.25s ease;
}

div[data-testid="stDownloadButton"]:hover {
    transform: translateY(-1px);
}

/* Subtle separators */
hr {
    border-color: rgba(255, 255, 255, 0.10);
    margin-top: 1.8rem;
    margin-bottom: 1.8rem;
}

/* Accessibility: respect reduced-motion preferences */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
</style>
""", unsafe_allow_html=True)
