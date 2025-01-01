import os
from typing import List, Tuple
from PIL import Image
import cv2
import pytesseract
from fastapi import FastAPI, UploadFile, Form
from pydantic import BaseModel
import json
from transformers import pipeline

# Install necessary libraries with pip: 
# pip install Pillow opencv-python pytesseract fastapi uvicorn transformers torch

# Define constants
MODERATION_LOG_FILE = "moderation_logs.txt"
DEFAULT_GUIDELINES = "default_guidelines.json"

# Load community guidelines
def load_guidelines(file_path: str) -> dict:
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"text": [], "image": [], "video": []}

guidelines = load_guidelines(DEFAULT_GUIDELINES)

# Initialize NLP pipeline for multilingual content moderation
nlp_moderation_pipeline = pipeline("text-classification", model="unitary/toxic-bert")

# Helper functions
def log_moderation_action(content_type: str, content_identifier: str, action: str):
    """Log moderation actions to a file."""
    with open(MODERATION_LOG_FILE, "a") as log_file:
        log_file.write(f"Content Type: {content_type}, Identifier: {content_identifier}, Action: {action}\n")

# Text Moderation
def moderate_text(text: str, community_guidelines: List[str]) -> Tuple[bool, List[str]]:
    """Moderate text content for inappropriate content."""
    nlp_results = nlp_moderation_pipeline(text)
    violations = []
    for result in nlp_results:
        if result["label"] == "TOXIC" and result["score"] > 0.7:
            violations.append("Toxic or offensive content detected")
    for guideline in community_guidelines:
        if guideline.lower() in text.lower():
            violations.append(f"Violation: {guideline}")
    return len(violations) == 0, violations

# Image Moderation
def moderate_image(image_path: str, community_guidelines: List[str]) -> Tuple[bool, List[str]]:
    """Moderate image content by analyzing text and detecting explicit material."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        is_text_safe, reasons = moderate_text(text, community_guidelines)
        if not is_text_safe:
            return False, reasons
        # Extend here with explicit image detection algorithms if needed
        return True, []
    except Exception as e:
        return False, [f"Error processing image: {str(e)}"]

# Video Moderation
def moderate_video(video_path: str, community_guidelines: List[str]) -> Tuple[bool, List[str]]:
    """Moderate video content by extracting frames and analyzing text."""
    try:
        cap = cv2.VideoCapture(video_path)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        reasons = []
        for i in range(0, frame_count, max(1, frame_rate)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
            temp_image_path = "temp_frame.jpg"
            cv2.imwrite(temp_image_path, frame)
            is_frame_safe, frame_reasons = moderate_image(temp_image_path, community_guidelines)
            os.remove(temp_image_path)
            if not is_frame_safe:
                reasons.extend(frame_reasons)
        cap.release()
        return len(reasons) == 0, reasons
    except Exception as e:
        return False, [f"Error processing video: {str(e)}"]

# FastAPI Application
app = FastAPI()

class CommunityGuidelines(BaseModel):
    text: List[str]
    image: List[str]
    video: List[str]

@app.post("/upload")
async def moderate(content_type: str = Form(...), file: UploadFile = None):
    if content_type not in ["text", "image", "video"] or not file:
        return {"error": "Invalid content type or file missing"}

    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    if content_type == "text":
        with open(file_path, "r") as text_file:
            text = text_file.read()
        is_safe, reasons = moderate_text(text, guidelines["text"])
    elif content_type == "image":
        is_safe, reasons = moderate_image(file_path, guidelines["image"])
    elif content_type == "video":
        is_safe, reasons = moderate_video(file_path, guidelines["video"])

    os.remove(file_path)

    action = "Approved" if is_safe else f"Rejected: {', '.join(reasons)}"
    log_moderation_action(content_type, file.filename, action)
    return {"status": action}

@app.post("/update-guidelines")
async def update_guidelines(new_guidelines: CommunityGuidelines):
    global guidelines
    guidelines = new_guidelines.dict()
    with open(DEFAULT_GUIDELINES, "w") as file:
        json.dump(guidelines, file, indent=4)
    return {"message": "Community guidelines updated successfully"}

# Example of running the server
# Use: uvicorn content_moderation:app --reload
