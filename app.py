import os
from flask import Flask, render_template, request, jsonify
from google import genai
from PIL import Image
import io

app = Flask(__name__)

# Fetch Gemini API Key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"response": "API Key அமைக்கப்படவில்லை!"}), 500
    
    prompt = request.form.get("prompt", "")
    image_file = request.files.get("image")
    
    contents = []
    if image_file:
        try:
            img_bytes = image_file.read()
            image = Image.open(io.BytesIO(img_bytes))
            contents.append(image)
        except Exception as e:
            return jsonify({"response": "படத்தை படிக்க முடியவில்லை!"}), 400
        
    if prompt:
        contents.append(prompt)
        
    if not contents:
        return jsonify({"response": "தயவுசெய்து ஏதேனும் கேள்வி அல்லது படத்தை அனுப்பவும்."})
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"பிழை ஏற்பட்டது: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
