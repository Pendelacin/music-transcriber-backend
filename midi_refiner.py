from music21 import converter, stream, note, chord, tempo, meter, key, clef
import copy

class MidiRefiner:
    def __init__(self):
        pass
    
    def refine(self, midi_file, output_file=None):
        """Refine MIDI file with AI-based corrections"""
        try:
            # Load MIDI
            score = converter.parse(midi_file)
            
            # Apply refinements
            score = self._quantize_notes(score)
            score = self._remove_short_notes(score)
            score = self._fix_overlapping_notes(score)
            score = self._detect_key_and_add(score)
            score = self._separate_hands_piano(score)
            
            # Save refined MIDI
            if output_file is None:
                output_file = midi_file.replace('.mid', '_refined.mid')
            
            score.write('midi', output_file)
            
            return {
                'success': True,
                'refined_file': output_file,
                'key': self._get_key(score),
                'time_signature': self._get_time_signature(score)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _quantize_notes(self, score, grid=0.25):
        """Snap notes to rhythmic grid"""
        for element in score.flatten().notesAndRests:
            element.offset = round(element.offset / grid) * grid
            element.duration.quarterLength = round(
                element.duration.quarterLength / grid
            ) * grid
        return score
    
    def _remove_short_notes(self, score, min_duration=0.125):
        """Remove very short notes"""
        for part in score.parts:
            notes_to_remove = []
            for element in part.flatten().notesAndRests:
                if isinstance(element, note.Note):
                    if element.duration.quarterLength < min_duration:
                        notes_to_remove.append(element)
            
            for n in notes_to_remove:
                part.remove(n, recurse=True)
        
        return score
    
    def _fix_overlapping_notes(self, score):
        """Fix overlapping notes"""
        for part in score.parts:
            notes = list(part.flatten().notes)
            notes.sort(key=lambda x: x.offset)
            
            for i in range(len(notes) - 1):
                current = notes[i]
                next_note = notes[i + 1]
                
                current_end = current.offset + current.duration.quarterLength
                if current_end > next_note.offset:
                    new_duration = next_note.offset - current.offset
                    if new_duration > 0:
                        current.duration.quarterLength = new_duration
        
        return score
    
    def _detect_key_and_add(self, score):
        """Detect and add key signature"""
        try:
            analyzed_key = score.analyze('key')
            score.insert(0, analyzed_key)
        except:
            pass
        return score
    
    def _get_key(self, score):
        """Get key signature"""
        try:
            k = score.analyze('key')
            return f"{k.tonic.name} {k.mode}"
        except:
            return "C major"
    
    def _get_time_signature(self, score):
        """Get time signature"""
        ts = score.flatten().getElementsByClass(meter.TimeSignature)
        if ts:
            return ts[0].ratioString
        return "4/4"
    
    def _separate_hands_piano(self, score):
        """Separate into right and left hand"""
        try:
            SPLIT_PITCH = 60  # Middle C
            
            right_hand = stream.Part()
            left_hand = stream.Part()
            
            right_hand.id = 'Right Hand'
            left_hand.id = 'Left Hand'
            
            for element in score.flatten().notesAndRests:
                if isinstance(element, note.Note):
                    if element.pitch.midi >= SPLIT_PITCH:
                        right_hand.append(copy.deepcopy(element))
                    else:
                        left_hand.append(copy.deepcopy(element))
                elif isinstance(element, chord.Chord):
                    highest = max(p.midi for p in element.pitches)
                    if highest >= SPLIT_PITCH:
                        right_hand.append(copy.deepcopy(element))
                    else:
                        left_hand.append(copy.deepcopy(element))
            
            new_score = stream.Score()
            new_score.insert(0, right_hand)
            new_score.insert(0, left_hand)
            
            return new_score
        except:
            return score