
const form = document.getElementById("strategyForm");
const button = document.getElementById("generateBtn");
const results = document.getElementById("results");

function showList(id, items) {
  const list = document.getElementById(id);
  list.replaceChildren();

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  button.disabled = true;
  button.textContent = "Building your strategy...";

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        niche: document.getElementById("niche").value,
        topic: document.getElementById("topic").value,
        audience: document.getElementById("audience").value
      })
    });

    if (!response.ok) {
      throw new Error("The server couldn't generate your strategy.");
    }

    const data = await response.json();

    showList("ideas", data.ideas);
    showList("titles", data.titles);
    document.getElementById("thumbnail").textContent =
      data.thumbnail_tip;
    document.getElementById("script").textContent = data.script;

    results.hidden = false;
    results.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  } catch (error) {
    alert(
      "Couldn't generate results. Make sure the website is deployed and try again."
    );
    console.error(error);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Generate my strategy <span>↗</span>';
  }
});
