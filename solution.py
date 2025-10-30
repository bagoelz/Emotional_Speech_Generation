#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Optional, Dict, Any

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TTSEngine:
    """Base class for TTS engines"""
    
    def __init__(self, name: str):
        self.name = name
        self.available = False
        
    def check_availability(self) -> bool:
        """Check if engine is available"""
        return self.available
        
    def synthesize(self, text: str, output_path: Path, style: str = "neutral", 
                  intensity: int = 50, **kwargs) -> bool:
        """Synthesize text to audio file"""
        raise NotImplementedError


class CoquiTTSEngine(TTSEngine):
    """Coqui TTS Engine - Primary choice for high quality neural synthesis"""
    
    def __init__(self):
        super().__init__("coqui")
        self.tts = None
        self._check_and_init()
        
    def _check_and_init(self):
        """Initialize Coqui TTS if available"""
        try:
            from TTS.api import TTS
            
            # Try to initialize with a lightweight model
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            logger.info(f"Initializing Coqui TTS with model: {model_name}")
            
            self.tts = TTS(model_name=model_name, progress_bar=False)
            self.available = True
            logger.info("✓ Coqui TTS engine initialized successfully")
            
        except ImportError:
            logger.warning("Coqui TTS not available - install with: pip install TTS torch")
            self.available = False
        except Exception as e:
            logger.warning(f"Coqui TTS initialization failed: {e}")
            self.available = False
    
    def synthesize(self, text: str, output_path: Path, style: str = "neutral", 
                  intensity: int = 50, **kwargs) -> bool:
        """Synthesize using Coqui TTS"""
        if not self.available:
            return False
            
        try:
            # Style mapping for Coqui TTS
            style_params = self._get_style_params(style, intensity)
            
            logger.info(f"Synthesizing with Coqui TTS: style={style}, intensity={intensity}")
            
            # Generate audio
            self.tts.tts_to_file(
                text=text,
                file_path=str(output_path),
                **style_params
            )
            
            logger.info(f"✓ Audio generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            return False
    
    def _get_style_params(self, style: str, intensity: int) -> Dict[str, Any]:
        """Map style and intensity to Coqui TTS parameters"""
        # Base parameters
        params = {}
        
        # Intensity scaling (0-100 -> 0.5-1.5)
        intensity_scale = 0.5 + (intensity / 100.0)
        
        # Style-specific adjustments
        style_configs = {
            "neutral": {},
            "enthusiastic": {"speed": 1.1 * intensity_scale},
            "somber": {"speed": 0.8 / intensity_scale},
            "confident": {"speed": 1.0 * intensity_scale},
            "authoritative": {"speed": 0.9 * intensity_scale}
        }
        
        return style_configs.get(style, {})


class PyttsxEngine(TTSEngine):
    """pyttsx3 Engine - Fallback choice for compatibility"""
    
    def __init__(self):
        super().__init__("pyttsx3")
        self.engine = None
        self._check_and_init()
        
    def _check_and_init(self):
        """Initialize pyttsx3 if available"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.available = True
            logger.info("✓ pyttsx3 engine initialized successfully")
            
        except ImportError:
            logger.warning("pyttsx3 not available - install with: pip install pyttsx3")
            self.available = False
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {e}")
            self.available = False
    
    def synthesize(self, text: str, output_path: Path, style: str = "neutral", 
                  intensity: int = 50, voice: Optional[str] = None, **kwargs) -> bool:
        """Synthesize using pyttsx3"""
        if not self.available:
            return False
            
        try:
            # Apply voice selection
            if voice is not None:
                self._select_voice(voice)
            
            # Apply style parameters
            self._apply_style(style, intensity)
            
            logger.info(f"Synthesizing with pyttsx3: style={style}, intensity={intensity}")
            
            # Generate audio
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            
            logger.info(f"✓ Audio generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            return False
    
    def _select_voice(self, voice_query: str):
        """Select voice by index, name, or gender"""
        voices = self.engine.getProperty('voices')
        
        # Handle gender-based selection
        if voice_query.lower() in ['female', 'woman', 'wanita', 'perempuan']:
            female_voice = self._find_female_voice(voices)
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
                logger.info(f"Selected female voice: {getattr(female_voice, 'name', 'Unknown')}")
                return
        elif voice_query.lower() in ['male', 'man', 'pria', 'laki-laki']:
            male_voice = self._find_male_voice(voices)
            if male_voice:
                self.engine.setProperty('voice', male_voice.id)
                logger.info(f"Selected male voice: {getattr(male_voice, 'name', 'Unknown')}")
                return
        
        # Try index selection
        try:
            idx = int(voice_query)
            if 0 <= idx < len(voices):
                self.engine.setProperty('voice', voices[idx].id)
                return
        except ValueError:
            pass
        
        # Try name matching
        for v in voices:
            if voice_query.lower() in getattr(v, 'name', '').lower():
                self.engine.setProperty('voice', v.id)
                return
    
    def _find_female_voice(self, voices):
        """Find a female voice from available voices"""
        # Common female voice indicators
        female_indicators = [
            'zira', 'hazel', 'susan', 'anna', 'helena', 'sabina', 'katja',
            'female', 'woman', 'girl', 'lady', 'ms', 'miss', 'mrs',
            'f+', '+f', '(f)', '[f]', 'fem'
        ]
        
        for voice in voices:
            name = getattr(voice, 'name', '').lower()
            # Check for female indicators in voice name
            if any(indicator in name for indicator in female_indicators):
                return voice
        
        # If no clear female voice found, return first voice (often default female)
        return voices[0] if voices else None
    
    def _find_male_voice(self, voices):
        """Find a male voice from available voices"""
        # Common male voice indicators
        male_indicators = [
            'david', 'mark', 'richard', 'george', 'james', 'paul',
            'male', 'man', 'boy', 'gentleman', 'mr', 'mister',
            'm+', '+m', '(m)', '[m]', 'masc'
        ]
        
        for voice in voices:
            name = getattr(voice, 'name', '').lower()
            # Check for male indicators in voice name
            if any(indicator in name for indicator in male_indicators):
                return voice
        
        # If no clear male voice found, return second voice if available
        return voices[1] if len(voices) > 1 else voices[0] if voices else None
    
    def _apply_style(self, style: str, intensity: int):
        """Apply style parameters to pyttsx3 engine"""
        base_rate = self.engine.getProperty('rate')
        base_volume = self.engine.getProperty('volume')
        
        # Intensity scaling
        intensity_factor = 0.5 + (intensity / 100.0)
        
        # Style configurations
        style_configs = {
            "neutral": {"rate_mult": 1.0, "volume_mult": 1.0},
            "enthusiastic": {"rate_mult": 1.3, "volume_mult": 1.2},
            "somber": {"rate_mult": 0.7, "volume_mult": 0.8},
            "confident": {"rate_mult": 1.1, "volume_mult": 1.1},
            "authoritative": {"rate_mult": 0.9, "volume_mult": 1.0}
        }
        
        config = style_configs.get(style, style_configs["neutral"])
        
        # Apply parameters
        new_rate = int(base_rate * config["rate_mult"] * intensity_factor)
        new_volume = min(1.0, base_volume * config["volume_mult"] * intensity_factor)
        
        self.engine.setProperty('rate', new_rate)
        self.engine.setProperty('volume', new_volume)
    
    def list_voices(self):
        """List available voices with gender detection"""
        if not self.available:
            return []
            
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for i, v in enumerate(voices):
            name = getattr(v, 'name', 'Unknown')
            lang = getattr(v, 'languages', ['Unknown'])
            
            # Detect gender
            gender = self._detect_gender(name)
            
            voice_info = {
                'index': i,
                'name': name,
                'id': v.id,
                'languages': lang,
                'gender': gender
            }
            voice_list.append(voice_info)
            
        return voice_list
    
    def _detect_gender(self, voice_name: str) -> str:
        """Detect gender from voice name"""
        name_lower = voice_name.lower()
        
        # Female indicators
        female_indicators = [
            'zira', 'hazel', 'susan', 'anna', 'helena', 'sabina', 'katja',
            'female', 'woman', 'girl', 'lady', 'ms', 'miss', 'mrs',
            'f+', '+f', '(f)', '[f]', 'fem'
        ]
        
        # Male indicators  
        male_indicators = [
            'david', 'mark', 'richard', 'george', 'james', 'paul',
            'male', 'man', 'boy', 'gentleman', 'mr', 'mister',
            'm+', '+m', '(m)', '[m]', 'masc'
        ]
        
        if any(indicator in name_lower for indicator in female_indicators):
            return 'female'
        elif any(indicator in name_lower for indicator in male_indicators):
            return 'male'
        else:
            return 'unknown'


class DualTTSSystem:
    """Dual Engine TTS System with auto-fallback"""
    
    def __init__(self):
        self.coqui = CoquiTTSEngine()
        self.pyttsx = PyttsxEngine()
        
        # Determine primary engine
        if self.coqui.available:
            self.primary = self.coqui
            self.fallback = self.pyttsx
            logger.info("Primary engine: Coqui TTS, Fallback: pyttsx3")
        elif self.pyttsx.available:
            self.primary = self.pyttsx
            self.fallback = None
            logger.info("Primary engine: pyttsx3 (Coqui TTS not available)")
        else:
            logger.error("No TTS engines available!")
            sys.exit(1)
    
    def synthesize(self, text: str, output_path: Path, engine: str = "auto", **kwargs) -> bool:
        """Synthesize with specified or auto-selected engine"""
        
        # Engine selection
        if engine == "auto":
            selected_engine = self.primary
        elif engine == "coqui":
            if not self.coqui.available:
                logger.warning("Coqui TTS not available, falling back to pyttsx3")
                selected_engine = self.pyttsx
            else:
                selected_engine = self.coqui
        elif engine == "pyttsx3":
            selected_engine = self.pyttsx
        else:
            logger.error(f"Unknown engine: {engine}")
            return False
        
        # Attempt synthesis
        success = selected_engine.synthesize(text, output_path, **kwargs)
        
        # Auto-fallback if primary fails
        if not success and self.fallback and selected_engine == self.primary:
            logger.warning(f"Primary engine failed, trying fallback: {self.fallback.name}")
            success = self.fallback.synthesize(text, output_path, **kwargs)
        
        return success
    
    def get_status(self) -> Dict[str, bool]:
        """Get engine availability status"""
        return {
            "coqui": self.coqui.available,
            "pyttsx3": self.pyttsx.available
        }
    
    def get_voices(self):
        """Get available voices from all engines"""
        voices = {
            "coqui": [],
            "pyttsx3": []
        }
        
        if self.pyttsx.available:
            voices["pyttsx3"] = self.pyttsx.list_voices()
            
        # Add Coqui voices (hardcoded for now as Coqui has predefined models)
        if self.coqui.available:
            voices["coqui"] = [
                {"name": "Coqui Female Voice", "gender": "female", "language": "en"},
                {"name": "Coqui Male Voice", "gender": "male", "language": "en"}
            ]
            
        return voices
    
    def select_female_voice(self, engine: str = "auto"):
        """Select a female voice for the specified engine"""
        if engine == "auto":
            engine = "pyttsx3" if self.pyttsx.available else "coqui"
            
        if engine == "pyttsx3" and self.pyttsx.available:
            # Use the gender-based selection
            return "female"
        elif engine == "coqui" and self.coqui.available:
            # Coqui uses different voice selection method
            return "female"
        
        return None


def validate_inputs(text: str, output_path: Path) -> bool:
    """Validate input parameters"""
    if not text.strip():
        logger.error("Text input cannot be empty")
        return False
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if output path is writable
    try:
        output_path.touch()
        return True
    except Exception as e:
        logger.error(f"Cannot write to output path: {e}")
        return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Emotional Speech Generation - Dual Engine TTS System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python solution.py "Hello world" hello.wav
  python solution.py "We did it!" out.wav --style enthusiastic --intensity 80
  python solution.py "Somber news" news.wav --style somber --engine coqui
  python solution.py "Text here" out.wav --engine pyttsx3 --voice 1
  python solution.py --list-voices
  python solution.py --status
        """
    )
    
    parser.add_argument("text", nargs="?", help="Text to synthesize")
    parser.add_argument("output", nargs="?", help="Output WAV file path")
    
    parser.add_argument("--style", default="neutral", 
                       choices=["neutral", "enthusiastic", "somber", "confident", "authoritative"],
                       help="Speech style (default: neutral)")
    
    parser.add_argument("--intensity", type=int, default=50, metavar="0-100",
                       help="Style intensity 0-100 (default: 50)")
    
    parser.add_argument("--engine", default="auto", 
                       choices=["auto", "coqui", "pyttsx3"],
                       help="TTS engine selection (default: auto)")
    
    parser.add_argument("--voice", help="Voice selection (pyttsx3 only: index or name)")
    
    parser.add_argument("--list-voices", action="store_true",
                       help="List available voices and exit")
    
    parser.add_argument("--status", action="store_true",
                       help="Show engine status and exit")
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize TTS system
    tts_system = DualTTSSystem()
    
    # Handle special commands
    if args.status:
        status = tts_system.get_status()
        print("TTS Engine Status:")
        for engine, available in status.items():
            status_str = "✓ Available" if available else "✗ Not Available"
            print(f"  {engine}: {status_str}")
        return 0
    
    if args.list_voices:
        tts_system.pyttsx.list_voices()
        return 0
    
    # Validate required arguments
    if not args.text or not args.output:
        parser.error("Both text and output arguments are required")
    
    # Validate intensity range
    if not 0 <= args.intensity <= 100:
        parser.error("Intensity must be between 0 and 100")
    
    # Prepare paths and validate
    output_path = Path(args.output)
    if not validate_inputs(args.text, output_path):
        return 1
    
    # Synthesize
    logger.info(f"Starting synthesis: '{args.text[:50]}{'...' if len(args.text) > 50 else ''}'")
    
    success = tts_system.synthesize(
        text=args.text,
        output_path=output_path,
        engine=args.engine,
        style=args.style,
        intensity=args.intensity,
        voice=args.voice
    )
    
    if success:
        logger.info("✓ Synthesis completed successfully!")
        return 0
    else:
        logger.error("✗ Synthesis failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())