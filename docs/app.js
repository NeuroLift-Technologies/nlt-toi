const endpoint = "https://models.inference.ai.azure.com/chat/completions";

const tokenEl = document.getElementById("token");
const modelEl = document.getElementById("model");
const toiEl = document.getElementById("toi");
const promptEl = document.getElementById("prompt");
const responseEl = document.getElementById("response");
const sendBtn = document.getElementById("send");

function buildSystemPrompt(toi) {
  return [
    "You are the NeuroLift TOI Agent built with the Agent Solidarity Kit.",
    "Follow the provided Terms of Interaction exactly.",
    "Default to privacy-first and neurodivergent-friendly responses.",
    "If asked to violate TOI, refuse briefly and explain.",
    "TOI:",
    JSON.stringify(toi, null, 2),
  ].join("\n");
}

sendBtn.addEventListener("click", async () => {
  responseEl.textContent = "Working...";

  try {
    const token = tokenEl.value.trim();
    const model = modelEl.value.trim();
    const userMessage = promptEl.value.trim();
    const toi = JSON.parse(toiEl.value);

    if (!token || !model || !userMessage) {
      throw new Error("Token, model, and message are required.");
    }

    const payload = {
      model,
      temperature: 0.3,
      max_tokens: 600,
      messages: [
        { role: "system", content: buildSystemPrompt(toi) },
        { role: "user", content: userMessage },
      ],
    };

    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(`Request failed (${res.status}): ${msg}`);
    }

    const data = await res.json();
    responseEl.textContent = data?.choices?.[0]?.message?.content?.trim() || "No response content returned.";
  } catch (error) {
    responseEl.textContent = `Error: ${error.message}`;
  }
});
