import os
import uuid
import shutil
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session

from utils.video_processor import extract_audio, replace_audio_track
from utils.transcriber import transcribe_audio
from utils.subtitle_generator import generate_subtitle_file
from utils.translator import translate_subtitles
from utils.audio_generator import generate_dubbed_audio

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'videodub-pro-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

sessions_data = {}

LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Tamil": "ta",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
    "Dutch": "nl",
    "Polish": "pl",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Thai": "th",
    "Indonesian": "id",
    "Malay": "ms"
}

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_session_data():
    session_id = get_session_id()
    if session_id not in sessions_data:
        sessions_data[session_id] = {
            'temp_dir': None,
            'video_path': None,
            'audio_path': None,
            'original_subtitle': None,
            'translated_subtitle': None,
            'output_video': None,
            'original_subtitles_data': [],
            'translated_subtitles_data': [],
            'target_lang_code': None,
            'progress_status': {
                'audio_extraction': 'pending',
                'transcription': 'pending',
                'translation': 'pending',
                'subtitle_generation': 'pending',
                'audio_generation': 'pending',
                'video_merging': 'pending'
            }
        }
    return sessions_data[session_id]

def cleanup_session():
    session_id = get_session_id()
    if session_id in sessions_data:
        data = sessions_data[session_id]
        if data['temp_dir'] and os.path.exists(data['temp_dir']):
            try:
                shutil.rmtree(data['temp_dir'])
            except Exception:
                pass
        del sessions_data[session_id]

def read_srt_file(srt_path):
    import pysrt
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
        subtitles_data = []
        for sub in subs:
            subtitles_data.append({
                'index': sub.index,
                'start': str(sub.start),
                'end': str(sub.end),
                'text': sub.text
            })
        return subtitles_data
    except Exception as e:
        return []

def save_edited_subtitles(subtitles_data, output_path):
    import pysrt
    try:
        subs = pysrt.SubRipFile()
        for sub_data in subtitles_data:
            sub = pysrt.SubRipItem(
                index=sub_data['index'],
                start=sub_data['start'],
                end=sub_data['end'],
                text=sub_data['text']
            )
            subs.append(sub)
        subs.save(output_path, encoding='utf-8')
        return True
    except Exception as e:
        return False

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/api/languages')
def get_languages():
    return jsonify(LANGUAGES)

