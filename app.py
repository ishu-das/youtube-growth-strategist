
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}

    niche = data.get("niche", "your niche").strip()
    topic = data.get("topic", "your next video").strip()
    audience = data.get("audience", "beginners").strip()

    if not niche:
        niche = "your niche"
    if not topic:
        topic = "your next video"
    if not audience:
        audience = "beginners"

    return jsonify({
        "ideas": [
            f"5 Mistakes People Make About {topic}",
            f"I Tried {topic}: Here's What I Learned",
            f"The Beginner's Guide to {topic}"
        ],
        "titles": [
            f"{topic}: What Nobody Tells You",
            f"Stop Making These {topic} Mistakes",
            f"I Tested {topic} So You Don't Have To"
        ],
        "thumbnail_tip": (
            "Use one clear subject, strong contrast, "
            "and 2–4 readable words."
        ),
        "script": (
            f"HOOK: Ask a surprising question about {topic}.\n\n"
            f"VALUE: Explain what viewers will learn about {topic} "
            f"in the {niche} niche.\n\n"
            f"BODY: Give three useful points for {audience}.\n\n"
            "PAYOFF: Show the result or key takeaway.\n\n"
            "CTA: Ask viewers to comment with their experience."
        )
    })


if __name__ == "__main__":
    app.run(debug=True)
  
