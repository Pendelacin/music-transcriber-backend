from music21 import converter, layout, clef, metadata
import os

class SheetMusicGenerator:
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, midi_file, title="Untitled"):
        """Generate sheet music from MIDI"""
        try:
            score = converter.parse(midi_file)
            
            score.metadata = metadata.Metadata()
            score.metadata.title = title
            score.metadata.composer = "Transcribed by AI"
            
            score = self._format_score(score)
            
            base_name = os.path.splitext(os.path.basename(midi_file))[0]
            pdf_file = os.path.join(self.output_dir, f"{base_name}.pdf")
            xml_file = os.path.join(self.output_dir, f"{base_name}.musicxml")
            
            # Generate MusicXML (always works)
            score.write('musicxml', xml_file)
            
            # Try to generate PDF, but don't fail if it doesn't work
            try:
                score.write('lily.pdf', fp=pdf_file)
            except Exception as e:
                print(f"Warning: PDF generation failed: {e}")
                print("MusicXML file generated successfully - you can open this in MuseScore or other notation software")
                pdf_file = None
            
            return {
                'success': True,
                'pdf_file': pdf_file if pdf_file and os.path.exists(pdf_file) else xml_file,
                'xml_file': xml_file
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_score(self, score):
        """Format score for better appearance"""
        score.insert(0, layout.PageLayout(
            pageHeight=11.0 * 72,
            pageWidth=8.5 * 72,
            leftMargin=0.5 * 72,
            rightMargin=0.5 * 72,
            topMargin=0.5 * 72,
            bottomMargin=0.5 * 72
        ))
        
        for i, part in enumerate(score.parts):
            part_id = str(part.id) if part.id else f"Part {i+1}"
            
            if 'Right' in part_id or i == 0:
                part.insert(0, clef.TrebleClef())
            elif 'Left' in part_id or i == 1:
                part.insert(0, clef.BassClef())
        
        return score