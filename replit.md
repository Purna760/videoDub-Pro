# VideoDub Pro - AI Video Dubbing Application

## Overview

VideoDub Pro is a Flask-based video dubbing application that automates the process of translating and dubbing videos into different languages. The application extracts audio from videos, transcribes it using AI speech recognition, translates the transcription, generates dubbed audio in the target language, and produces a final video with the new audio track.

The application features a modern, professional dark-themed UI with smooth animations, glass-morphism effects, and a premium feel.

## Recent Changes

- **November 27, 2025**: Complete Flask conversion and UI redesign
  - Converted entire application from Streamlit to Flask framework
  - Created beautiful dark-themed HTML/CSS/JavaScript UI
  - Implemented REST API endpoints for all video processing functionality
  - Added real-time progress tracking with AJAX polling
  - Glass-morphism design with gradient backgrounds and animations
  - Responsive layout for mobile and desktop
  - Created Render deployment files (Dockerfile, render.yaml, Procfile)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology**: Flask with Jinja2 templates, vanilla JavaScript

The application uses Flask for serving HTML templates with an interactive UI featuring:
- Drag-and-drop video upload
- Real-time progress tracking with animated status indicators
- Subtitle review and editing interface
- Video preview and download options

**Design Features**:
- Dark theme with gradient backgrounds
- Glass-morphism card effects
- Animated progress indicators
- Responsive mobile-friendly layout
- Professional typography (Inter font)

### Backend Architecture

**Processing Pipeline**: Two-stage workflow via REST API

Stage 1 - Transcription and Translation:
- POST /api/upload - Upload video file
- POST /api/process/stage1 - Extract audio, transcribe, translate
- GET /api/progress - Real-time status polling

Stage 2 - Audio Generation and Video Creation:
- POST /api/save-edits - Save subtitle edits
- POST /api/process/stage2 - Generate dubbed audio, merge video
- GET /api/download/video - Download final video
- GET /api/download/original-srt - Download original subtitles
- GET /api/download/translated-srt - Download translated subtitles

### Modular Component Design

Each processing step is isolated in its own utility module:

- `utils/video_processor.py` - FFmpeg and MoviePy for video/audio manipulation
- `utils/transcriber.py` - Faster-Whisper integration for speech-to-text
- `utils/subtitle_generator.py` - SRT file format generation with timing
- `utils/translator.py` - Text translation service
- `utils/audio_generator.py` - Text-to-speech synthesis with timing alignment

## External Dependencies

### AI/ML Services

**Faster-Whisper** - Speech recognition model
- Model: "small" variant, CPU with int8 quantization
- Purpose: Transcribe video audio with timestamps

**Google Text-to-Speech (gTTS)** - Audio generation
- Purpose: Convert translated text to speech
- Languages: 20+ supported languages

**Translate Library** - Text translation
- Purpose: Translate subtitles between languages
- Auto-detects source language

### Media Processing

**FFmpeg-Python** - Audio extraction (16kHz mono PCM)
**MoviePy** - Video editing and audio replacement
**pysrt** - SRT subtitle file handling
**pydub** - Audio manipulation and timing

## File Structure

```
├── app.py                     # Main Flask application
├── templates/
│   └── index.html             # HTML template with CSS/JavaScript
├── utils/
│   ├── video_processor.py     # Video/audio extraction and merging
│   ├── transcriber.py         # Speech-to-text using Whisper
│   ├── subtitle_generator.py  # SRT file generation
│   ├── translator.py          # Text translation
│   └── audio_generator.py     # Text-to-speech synthesis
├── Dockerfile                 # Docker configuration for Render
├── render.yaml                # Render blueprint configuration
├── Procfile                   # Process file for deployment
├── requirements-render.txt    # Dependencies for Render deployment
├── DEPLOY_RENDER.md           # Render deployment guide
└── replit.md                  # This documentation file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/health` | GET | Health check endpoint |
| `/api/languages` | GET | Get supported languages |
| `/api/upload` | POST | Upload video file |
| `/api/process/stage1` | POST | Process video (transcribe, translate) |
| `/api/progress` | GET | Get processing status |
| `/api/save-edits` | POST | Save subtitle edits |
| `/api/process/stage2` | POST | Generate dubbed video |
| `/api/download/video` | GET | Download dubbed video |
| `/api/download/original-srt` | GET | Download original subtitles |
| `/api/download/translated-srt` | GET | Download translated subtitles |
| `/api/reset` | POST | Reset session |

## Deployment

### Replit
The application runs on Replit using Flask on port 5000.
Command: `python app.py`

### Render
For Render deployment, use Docker:
1. Push code to GitHub
2. Connect repository to Render
3. Select "Docker" runtime
4. Deploy automatically via render.yaml

See `DEPLOY_RENDER.md` for detailed deployment instructions.

## Supported Languages

English, Spanish, French, German, Hindi, Tamil, Arabic, Chinese (Simplified), Japanese, Korean, Portuguese, Russian, Italian, Dutch, Polish, Turkish, Vietnamese, Thai, Indonesian, Malay
