# Deploying VideoDub Pro to Render

This guide explains how to deploy the VideoDub Pro video dubbing application to Render.

## Prerequisites

- A Render account (free tier available at https://render.com)
- A GitHub repository with this project code

## Deployment Steps (Docker - Recommended)

This project uses Docker deployment to ensure FFmpeg and all dependencies are properly installed.

### Option 1: Using Render Blueprint (Recommended)

1. **Push your code to GitHub**
   - Make sure all files including `render.yaml` and `Dockerfile` are committed

2. **Connect to Render**
   - Go to https://dashboard.render.com
   - Click "New" > "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Deploy**
   - Click "Apply" to create the service
   - Wait for the build to complete (may take 10-15 minutes due to ML dependencies)

### Option 2: Manual Docker Deployment

1. **Create a new Web Service**
   - Go to https://dashboard.render.com
   - Click "New" > "Web Service"
   - Connect your GitHub repository

2. **Configure the service**
   - **Name**: videodub-pro (or your preferred name)
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile`

3. **Add Environment Variables**
   - `PORT`: `10000`
   - `SECRET_KEY`: (Render will auto-generate this)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete

## Key Files for Deployment

| File | Purpose |
|------|---------|
| `Dockerfile` | Docker configuration with FFmpeg and Python dependencies |
| `render.yaml` | Render blueprint for automated deployment |
| `requirements-render.txt` | Python dependencies including Flask, torch, and numpy |
| `Procfile` | Alternative process file for non-Docker deployments |
| `app.py` | Main Flask application |

## Memory Considerations

- The Whisper AI model requires significant memory
- **Recommended**: Use at least 2GB RAM (Starter plan or higher)
- Free tier may experience slower processing or memory errors with longer videos
- Consider using a smaller Whisper model for memory-constrained environments

## File Storage

- Processed videos are stored temporarily during the session
- Files are cleaned up when users process a new video
- For production use with heavy traffic, consider integrating cloud storage (S3, GCS)

## Troubleshooting

### Build Failures
- Ensure all files (`Dockerfile`, `requirements-render.txt`) are committed
- Check Render build logs for specific error messages
- Verify torch and numpy are installing correctly

### App Not Loading
- Check the health endpoint: `/health`
- Verify the PORT environment variable is set to 10000
- Review Render logs for startup errors

### Processing Errors
- Ensure video files are MP4 format
- Check memory usage in Render dashboard
- For longer videos, upgrade to a plan with more RAM

### Slow Performance
- First request may be slow as Whisper model loads
- Consider adding model caching for production use
- Upgrade plan for more CPU/memory resources

## Health Check

The Flask application provides a health endpoint:
- Path: `/health`
- Returns: `{"status": "healthy"}`
- This is automatically configured in `render.yaml`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/health` | GET | Health check |
| `/api/upload` | POST | Upload video |
| `/api/process/stage1` | POST | Transcribe and translate |
| `/api/process/stage2` | POST | Generate dubbed video |
| `/api/download/video` | GET | Download final video |

## Support

For issues specific to this application, please open a GitHub issue.
For Render-related issues, visit https://render.com/docs
