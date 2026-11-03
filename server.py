"""Afghan AI demo backend. API keys must stay server-side."""
import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "ai_configured": bool(os.getenv("OPENAI_API_KEY"))})

@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    language = body.get("language", "fa")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    if len(message) > 5000:
        return jsonify({"error": "Message is too long"}), 413
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service is not configured"}), 503
    lang_name = {"fa": "Dari Persian", "ps": "Pashto", "en": "English"}.get(language, "Dari Persian")
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are Afghan AI, a kind, accurate, age-appropriate school tutor for students in Afghanistan. "
                f"Answer in {lang_name}. Explain step by step, use simple examples, and encourage independent learning. "
                "For homework, explain the method rather than only giving a final answer. Be transparent about uncertainty. "
                "Do not claim to quote official Afghan curriculum unless the source is provided. Avoid requesting personal data."
            ),
            input=message,
        )
        return jsonify({"answer": response.output_text})
    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({"error": "AI request failed"}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8000")), debug=False)
