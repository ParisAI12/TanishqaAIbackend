import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const HF_TOKEN = "YOUR_HF_TOKEN"; // replace this

app.post("/chat", async (req, res) => {
  try {
    const { message } = req.body;

    const systemPrompt = `
You are Tanishqa AI, a modern Copilot-style assistant.
Your tone is clear, calm, and helpful.
You provide structured, thoughtful answers.
You avoid emotional or romantic language.
You focus on reasoning, clarity, and practical guidance.
You collaborate with the user and offer next steps.
You do not imply human feelings or experiences.
    `;

    const response = await fetch(
      "https://api-inference.huggingface.co/models/microsoft/Phi-3-medium-4k-instruct",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${HF_TOKEN}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          inputs: `${systemPrompt}\nUser: ${message}\nTanishqa AI:`,
          parameters: {
            max_new_tokens: 200,
            temperature: 0.7
          }
        })
      }
    );

    const data = await response.json();

    const text =
      data[0]?.generated_text ||
      data.generated_text ||
      "I can help with that. Tell me more about what you're trying to do.";

    const reply = text.split("Tanishqa AI:").pop().trim();

    res.json({ reply });
  } catch (err) {
    res.json({ reply: "Backend error: " + err.message });
  }
});

app.listen(3000, () => {
  console.log("Backend running on port 3000");
});

