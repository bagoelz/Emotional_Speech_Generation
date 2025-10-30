# Emotional Speech Generation — Conversational README

Imagine we’re side by side at your desk. You type a line, press enter, and a friendly narrator speaks back—with the mood you want. That’s what this tool does. It’s practical on Windows, works fine without a GPU, and can step up to richer, more expressive speech when you’re ready.

## What You Get
- A small command-line tool that turns your text into speech.
- A choice of mood: `neutral`, `enthusiastic`, `somber`, `confident`, or `authoritative`.
- Two engines so things always work: Coqui TTS for quality, pyttsx3 for reliability.

## Quick Start
Pick the setup that matches your machine and goals.

### Minimal Setup (pyttsx3 only)
1. `python -m venv .venv`
2. `./.venv/Scripts/Activate.ps1`
3. `pip install -r requirements.txt --no-deps`
4. `pip install pyttsx3 comtypes pywin32`

### Full Setup (Coqui TTS + pyttsx3)
1. `python -m venv .venv`
2. `./.venv/Scripts/Activate.ps1`
3. `pip install -r requirements.txt`
   - If Torch gives you trouble, install `torch` and `torchaudio` first, matching your Python/CPU/GPU.
4. `pip install TTS`

## Basic Use
`text` and `output` are positional.

- `python solution.py "Hello from our narrator" out.wav`
- Add mood and intensity:
  - `python solution.py "Hello from our narrator" out.wav --style enthusiastic --intensity 70`

## Pick Engine and Voice
- Let the tool choose (Coqui first, pyttsx3 fallback), or force one:
  - `--engine coqui` or `--engine pyttsx3`
- See available voices (pyttsx3):
  - `python solution.py "Hello" out.wav --list-voices`
- Use a specific voice:
  - `python solution.py "Hello" out.wav --engine pyttsx3 --voice "Microsoft David Desktop"`

## Styles and Intensity
- Styles: `neutral`, `enthusiastic`, `somber`, `confident`, `authoritative`
- Intensity: `0–100`
- Not sure where to start? Try `neutral` at `60`—it’s clear and natural.

## Handy Flags
- `--status` shows which engine is active and what voices are detected.
- `--verbose` prints extra logs for debugging.
- The script saves a small JSON next to your WAV with segment timings and style info—handy for long narration.

## If Something Acts Up
- Coqui/Torch installs can be finicky. Installing `torch`/`torchaudio` first often helps; some setups need CPU-only wheels.
- If Coqui isn’t available, pyttsx3 steps in automatically.
- Windows voices differ by machine—list voices, then pick one that sounds right.

## How It Works (no buzzwords)
- We split your text into natural chunks and clean up numbers, acronyms, and names.
- We plan the delivery: speed, energy, pitch, pauses, emphasis.
- Coqui TTS tries to sound expressive and human; pyttsx3 is the trusty backup.
- Audio gets gently smoothed so volumes match and joins don’t feel abrupt.

## Why Two Engines?
- Coqui TTS gives richer emotion and more natural prosody.
- pyttsx3 ensures you always get an output—great for quick tests and low-spec machines.
- You don’t have to choose; the tool picks Coqui if available and falls back without drama.

## Requirements
Check `requirements.txt` for both minimal and full installs.
- Minimal: `pyttsx3`, `comtypes`, `pywin32`
- Full: `torch`, `torchaudio`, `TTS` (Coqui), plus the minimal set above

## License and Good Sense
- Please respect consent and licensing for voices.
- Intended for narration, demos, and learning.

## Final Tip
I’d suggest starting simple: get pyttsx3 working, make sure the narration feels right, then add Coqui TTS when you want more expression. And if anything’s unclear, `--status` and `--verbose` will help us troubleshoot together.