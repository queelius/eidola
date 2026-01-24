"""Write persona directory structure."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..config import Config
from ..models import Voice
from ..rag import RAGIndex


class PersonaWriter:
    """Writes the persona output directory structure.

    Creates:
    - README.md
    - manifest.json
    - system-prompt.txt
    - voice-samples.jsonl
    - approaches/rag/
    - approaches/voice/ (if voice input provided)
    """

    def __init__(self, config: Config, input_path: Optional[Path] = None):
        self.config = config
        self.input_path = input_path

    def write(
        self,
        output_path: Path,
        rag_index: Optional[RAGIndex] = None,
        source_counts: Optional[Dict[str, int]] = None,
        voices: Optional[List[Voice]] = None,
    ) -> None:
        """Write the persona directory.

        Args:
            output_path: Path to output directory
            rag_index: RAG index to save
            source_counts: Count of sources by type
            voices: Voice recordings to include
        """
        output_path.mkdir(parents=True, exist_ok=True)

        source_counts = source_counts or {}
        voices = voices or []

        # Write core files
        self._write_readme(output_path, source_counts, len(voices) > 0)
        self._write_manifest(output_path, source_counts, len(voices) > 0)
        self._write_system_prompt(output_path)
        self._write_voice_samples(output_path)

        # Write RAG approach
        if rag_index and self.config.rag.enabled:
            rag_path = output_path / "approaches" / "rag"
            rag_index.save(rag_path)
            self._write_rag_readme(rag_path)

        # Write voice approach
        if voices and self.config.voice.enabled:
            voice_path = output_path / "approaches" / "voice"
            self._write_voice_directory(voice_path, voices)

    def _write_readme(
        self, path: Path, source_counts: Dict[str, int], has_voice: bool = False
    ) -> None:
        """Write the persona README.md."""
        sources_str = ", ".join(
            f"{count} {source}s" if count != 1 else f"{count} {source}"
            for source, count in source_counts.items()
            if count > 0
        )

        voice_section = ""
        if has_voice:
            voice_section = """
5. **Voice** (approaches/voice/) - Voice cloning and speech synthesis
   - Reference audio clips for voice cloning
   - Supports Chroma, RVC, XTTS, F5-TTS
   - Transcripts for speech-aware RAG
"""

        content = f"""# {self.config.persona_name} - Digital Persona

Generated: {datetime.now().strftime("%Y-%m-%d")}
Source: {sources_str or "No sources"}

## Quick Start

Use the system prompt in `system-prompt.txt` with any LLM.
For better results, enable one or more enhancement approaches.

## Contents

- system-prompt.txt - Works with any LLM (Claude, GPT, Gemini, Llama, Ollama)
- voice-samples.jsonl - Few-shot examples for improved voice fidelity
- approaches/ - Enhancement methods (RAG, infinigram, fine-tune, tools, voice)

## Approaches (Choose One or More)

1. **RAG** (approaches/rag/) - Retrieval-augmented generation
   - Semantic search over all content
   - Grounded responses with citations

2. **Infinigram** (approaches/infinigram/) - Probability mixing (RECOMMENDED)
   - Mix infinigram n-gram probabilities with LLM output
   - ~70% perplexity reduction on personal style
   - Serve via REST API for any provider

3. **Fine-tune** (approaches/fine-tune/) - Model-specific training
   - Highest voice fidelity but model-dependent
   - Formats for OpenAI, Llama/Alpaca

4. **Tools** (approaches/tools/) - Dynamic context via MCP
   - Real-time retrieval during conversation
   - Works with MCP-compatible clients
{voice_section}
## Graceful Degradation

If technical formats become obsolete:
- system-prompt.txt is plain text, always readable
- voice-samples.jsonl is standard JSON
- Source data lives in ctk, mtk, btk, ptk, ebk exports
- README.md documents reconstruction

## Voice Characteristics

{self.config.persona_description or "Voice characteristics not specified."}
"""
        (path / "README.md").write_text(content, encoding="utf-8")

    def _write_manifest(
        self, path: Path, source_counts: Dict[str, int], has_voice: bool = False
    ) -> None:
        """Write the manifest.json."""
        manifest = {
            "version": "1.0",
            "name": self.config.persona_name,
            "generated": datetime.now().isoformat(),
            "sources": {
                source: {"count": count} for source, count in source_counts.items()
            },
            "approaches": {
                "rag": self.config.rag.enabled,
                "infinigram": self.config.infinigram.enabled,
                "fine_tune": self.config.fine_tune.enabled,
                "tools": self.config.tools.enabled,
                "voice": self.config.voice.enabled and has_voice,
            },
            "echo_compliant": self.config.echo.enabled,
        }

        (path / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def _get_identity_description(self) -> str:
        """Get the identity description for the system prompt."""
        if self.config.persona_description:
            return self.config.persona_description
        name = self.config.persona_name
        return (
            f"{name} is a person whose thoughts, values, "
            "and voice are captured in this archive."
        )

    def _write_system_prompt(self, path: Path) -> None:
        """Write the system-prompt.txt."""
        name = self.config.persona_name
        content = f"""You are speaking as {name}'s digital echo - a conversable archive
of their thinking, values, and voice.

## Identity

{self._get_identity_description()}

## Voice

- Direct and clear
- Uses concrete examples
- Comfortable saying "I don't know" or "I might be wrong"

## Boundaries

- Don't claim to be conscious or to have current experiences
- Don't speculate wildly beyond known views
- Be honest about being an echo, not the person
- Refer to professional help for medical/legal/crisis questions

When responding, draw on the style and substance of the conversations
and writings, but acknowledge uncertainty when you're extrapolating.
"""
        (path / "system-prompt.txt").write_text(content, encoding="utf-8")

    def _write_voice_samples(self, path: Path) -> None:
        """Write initial voice-samples.jsonl (empty, to be populated)."""
        # Placeholder - in a full implementation, this would extract
        # representative Q&A pairs from conversations
        (path / "voice-samples.jsonl").write_text("", encoding="utf-8")

    def _write_rag_readme(self, path: Path) -> None:
        """Write README for RAG approach."""
        content = """# RAG (Retrieval-Augmented Generation)

This directory contains the vector index for semantic search over personal content.

## Contents

- `index.faiss` - FAISS vector index
- `chunks.jsonl` - Text chunks with embeddings
- `metadata.json` - Index metadata and configuration

## Usage

Load the index and search:

```python
from longshade.rag import RAGIndex

index = RAGIndex.load("./")
results = index.search("What do you think about X?", k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['chunk'].text}")
    if 'context' in result:
        print("Context:", result['context'])
```

## Chunking Strategy

- Conversations: Turn-level indexing with context expansion
- Writings: Paragraph-level chunks
- Emails: Full body as single chunk
- Bookmarks: Annotation only
- Photos: Caption only
- Reading: Review and highlighted notes
- Voice: Transcript or caption as single chunk

## Context Expansion

For conversation chunks, surrounding context (±3 turns by default)
is retrieved along with the matching turn.
"""
        (path / "README.md").write_text(content, encoding="utf-8")

    def _write_voice_directory(self, path: Path, voices: List[Voice]) -> None:
        """Write the voice approach directory.

        Creates:
        - README.md - Usage instructions
        - reference-clips/ - Best clips for voice cloning
        - transcripts.jsonl - All transcripts for text RAG
        - chroma/ - Chroma-specific format
        - rvc/ - RVC-specific format
        - xtts/ - XTTS-specific format
        - fine-tune/ - Audio model fine-tuning data
        """
        path.mkdir(parents=True, exist_ok=True)

        # Select best reference clips based on duration
        reference_clips = self._select_reference_clips(voices)

        # Write main README
        self._write_voice_readme(path, voices, reference_clips)

        # Write transcripts
        self._write_voice_transcripts(path, voices)

        # Write reference clips manifest
        self._write_reference_clips(path, reference_clips)

        # Write format-specific subdirectories
        for fmt in self.config.voice.formats:
            if fmt == "chroma":
                self._write_chroma_format(path / "chroma", reference_clips)
            elif fmt == "rvc":
                self._write_rvc_format(path / "rvc", reference_clips)
            elif fmt == "xtts":
                self._write_xtts_format(path / "xtts", reference_clips)

        # Write fine-tune data
        self._write_voice_finetune(path / "fine-tune", voices)

    def _select_reference_clips(self, voices: List[Voice]) -> List[Voice]:
        """Select the best reference clips for voice cloning.

        Criteria:
        - Has duration >= min_duration
        - Prefer clips with transcripts
        - Limit to max_reference_clips
        """
        min_duration = self.config.voice.min_duration
        max_clips = self.config.voice.max_reference_clips

        # Filter by minimum duration
        candidates = [
            v for v in voices if v.duration and v.duration >= min_duration
        ]

        # Sort by preference: has transcript, then by duration (longer is better)
        candidates.sort(
            key=lambda v: (v.transcript is not None, v.duration or 0),
            reverse=True,
        )

        return candidates[:max_clips]

    def _write_voice_readme(
        self, path: Path, voices: List[Voice], reference_clips: List[Voice]
    ) -> None:
        """Write README for voice approach."""
        total_duration = sum(v.duration or 0 for v in voices)
        transcribed_count = sum(1 for v in voices if v.transcript)

        content = f"""# Voice Cloning and Speech Synthesis

This directory contains reference audio and training data for voice cloning.

## Overview

- **Total clips**: {len(voices)}
- **Total duration**: {total_duration:.1f} seconds ({total_duration / 60:.1f} minutes)
- **With transcripts**: {transcribed_count}
- **Reference clips selected**: {len(reference_clips)}

## Quick Start

Minimal example to synthesize speech in the persona's voice:

```bash
# Install a TTS system (choose one)
pip install TTS                  # XTTS (recommended)
pip install chroma-tts           # Chroma TTS
pip install openvoice            # OpenVoice

# Generate speech
python -c "
from TTS.api import TTS
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
tts.tts_to_file('Hello, this is my voice.', speaker_wav='reference-clips/sample-001.wav', language='en', file_path='output.wav')
"
```

## Contents

- `reference-clips/` - Best clips for zero-shot voice cloning
- `transcripts.jsonl` - All transcripts for speech-aware RAG
- `chroma/` - Chroma TTS format
- `rvc/` - RVC (Retrieval-based Voice Conversion) format
- `xtts/` - Coqui XTTS format
- `fine-tune/` - Audio model fine-tuning data

## Installation

### XTTS v2 (Recommended)

```bash
pip install TTS

# Or with GPU support
pip install TTS torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
```

### Chroma TTS

```bash
pip install chroma-tts
```

### F5-TTS

```bash
pip install f5-tts
# Or from source:
git clone https://github.com/SWivid/F5-TTS
cd F5-TTS && pip install -e .
```

### OpenVoice

```bash
pip install openvoice
# Or from source:
git clone https://github.com/myshell-ai/OpenVoice
cd OpenVoice && pip install -e .
```

### RVC (Fine-tuning)

```bash
# RVC requires manual setup - see rvc/README.md
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
```

## End-to-End Workflow

Generate text with an LLM, then synthesize with the persona's voice:

```python
import anthropic
from TTS.api import TTS

# 1. Generate response with Claude
client = anthropic.Anthropic()
with open("../../system-prompt.txt") as f:
    system_prompt = f.read()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=system_prompt,
    messages=[{{"role": "user", "content": "What's your take on learning new skills?"}}]
)
text = response.content[0].text

# 2. Synthesize speech in persona's voice
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text=text,
    speaker_wav="reference-clips/sample-001.wav",
    language="en",
    file_path="response.wav"
)
print(f"Saved speech to response.wav")
```

## Supported Systems

| System | Type | Quality | Data Needed | GPU Required |
|--------|------|---------|-------------|--------------|
| XTTS v2 | Zero-shot | Great | 6-30 sec reference | Recommended |
| Chroma TTS | Zero-shot | Great | 6-30 sec reference | Recommended |
| F5-TTS | Zero-shot | Great | 15 sec reference | Required |
| OpenVoice | Zero-shot | Good | 30 sec reference | Recommended |
| RVC | Fine-tuned | Excellent | 10-30 min training | Required |
| ElevenLabs | Cloud API | Excellent | 30 sec reference | No |

### XTTS v2

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Basic synthesis
tts.tts_to_file(
    text="Hello, this is my voice.",
    speaker_wav="reference-clips/sample-001.wav",
    language="en",
    file_path="output.wav"
)

# With multiple reference clips for better quality
tts.tts_to_file(
    text="Hello, this is my voice.",
    speaker_wav=["reference-clips/sample-001.wav", "reference-clips/sample-002.wav"],
    language="en",
    file_path="output.wav"
)

# Streaming synthesis
for chunk in tts.tts_stream(
    text="Long text to synthesize...",
    speaker_wav="reference-clips/sample-001.wav",
    language="en"
):
    # Process audio chunk
    pass
```

### F5-TTS

```python
from f5_tts.api import F5TTS

# Initialize
tts = F5TTS()

# Synthesize
audio = tts.infer(
    ref_file="reference-clips/sample-001.wav",
    ref_text="Transcript of the reference audio if available",
    gen_text="Text you want the persona to say",
    model="F5-TTS",  # or "E2-TTS"
)

# Save
import soundfile as sf
sf.write("output.wav", audio, 24000)
```

### OpenVoice

```python
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

# Extract voice characteristics
ckpt_converter = "checkpoints/converter"
tone_color_converter = ToneColorConverter(ckpt_converter)
source_se = se_extractor.get_se(
    "reference-clips/sample-001.wav",
    tone_color_converter,
    target_dir="processed_voices"
)

# Convert any TTS output to persona's voice
tone_color_converter.convert(
    audio_src_path="base_tts_output.wav",
    src_se=base_speaker_embedding,
    tgt_se=source_se,
    output_path="output.wav"
)
```

### ElevenLabs (Cloud API)

```python
from elevenlabs import generate, clone, set_api_key
import os

set_api_key(os.environ["ELEVENLABS_API_KEY"])

# Clone voice from reference audio
voice = clone(
    name="{self.config.persona_name}",
    files=["reference-clips/sample-001.wav", "reference-clips/sample-002.wav"],
)

# Generate speech
audio = generate(
    text="Hello, this is my voice.",
    voice=voice,
)

with open("output.mp3", "wb") as f:
    f.write(audio)
```

## Three Approaches

### 1. Voice Cloning (Zero-Shot)

Use reference clips directly with voice cloning systems. No training required.
Best for quick setup with good quality.

### 2. Fine-Tuning

Train a dedicated voice model on the provided data. See `rvc/README.md`.
Best for highest quality when you have 10+ minutes of audio.

### 3. Speech RAG

Transcripts are indexed in the RAG system. Use for context-aware generation:

```python
# Search for relevant speech context
results = rag_index.search("topic of interest", source_filter="voice")
for result in results:
    print(f"The persona said: {{result['chunk'].text}}")
```

## Philosophy

This directory stores **data**, not trained models:
- Reference audio clips work with any voice cloning system
- Training data can be used with future systems
- Transcripts provide searchable content
"""
        (path / "README.md").write_text(content, encoding="utf-8")

    def _write_voice_transcripts(self, path: Path, voices: List[Voice]) -> None:
        """Write all transcripts to JSONL."""
        transcripts_path = path / "transcripts.jsonl"

        with open(transcripts_path, "w", encoding="utf-8") as f:
            for voice in voices:
                if voice.transcript or voice.caption:
                    record = {
                        "path": voice.path,
                        "text": voice.transcript or voice.caption,
                        "is_transcript": voice.transcript is not None,
                        "duration": voice.duration,
                        "context": voice.context,
                        "timestamp": (
                            voice.timestamp.isoformat() if voice.timestamp else None
                        ),
                    }
                    f.write(json.dumps(record) + "\n")

    def _write_reference_clips(self, path: Path, reference_clips: List[Voice]) -> None:
        """Write reference clips manifest and copy audio files if available."""
        clips_dir = path / "reference-clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        manifest = []
        for i, voice in enumerate(reference_clips):
            clip_info = {
                "id": f"sample-{i + 1:03d}",
                "original_path": voice.path,
                "duration": voice.duration,
                "transcript": voice.transcript,
                "context": voice.context,
                "language": voice.language,
            }
            manifest.append(clip_info)

            # Copy audio file if input_path is set and file exists
            if self.input_path:
                source_audio = self.input_path / "voice" / voice.path
                if source_audio.exists():
                    dest_name = f"sample-{i + 1:03d}{source_audio.suffix}"
                    shutil.copy2(source_audio, clips_dir / dest_name)
                    clip_info["copied_as"] = dest_name

        (clips_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def _write_chroma_format(self, path: Path, reference_clips: List[Voice]) -> None:
        """Write Chroma TTS-specific format."""
        path.mkdir(parents=True, exist_ok=True)

        readme = """# Chroma TTS Format

Reference audio for Chroma TTS voice cloning.

## Installation

```bash
pip install chroma-tts

# With GPU support
pip install chroma-tts torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
```

## Quick Start

```python
from chroma_tts import ChromaTTS

# Initialize
tts = ChromaTTS()

# Load voice from reference audio
tts.load_voice("../reference-clips/sample-001.wav")

# Synthesize speech
audio = tts.synthesize("Hello, this is my voice.")

# Save to file
audio.save("output.wav")
```

## Detailed Usage

### Basic Synthesis

```python
from chroma_tts import ChromaTTS

tts = ChromaTTS()

# Load from single reference
tts.load_voice("../reference-clips/sample-001.wav")

# Synthesize
audio = tts.synthesize(
    text="The text you want to convert to speech.",
    speed=1.0,           # Speech rate (0.5-2.0)
    emotion="neutral",   # neutral, happy, sad, angry
)
audio.save("output.wav")
```

### Multiple Reference Clips

Using multiple clips can improve voice quality:

```python
from chroma_tts import ChromaTTS
from pathlib import Path

tts = ChromaTTS()

# Load multiple references
reference_clips = list(Path("../reference-clips").glob("*.wav"))
tts.load_voice(reference_clips)

# Synthesize with combined voice profile
audio = tts.synthesize("Hello, this is my voice.")
```

### Streaming Synthesis

For long texts, use streaming to start playback earlier:

```python
from chroma_tts import ChromaTTS

tts = ChromaTTS()
tts.load_voice("../reference-clips/sample-001.wav")

# Stream audio chunks
for chunk in tts.synthesize_stream("Long text to synthesize..."):
    # Process or play chunk
    chunk.play()  # Or write to file
```

### Integration with LLM

Complete workflow from text generation to speech:

```python
import anthropic
from chroma_tts import ChromaTTS

# Initialize
client = anthropic.Anthropic()
tts = ChromaTTS()
tts.load_voice("../reference-clips/sample-001.wav")

# Load persona's system prompt
with open("../../../system-prompt.txt") as f:
    system_prompt = f.read()

# Generate response
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "Tell me about yourself."}]
)

# Synthesize speech
text = response.content[0].text
audio = tts.synthesize(text)
audio.save("response.wav")
```

## Files

- `config.yaml` - Voice configuration (name, clip count, total duration)
- `../reference-clips/` - Reference audio files
"""
        (path / "README.md").write_text(readme, encoding="utf-8")

        # Write config
        config = {
            "name": self.config.persona_name,
            "clips": len(reference_clips),
            "total_duration": sum(v.duration or 0 for v in reference_clips),
        }
        import yaml

        (path / "config.yaml").write_text(
            yaml.safe_dump(config, default_flow_style=False), encoding="utf-8"
        )

    def _write_rvc_format(self, path: Path, reference_clips: List[Voice]) -> None:
        """Write RVC-specific format."""
        path.mkdir(parents=True, exist_ok=True)
        (path / "training-samples").mkdir(exist_ok=True)

        readme = """# RVC (Retrieval-based Voice Conversion) Format

Training data for RVC voice model. RVC provides the highest quality voice
cloning but requires training a custom model.

## Requirements

- 10-30 minutes of clean audio (more is better)
- Clips split into 10-15 second segments
- 48kHz WAV format preferred
- Single speaker, minimal background noise
- GPU with 8GB+ VRAM for training

## Installation

```bash
# Clone RVC repository
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
cd Retrieval-based-Voice-Conversion-WebUI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download pretrained models (required)
python tools/download_models.py
```

## Audio Preprocessing

Before training, preprocess your audio for best results:

```bash
# Install preprocessing tools
pip install pydub ffmpeg-python

# Preprocess script
python - << 'EOF'
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

input_dir = Path("training-samples")
output_dir = Path("processed-samples")
output_dir.mkdir(exist_ok=True)

for audio_file in input_dir.glob("*.wav"):
    # Load and normalize
    audio = AudioSegment.from_wav(audio_file)
    audio = audio.set_frame_rate(48000)
    audio = audio.set_channels(1)

    # Normalize volume
    target_dBFS = -20
    change_in_dBFS = target_dBFS - audio.dBFS
    audio = audio.apply_gain(change_in_dBFS)

    # Split on silence (10-15 sec segments)
    chunks = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=-40,
        keep_silence=200
    )

    # Export chunks
    for i, chunk in enumerate(chunks):
        if 3000 < len(chunk) < 15000:  # 3-15 seconds
            chunk.export(output_dir / f"{audio_file.stem}_{i:03d}.wav", format="wav")

print(f"Processed {len(list(output_dir.glob('*.wav')))} segments")
EOF
```

## Training

### Using Web UI

```bash
cd Retrieval-based-Voice-Conversion-WebUI

# Start web interface
python infer-web.py

# Then in browser:
# 1. Go to "Train" tab
# 2. Enter experiment name
# 3. Upload audio from processed-samples/
# 4. Click "Process Data"
# 5. Click "Train Model"
```

### Using Command Line

```bash
cd Retrieval-based-Voice-Conversion-WebUI

# Copy training samples to dataset folder
mkdir -p datasets/persona_voice
cp processed-samples/*.wav datasets/persona_voice/

# Preprocess
python trainset_preprocess_pipeline_print.py \\
    datasets/persona_voice \\
    48000 \\
    4  # Number of CPU threads

# Extract features
python extract_f0_print.py \\
    logs/persona_voice \\
    4 \\
    harvest  # f0 extraction method: harvest, pm, dio

python extract_feature_print.py \\
    logs/persona_voice \\
    4

# Train
python train_nsf_sim_cache_sid_load_pretrain.py \\
    -e persona_voice \\
    -sr 48k \\
    -f0 1 \\
    -bs 8 \\
    -te 200 \\
    -se 50
```

### Training Parameters

| Parameter | Recommended | Description |
|-----------|-------------|-------------|
| Sample rate | 48k | Use 48k for best quality |
| Batch size | 8 | Reduce if OOM errors |
| Epochs | 200-500 | More for better quality |
| Save frequency | 50 | Save checkpoint every N epochs |

## Inference (After Training)

```python
# Using the trained model
from infer_pack.models import SynthesizerTrnMs256NSFsid
import torch

# Load model
model_path = "weights/persona_voice.pth"
index_path = "logs/persona_voice/added_IVF1024_Flat_nprobe_1.index"

# Convert any audio to persona's voice
# (See RVC documentation for full inference code)
```

### Using Web UI for Inference

```bash
# Start web interface
python infer-web.py

# In browser:
# 1. Go to "Inference" tab
# 2. Select trained model
# 3. Upload source audio (any voice)
# 4. Click "Convert"
```

### Integration Example

```python
# Complete pipeline: Generate text -> TTS -> Voice conversion
import anthropic
from TTS.api import TTS
import subprocess

# 1. Generate text
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=open("../../../system-prompt.txt").read(),
    messages=[{"role": "user", "content": "What do you think about AI?"}]
)
text = response.content[0].text

# 2. Generate base TTS (any voice)
base_tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
base_tts.tts_to_file(text, file_path="base_tts.wav")

# 3. Convert to persona's voice using RVC
subprocess.run([
    "python", "infer_cli.py",
    "--model", "weights/persona_voice.pth",
    "--index", "logs/persona_voice/added_IVF1024_Flat_nprobe_1.index",
    "--input", "base_tts.wav",
    "--output", "persona_voice.wav"
])
```

## Files

- `training-samples/` - Raw audio clips for training
- After training (in RVC directory):
  - `weights/persona_voice.pth` - Trained model
  - `logs/persona_voice/*.index` - Feature index for retrieval

## Tips

1. **Quality over quantity**: 10 minutes of clean audio beats 30 minutes of noisy audio
2. **Consistent recording**: Same microphone, room, and distance
3. **Varied speech**: Include different emotions and speech patterns
4. **Remove silence**: Trim silence from beginning/end of clips
5. **Check normalization**: All clips should have similar volume
"""
        (path / "README.md").write_text(readme, encoding="utf-8")

    def _write_xtts_format(self, path: Path, reference_clips: List[Voice]) -> None:
        """Write XTTS-specific format."""
        path.mkdir(parents=True, exist_ok=True)

        readme = """# XTTS (Coqui) Format

Reference audio for XTTS v2 voice cloning. XTTS provides excellent zero-shot
voice cloning with multilingual support.

## Installation

```bash
# Basic installation
pip install TTS

# With GPU support (recommended)
pip install TTS torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

# Verify installation
python -c "from TTS.api import TTS; print('XTTS ready')"
```

## Requirements

- 6-30 seconds of clear speech (10-20 sec optimal)
- WAV format, 22050 Hz or higher
- Single speaker, no background noise
- Clear articulation, natural pace

## Quick Start

```python
from TTS.api import TTS

# Load XTTS v2 model (downloads automatically on first use)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Synthesize speech
tts.tts_to_file(
    text="Hello, this is my voice.",
    speaker_wav="../reference-clips/sample-001.wav",
    language="en",
    file_path="output.wav"
)
```

## Detailed Usage

### Basic Synthesis

```python
from TTS.api import TTS

# Initialize (use GPU if available)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Simple synthesis
tts.tts_to_file(
    text="The text you want to convert to speech.",
    speaker_wav="../reference-clips/sample-001.wav",
    language="en",
    file_path="output.wav"
)
```

### Multiple Reference Clips

Using multiple clips improves voice consistency:

```python
from TTS.api import TTS
from pathlib import Path

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Collect all reference clips
reference_clips = list(Path("../reference-clips").glob("*.wav"))

# Use multiple references (up to 5-6 clips work well)
tts.tts_to_file(
    text="Hello, this is my voice.",
    speaker_wav=[str(clip) for clip in reference_clips[:5]],
    language="en",
    file_path="output.wav"
)
```

### Streaming Synthesis

For real-time applications or long texts:

```python
from TTS.api import TTS
import sounddevice as sd
import numpy as np

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Get audio as numpy array for streaming
audio = tts.tts(
    text="This is a long text that will be synthesized in one go...",
    speaker_wav="../reference-clips/sample-001.wav",
    language="en"
)

# Play directly
sd.play(np.array(audio), samplerate=24000)
sd.wait()
```

### Multilingual Support

XTTS supports multiple languages:

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Supported languages: en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko, hi

# English
tts.tts_to_file(
    text="Hello, how are you?",
    speaker_wav="../reference-clips/sample-001.wav",
    language="en",
    file_path="output_en.wav"
)

# Spanish (same voice, different language)
tts.tts_to_file(
    text="Hola, ¿cómo estás?",
    speaker_wav="../reference-clips/sample-001.wav",
    language="es",
    file_path="output_es.wav"
)
```

### GPU vs CPU

```python
from TTS.api import TTS

# GPU (recommended for production)
tts_gpu = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# CPU only (slower but works without CUDA)
tts_cpu = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
```

### Pre-compute Speaker Embedding

For repeated synthesis with the same voice, pre-compute the embedding:

```python
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torch

# Load model directly
config = XttsConfig()
config.load_json("path/to/xtts/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="path/to/xtts/")
model.cuda()

# Compute speaker embedding once
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
    audio_path=["../reference-clips/sample-001.wav", "../reference-clips/sample-002.wav"]
)

# Save embedding for reuse
torch.save({
    "gpt_cond_latent": gpt_cond_latent,
    "speaker_embedding": speaker_embedding
}, "speaker-embedding.pt")

# Reuse for synthesis
out = model.inference(
    text="Text to synthesize",
    language="en",
    gpt_cond_latent=gpt_cond_latent,
    speaker_embedding=speaker_embedding,
)
```

### Integration with LLM

Complete workflow from text generation to speech:

```python
import anthropic
from TTS.api import TTS

# Initialize
client = anthropic.Anthropic()
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Load persona's system prompt
with open("../../../system-prompt.txt") as f:
    system_prompt = f.read()

def generate_and_speak(user_message: str, output_file: str = "response.wav"):
    # Generate text response
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    text = response.content[0].text

    # Synthesize speech
    tts.tts_to_file(
        text=text,
        speaker_wav="../reference-clips/sample-001.wav",
        language="en",
        file_path=output_file
    )

    return text, output_file

# Use
text, audio_file = generate_and_speak("What's your philosophy on life?")
print(f"Response: {text}")
print(f"Audio saved to: {audio_file}")
```

### Batch Processing

For processing multiple texts efficiently:

```python
from TTS.api import TTS
from pathlib import Path

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

texts = [
    "First sentence to synthesize.",
    "Second sentence to synthesize.",
    "Third sentence to synthesize.",
]

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

for i, text in enumerate(texts):
    tts.tts_to_file(
        text=text,
        speaker_wav="../reference-clips/sample-001.wav",
        language="en",
        file_path=str(output_dir / f"output_{i:03d}.wav")
    )
```

## Files

- `speaker-embedding.json` - Metadata about reference clips
- `../reference-clips/` - Reference audio files

## Tips

1. **Reference quality matters**: Use clean, noise-free reference audio
2. **Optimal length**: 10-20 seconds works best (too short = poor quality, too long = slower)
3. **Multiple clips**: Using 2-5 clips often gives better results than one
4. **Match content**: Reference clips with varied speech (questions, statements) help
5. **GPU recommended**: CPU is 5-10x slower for synthesis
"""
        (path / "README.md").write_text(readme, encoding="utf-8")

        # Write speaker embedding placeholder
        embedding = {
            "format": "xtts_v2",
            "note": "Generate embedding using XTTS get_conditioning_latents()",
            "reference_clips": [v.path for v in reference_clips],
        }
        (path / "speaker-embedding.json").write_text(
            json.dumps(embedding, indent=2), encoding="utf-8"
        )

    def _write_voice_finetune(self, path: Path, voices: List[Voice]) -> None:
        """Write audio model fine-tuning data."""
        path.mkdir(parents=True, exist_ok=True)

        transcribed_count = sum(1 for v in voices if v.transcript)
        total_duration = sum(v.duration or 0 for v in voices if v.transcript)

        readme = f"""# Audio Model Fine-Tuning Data

Training data for fine-tuning speech models.

## Overview

- **Transcribed clips**: {transcribed_count}
- **Total duration**: {total_duration:.1f} seconds ({total_duration / 60:.1f} minutes)

## File Formats

### chroma-format.jsonl

Text + audio pairs for Chroma TTS fine-tuning:

```json
{{"audio_path": "clips/sample-001.wav", "text": "Hello world", "duration": 10.5, "language": "en"}}
{{"audio_path": "clips/sample-002.wav", "text": "How are you", "duration": 8.2, "language": "en"}}
```

### whisper-format.jsonl

Transcription pairs for Whisper fine-tuning:

```json
{{"audio": "clips/sample-001.wav", "text": "Hello world", "language": "en"}}
{{"audio": "clips/sample-002.wav", "text": "How are you", "language": "en"}}
```

## Usage Examples

### Loading the Data

```python
import json
from pathlib import Path

# Load Chroma format
with open("chroma-format.jsonl") as f:
    chroma_data = [json.loads(line) for line in f]

print(f"Loaded {{len(chroma_data)}} training samples")
for sample in chroma_data[:3]:
    print(f"  {{sample['audio_path']}}: {{sample['text'][:50]}}...")
```

### Chroma TTS Fine-Tuning

```python
from chroma_tts import ChromaTTS
import json

# Load training data
with open("chroma-format.jsonl") as f:
    training_data = [json.loads(line) for line in f]

# Initialize model
tts = ChromaTTS()

# Fine-tune (API may vary - check Chroma documentation)
tts.fine_tune(
    training_data=training_data,
    audio_base_path="../../../input/voice/",  # Base path for audio files
    epochs=100,
    learning_rate=1e-4,
    save_path="finetuned_model/"
)

# Use fine-tuned model
tts_finetuned = ChromaTTS.load("finetuned_model/")
audio = tts_finetuned.synthesize("New text to speak")
```

### XTTS Fine-Tuning

```python
# XTTS fine-tuning requires the Coqui TTS training scripts
# See: https://github.com/coqui-ai/TTS/tree/dev/recipes/ljspeech

import json
from pathlib import Path

# Convert to XTTS format
with open("chroma-format.jsonl") as f:
    data = [json.loads(line) for line in f]

# Create metadata file for XTTS training
xtts_metadata = Path("xtts_metadata.txt")
with open(xtts_metadata, "w") as f:
    for sample in data:
        # Format: audio_path|text|speaker_name
        audio_path = Path(sample["audio_path"]).name
        text = sample["text"].replace("|", " ")
        f.write(f"{{audio_path}}|{{text}}|persona\\n")

print(f"Created XTTS metadata with {{len(data)}} samples")
```

### Whisper Fine-Tuning

Fine-tune Whisper for better transcription of the persona's voice:

```python
from datasets import Dataset
import json

# Load training data
with open("whisper-format.jsonl") as f:
    data = [json.loads(line) for line in f]

# Convert to HuggingFace Dataset format
dataset = Dataset.from_dict({{
    "audio": [d["audio"] for d in data],
    "text": [d["text"] for d in data],
    "language": [d["language"] for d in data],
}})

# Fine-tune with transformers
from transformers import WhisperForConditionalGeneration, WhisperProcessor, Seq2SeqTrainer

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
processor = WhisperProcessor.from_pretrained("openai/whisper-small")

# Training setup (simplified - see HuggingFace docs for full example)
trainer = Seq2SeqTrainer(
    model=model,
    train_dataset=dataset,
    # ... training arguments
)
trainer.train()
```

### Custom Training Script

Template for creating custom training pipelines:

```python
import json
from pathlib import Path
import torch
import torchaudio

def load_training_data(jsonl_path: str, audio_base_path: str):
    \"\"\"Load training data from JSONL file.\"\"\"
    samples = []
    with open(jsonl_path) as f:
        for line in f:
            sample = json.loads(line)
            audio_path = Path(audio_base_path) / sample["audio_path"]
            if audio_path.exists():
                waveform, sample_rate = torchaudio.load(audio_path)
                samples.append({{
                    "waveform": waveform,
                    "sample_rate": sample_rate,
                    "text": sample["text"],
                    "duration": sample["duration"],
                }})
    return samples

def create_dataloader(samples, batch_size=8):
    \"\"\"Create PyTorch DataLoader from samples.\"\"\"
    # Implement custom collation for variable-length audio
    # ...
    pass

# Example usage
training_data = load_training_data(
    "chroma-format.jsonl",
    "../../../input/voice/"
)
print(f"Loaded {{len(training_data)}} samples for training")
```

### Validate Training Data

Check data quality before training:

```python
import json
from pathlib import Path
import torchaudio

def validate_training_data(jsonl_path: str, audio_base_path: str):
    \"\"\"Validate that all training samples are accessible and valid.\"\"\"
    errors = []
    valid_count = 0
    total_duration = 0

    with open(jsonl_path) as f:
        for i, line in enumerate(f):
            sample = json.loads(line)
            audio_path = Path(audio_base_path) / sample["audio_path"]

            if not audio_path.exists():
                errors.append(f"Line {{i}}: Audio file not found: {{audio_path}}")
                continue

            try:
                waveform, sample_rate = torchaudio.load(audio_path)
                duration = waveform.shape[1] / sample_rate

                # Check duration matches
                if abs(duration - sample["duration"]) > 0.5:
                    errors.append(f"Line {{i}}: Duration mismatch: {{duration:.1f}} vs {{sample['duration']:.1f}}")

                valid_count += 1
                total_duration += duration
            except Exception as e:
                errors.append(f"Line {{i}}: Error loading audio: {{e}}")

    print(f"Valid samples: {{valid_count}}")
    print(f"Total duration: {{total_duration / 60:.1f}} minutes")
    if errors:
        print(f"Errors ({{len(errors)}}):")
        for err in errors[:10]:
            print(f"  {{err}}")

# Run validation
validate_training_data("chroma-format.jsonl", "../../../input/voice/")
```

## Tips

1. **Data quality**: Clean audio with accurate transcripts is essential
2. **Minimum data**: At least 30 minutes of transcribed audio recommended
3. **Varied content**: Include different speaking styles, emotions, topics
4. **Consistent recording**: Same microphone and room conditions preferred
5. **Accurate timestamps**: Verify transcripts match audio content
"""
        (path / "README.md").write_text(readme, encoding="utf-8")

        # Write Chroma format (text + audio pairs)
        with open(path / "chroma-format.jsonl", "w", encoding="utf-8") as f:
            for voice in voices:
                if voice.transcript:
                    record = {
                        "audio_path": voice.path,
                        "text": voice.transcript,
                        "duration": voice.duration,
                        "language": voice.language or "en",
                    }
                    f.write(json.dumps(record) + "\n")

        # Write Whisper format (transcription pairs)
        with open(path / "whisper-format.jsonl", "w", encoding="utf-8") as f:
            for voice in voices:
                if voice.transcript:
                    record = {
                        "audio": voice.path,
                        "text": voice.transcript,
                        "language": voice.language or "en",
                    }
                    f.write(json.dumps(record) + "\n")
