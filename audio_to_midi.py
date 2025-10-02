from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import os

class AudioToMidiConverter:
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def convert(self, audio_file):
        """Convert audio file to MIDI"""
        try:
            # Run basic-pitch prediction
            model_output, midi_data, note_events = predict(
                audio_file,
                ICASSP_2022_MODEL_PATH,
                onset_threshold=0.5,
                frame_threshold=0.3,
                minimum_note_length=127.70,
                minimum_frequency=None,
                maximum_frequency=None,
                multiple_pitch_bends=False,
                melodia_trick=True,
            )
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            midi_file = os.path.join(self.output_dir, f"{base_name}.mid")
            
            # Save MIDI file
            midi_data.write(midi_file)
            
            return {
                'success': True,
                'midi_file': midi_file,
                'num_notes': len(note_events)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }