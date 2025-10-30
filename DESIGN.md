# Emotional Speech Generation — System Design (Conversational Guide)

Let’s imagine we’re sitting together with a cup of coffee. You type a line, press a button, and a friendly narrator speaks back—in the mood you asked for. That’s the idea. We’ll keep things practical, easy to run, and ready to grow when you want more expression.

## The Big Picture
- Turn your script into a clear, natural narration.
- Choose a mood: neutral, enthusiastic, somber, confident, or authoritative—and how strong it should feel.
- Use two engines so it “just works”: Coqui TTS for quality, pyttsx3 for reliability.

## How We’d Use It Together
1. You give me the text (plain or Markdown). We check it’s clean—no empty input.
2. We split into natural sentences so long paragraphs become breathable chunks.
3. We tidy details: numbers, dates, acronyms, special names—so pronunciation stays solid.
4. We plan delivery: speaking rate, energy, pitch range, pauses, where to emphasize.
5. We synthesize: Coqui TTS when available (expressive, neural). If not, pyttsx3 steps in without drama.
6. We polish the audio: a good vocoder (e.g., HiFi‑GAN), gentle de‑essing, loudness normalization, smooth joins.
7. We sanity‑check: quick ASR (Whisper) to catch obvious intelligibility issues.
8. We export: a WAV file plus a tiny JSON with style and segment timings.

Example (CLI):
- `python solution.py "Hello from our narrator" out.wav`
- `python solution.py "We did it!" out.wav --style enthusiastic --intensity 80`

## Why These Models?
### Coqui TTS (Primary)
- Natural prosody, offline after models are downloaded.
- Can steer emotion with style tokens/embeddings.
- Good docs and active community—easy to build on.

### pyttsx3 (Fallback)
- Works out of the box on Windows and starts fast.
- Lightweight and dependable—great for quick demos and low‑spec machines.
- Ensures you always get output even without GPU or big downloads.

### Where We Can Go Later
- **StyleTTS2** for fine‑grained control via textual prompts.
- **YourTTS** for zero‑shot voices and multilingual support.
- Classic **Tacotron2 + GST** if you prefer a familiar fine‑tuning path.

## Emotion Control, In Plain Words
- Pick a preset: neutral, enthusiastic, somber, confident, authoritative.
- Set intensity 0–100 to make delivery calmer or more energetic.
- Auto‑emphasize names, dates, keywords; add small hints if needed.
- Under the hood, presets map to style embeddings and prosody targets (pitch, rate, energy, pauses), with tiny variations so it never feels robotic.

## The Data That Helps
- Emotional speech: ESD, RAVDESS, EmoV‑DB, CREMA‑D, IEMOCAP.
- Long‑form narration: M‑AILABS English, LibriVox, VoxForge.
- If needed, curated documentary samples (respecting licensing).
- Aim for ~50+ hours per emotion to start; ~200+ hours for production‑level diversity.

## How We Judge Quality (Together)
- First, listen: MOS ratings, A/B preferences, “did the emotion come through?”
- Then measure: WER via Whisper, prosody stats (pitch/energy variance, pause patterns), synthesis speed.
- Goal: consistent style that feels natural—not over‑acted.

## Shipping Plan
- Today: a friendly CLI with clear flags.
  - `python solution.py "Hello" out.wav --style enthusiastic --intensity 70`
- Next: FastAPI `/synthesize` with a simple web button.
- Packaging: Docker for easy setup; optional GPU support.
- Caching: reuse identical segment + style outputs.

## Real‑World Quirks (We’ve Got Your Back)
- Acted emotion vs. real feeling: mix datasets, calibrate intensity, add human review for tricky parts.
- Long texts drifting in style: keep a style timeline, crossfade segments, monitor consistency.
- Tricky words: small lexicon, G2P fallback, user‑editable pronunciations.
- Emotion precision: gentle micro‑variations; avoid extremes that feel fake.
- Performance limits: pick fast models on CPU; rely on pyttsx3 when needed.
- Ethics: consent for voice cloning, clear usage terms, and sensible content rules.

## A Simple Path to Build This
**Phase 1 — MVP**
- Coqui TTS primary, pyttsx3 fallback.
- Pretrained English (VITS/FastPitch) + HiFi‑GAN.
- CLI with style and intensity.

**Phase 2 — Enhancements**
- Style tokens/conditioning for richer control.
- FastAPI + small web UI.
- Evaluate with MOS + ASR‑based WER.

**Phase 3 — Production**
- StyleTTS2 for fine‑grained prosody.
- Fine‑tune for documentary narrations.
- Dockerized deployment and cloud options.

**What “done” feels like**
- Dual engine works smoothly.
- MOS > 3.5 on emotional styles; WER < 5%.
- One‑command synthesis and docs anyone can follow.

## Wrap‑Up
If we were at a whiteboard, I’d say: start simple, make sure the narration feels right, and then dial up the fancy models. You’ll have something reliable on day one and a clear path to warm, expressive storytelling as you grow.