
# Multilingual Content Moderation Program - Instructions

This program automates content moderation for a social media platform, ensuring compliance with community guidelines.
It supports text, image, and video content moderation and uses Hugging Face Transformers for multilingual text analysis.

## Prerequisites

1. **Python 3.7 or above** must be installed on your system.
2. Install the required Python libraries using pip:
   ```bash
   pip install fastapi uvicorn Pillow opencv-python pytesseract transformers torch
   ```
3. **Tesseract OCR** must be installed for text extraction from images:
   - Windows: [Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: Install using `sudo apt install tesseract-ocr`
   - macOS: Install using `brew install tesseract`
4. Ensure the model `unitary/toxic-bert` can be accessed. It will be automatically downloaded the first time it runs.

## Running the Program

1. Save the provided Python code to a file named `content_moderation.py`.
2. Start the FastAPI server using the following command:
   ```bash
   uvicorn content_moderation:app --reload
   ```
3. The server will start running locally. By default, it will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

### 1. `/upload`
Uploads content for moderation.

**Method**: POST  
**Parameters**:
- `content_type`: The type of content to moderate (`text`, `image`, `video`).
- `file`: The file to be moderated.

**Example Command Using `curl`**:
```bash
curl -X POST "http://127.0.0.1:8000/upload" -F "content_type=text" -F "file=@sample.txt"
```

### 2. `/update-guidelines`
Updates the community guidelines.

**Method**: POST  
**Body**:
- JSON object with updated guidelines for `text`, `image`, and `video` content.

**Example Command Using `curl`**:
```bash
curl -X POST "http://127.0.0.1:8000/update-guidelines" -H "Content-Type: application/json" -d '{
    "text": ["new prohibited words"],
    "image": ["new image-related guidelines"],
    "video": ["new video-related guidelines"]
}'
```

## Logs

All moderation actions are logged in the `moderation_logs.txt` file in the same directory.

## Customization

1. **Guidelines**:
   - Update the default guidelines by editing the `default_guidelines.json` file or using the `/update-guidelines` API.

2. **Extend Moderation**:
   - Add more advanced moderation techniques (e.g., nudity detection, audio analysis) by enhancing the functions.

## Stopping the Server

To stop the server, press `Ctrl+C` in the terminal where the server is running.

## Additional Notes

- Ensure `temp_` files created during processing are cleaned up automatically.
- For large-scale deployment, consider containerization with Docker and orchestration with Kubernetes.