@app.route('/api/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No video file selected'}), 400
        
        data = get_session_data()
        
        if data['temp_dir'] and os.path.exists(data['temp_dir']):
            shutil.rmtree(data['temp_dir'])
        
        temp_dir = tempfile.mkdtemp()
        data['temp_dir'] = temp_dir
        
        video_path = os.path.join(temp_dir, "input_video.mp4")
        video_file.save(video_path)
        data['video_path'] = video_path
        
        data['progress_status'] = {
            'audio_extraction': 'pending',
            'transcription': 'pending',
            'translation': 'pending',
            'subtitle_generation': 'pending',
            'audio_generation': 'pending',
            'video_merging': 'pending'
        }
        
        return jsonify({'success': True, 'message': 'Video uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process/stage1', methods=['POST'])
def process_stage1():
    try:
        req_data = request.get_json()
        target_language = req_data.get('target_language', 'Hindi')
        source_language = req_data.get('source_language', 'English')
        
        data = get_session_data()
        
        if not data['video_path'] or not os.path.exists(data['video_path']):
            return jsonify({'success': False, 'error': 'No video uploaded'}), 400
        
        temp_dir = data['temp_dir']
        video_path = data['video_path']
        
        data['progress_status']['audio_extraction'] = 'processing'
        audio_path = os.path.join(temp_dir, "extracted_audio.wav")
        extract_audio(video_path, audio_path)
        data['audio_path'] = audio_path
        data['progress_status']['audio_extraction'] = 'completed'
        
        data['progress_status']['transcription'] = 'processing'
        language, segments = transcribe_audio(audio_path)
        data['progress_status']['transcription'] = 'completed'
        
        data['progress_status']['subtitle_generation'] = 'processing'
        original_subtitle_path = os.path.join(temp_dir, f"subtitles_{language}.srt")
        generate_subtitle_file(segments, original_subtitle_path)
        data['original_subtitle'] = original_subtitle_path
        data['progress_status']['subtitle_generation'] = 'completed'
        
        data['progress_status']['translation'] = 'processing'
        target_lang_code = LANGUAGES.get(target_language, 'hi')
        source_lang_code = LANGUAGES.get(source_language, 'en')
        translated_subtitle_path = os.path.join(temp_dir, f"subtitles_{target_lang_code}.srt")
        translate_subtitles(original_subtitle_path, translated_subtitle_path, target_lang_code, source_lang_code)
        data['translated_subtitle'] = translated_subtitle_path
        data['target_lang_code'] = target_lang_code
        data['progress_status']['translation'] = 'completed'
        
        data['original_subtitles_data'] = read_srt_file(original_subtitle_path)
        data['translated_subtitles_data'] = read_srt_file(translated_subtitle_path)
        
        return jsonify({
            'success': True,
            'original_subtitles': data['original_subtitles_data'],
            'translated_subtitles': data['translated_subtitles_data'],
            'message': 'Stage 1 completed successfully'
        })
    except Exception as e:
        data = get_session_data()
        data['progress_status'] = {k: 'pending' for k in data['progress_status']}
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress')
def get_progress():
    data = get_session_data()
    return jsonify(data['progress_status'])

@app.route('/api/save-edits', methods=['POST'])
def save_edits():
    try:
        req_data = request.get_json()
        edited_subtitles = req_data.get('edited_subtitles', [])
        
        data = get_session_data()
        
        if not data['translated_subtitle']:
            return jsonify({'success': False, 'error': 'No subtitles to edit'}), 400
        
        for i, edit in enumerate(edited_subtitles):
            if i < len(data['translated_subtitles_data']):
                data['translated_subtitles_data'][i]['text'] = edit['text']
        
        success = save_edited_subtitles(data['translated_subtitles_data'], data['translated_subtitle'])
        
        if success:
            return jsonify({'success': True, 'message': 'Edits saved successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save edits'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process/stage2', methods=['POST'])
def process_stage2():
    try:
        data = get_session_data()
        
        if not data['translated_subtitle'] or not os.path.exists(data['translated_subtitle']):
            return jsonify({'success': False, 'error': 'No translated subtitles found'}), 400
        
        temp_dir = data['temp_dir']
        
        data['progress_status']['audio_generation'] = 'processing'
        dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")
        generate_dubbed_audio(data['translated_subtitle'], dubbed_audio_path, data['target_lang_code'])
        data['progress_status']['audio_generation'] = 'completed'
        
        data['progress_status']['video_merging'] = 'processing'
        output_video_path = os.path.join(temp_dir, "output_dubbed_video.mp4")
        replace_audio_track(data['video_path'], dubbed_audio_path, output_video_path)
        data['output_video'] = output_video_path
        data['progress_status']['video_merging'] = 'completed'
        
        return jsonify({
            'success': True,
            'message': 'Video dubbing completed successfully'
        })
    except Exception as e:
        data = get_session_data()
        data['progress_status']['audio_generation'] = 'pending'
        data['progress_status']['video_merging'] = 'pending'
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/video')
def download_video():
    try:
        data = get_session_data()
        if data['output_video'] and os.path.exists(data['output_video']):
            return send_file(
                data['output_video'],
                mimetype='video/mp4',
                as_attachment=True,
                download_name='dubbed_video.mp4'
            )
        return jsonify({'success': False, 'error': 'No video available'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/original-srt')
def download_original_srt():
    try:
        data = get_session_data()
        if data['original_subtitle'] and os.path.exists(data['original_subtitle']):
            return send_file(
                data['original_subtitle'],
                mimetype='text/plain',
                as_attachment=True,
                download_name='original_subtitles.srt'
            )
        return jsonify({'success': False, 'error': 'No subtitles available'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/translated-srt')
def download_translated_srt():
    try:
        data = get_session_data()
        if data['translated_subtitle'] and os.path.exists(data['translated_subtitle']):
            return send_file(
                data['translated_subtitle'],
                mimetype='text/plain',
                as_attachment=True,
                download_name='translated_subtitles.srt'
            )
        return jsonify({'success': False, 'error': 'No subtitles available'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_session():
    cleanup_session()
    return jsonify({'success': True, 'message': 'Session reset successfully'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
