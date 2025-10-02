from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from downloader import VideoDownloader
from audio_to_midi import AudioToMidiConverter
from midi_refiner import MidiRefiner
from sheet_music_generator import SheetMusicGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for iOS app

# Initialize components
downloader = VideoDownloader()
audio_converter = AudioToMidiConverter()
midi_refiner = MidiRefiner()
sheet_generator = SheetMusicGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Music Transcriber API'})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Main transcription endpoint"""
    try:
        data = request.json
        video_url = data.get('url')
        title = data.get('title', 'Untitled')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())[:8]
        
        # Step 1: Download audio
        print(f"[{job_id}] Downloading audio from {video_url}")
        download_result = downloader.download_audio(video_url)
        
        if not download_result['success']:
            return jsonify({'error': download_result['error']}), 400
        
        audio_file = download_result['file_path']
        video_title = download_result['title']
        
        # Step 2: Convert to MIDI
        print(f"[{job_id}] Converting audio to MIDI")
        midi_result = audio_converter.convert(audio_file)
        
        if not midi_result['success']:
            downloader.cleanup(audio_file)
            return jsonify({'error': midi_result['error']}), 500
        
        midi_file = midi_result['midi_file']
        
        # Step 3: Refine MIDI
        print(f"[{job_id}] Refining MIDI with AI")
        refine_result = midi_refiner.refine(midi_file)
        
        if not refine_result['success']:
            downloader.cleanup(audio_file)
            return jsonify({'error': refine_result['error']}), 500
        
        refined_midi = refine_result['refined_file']
        
        # Step 4: Generate sheet music
        print(f"[{job_id}] Generating sheet music")
        sheet_result = sheet_generator.generate(refined_midi, title=video_title)
        
        if not sheet_result['success']:
            downloader.cleanup(audio_file)
            return jsonify({'error': sheet_result['error']}), 500
        
        # Cleanup audio file
        downloader.cleanup(audio_file)
        
        # Return results
        return jsonify({
            'success': True,
            'job_id': job_id,
            'title': video_title,
            'key': refine_result.get('key', 'Unknown'),
            'time_signature': refine_result.get('time_signature', '4/4'),
            'num_notes': midi_result.get('num_notes', 0),
            'files': {
                'midi': f'/download/midi/{job_id}',
                'pdf': f'/download/pdf/{job_id}',
                'xml': f'/download/xml/{job_id}'
            }
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/midi/<job_id>', methods=['GET'])
def download_midi(job_id):
    """Download MIDI file"""
    try:
        # Find the refined MIDI file
        for file in os.listdir('outputs'):
            if file.endswith('_refined.mid'):
                file_path = os.path.join('outputs', file)
                return send_file(file_path, as_attachment=True, 
                               download_name=f'{job_id}.mid')
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/pdf/<job_id>', methods=['GET'])
def download_pdf(job_id):
    """Download PDF file"""
    try:
        for file in os.listdir('outputs'):
            if file.endswith('.pdf'):
                file_path = os.path.join('outputs', file)
                return send_file(file_path, as_attachment=True,
                               download_name=f'{job_id}.pdf')
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/xml/<job_id>', methods=['GET'])
def download_xml(job_id):
    """Download MusicXML file"""
    try:
        for file in os.listdir('outputs'):
            if file.endswith('.musicxml'):
                file_path = os.path.join('outputs', file)
                return send_file(file_path, as_attachment=True,
                               download_name=f'{job_id}.musicxml')
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)