import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from PIL import Image

app = Flask(__name__)

# System Instruction to give clean, non-technical subject answers
SYSTEM_INSTRUCTION = """
You are Ji Web Assistant, a helpful and smart AI. 
Provide clear, accurate, and direct answers relevant to the user's question or subject (e.g., Business, Commerce, Tamil, History, Science). 
Do NOT generate programming code or technical scripts unless the user explicitly asks for code or Python/programming topics.
"""

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    client = get_client()
    if not client:
        return jsonify({"error": "GEMINI_API_KEY is missing in Environment Variables."}), 400

    prompt = request.form.get("prompt", "").strip()
    image_file = request.files.get("image")

    if not prompt and not image_file:
        return jsonify({"error": "Please enter a message or upload an image."}), 400

    contents = []
    
    if image_file and image_file.filename != "":
        try:
            img = Image.open(image_file.stream)
            contents.append(img)
        except Exception as e:
            return jsonify({"error": f"Invalid image file: {str(e)}"}), 400

    if prompt:
        contents.append(prompt)

    try:
        # Using the official gemini-2.5-flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)