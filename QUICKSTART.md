# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd /path/to/ai-paper-filter

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## First Run (2 minutes)

```bash
# Test installation
python test_basic.py

# Run with your interests
python main.py --prompt "I work on machine learning and AI agents"
```

## View Results

```bash
# Open the HTML report in your browser
open output/daily_briefing.html  # macOS
xdg-open output/daily_briefing.html  # Linux
start output/daily_briefing.html  # Windows
```

## Common Commands

### Get latest papers
```bash
python main.py --prompt "Your interests here"
```

### Get papers from specific date
```bash
python main.py --prompt "Your interests" --date "2024-01-05"
```

### Analyze more papers (slower but more results)
```bash
python main.py --prompt "Your interests" --max-papers 15
```

### Save to custom location
```bash
python main.py --prompt "Your interests" --output-dir "./my_papers"
```

## Troubleshooting

### Out of Memory?
Edit `src/brain.py` line 62 and change to 7B model:
```python
def __init__(self, model_path="Qwen/Qwen2.5-7B-Instruct"):
```

### No papers found?
- Use broader keywords
- Try `--max-papers 15`
- Check a different date with `--date`

### Slow performance?
- First run downloads models (one-time, ~8GB)
- Subsequent runs are faster
- Use GPU if available (CUDA/MPS)

## What Gets Downloaded on First Run?

1. **Qwen 14B Model** (~8GB)
   - Location: `~/.cache/huggingface/`
   - Used for: Paper analysis
   - One-time download

2. **Sentence Transformer** (~80MB)
   - Location: `~/.cache/torch/`
   - Used for: Semantic similarity
   - One-time download

## Need Help?

Check the full README.md for detailed documentation.
