import cv2
import anthropic
import base64
import os

# 🔑 Put your Claude API key here
API_KEY = "your_claude_api_key_here"

client = anthropic.Anthropic(api_key=API_KEY)

# 📷 Capture image from webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera")
    exit()

print("Press SPACE to capture image")

while True:
    ret, frame = cap.read()
    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)
    if key == 32:  # Spacebar
        cv2.imwrite("frame.jpg", frame)
        break

cap.release()
cv2.destroyAllWindows()

# 📤 Send image to Claude
with open("frame.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this image and describe the emotional state of any people visible."
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
            ],
        }
    ],
)

print("\nClaude says:\n")
print(response.content[0].text)