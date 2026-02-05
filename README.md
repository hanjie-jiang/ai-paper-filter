# AI Paper Daily Debrief Agent

A self-contained application that provides personalized AI research paper recommendations based on user interests. Built with Qwen LLM for intelligent paper analysis and ranking.

## Features

- **Personalized Recommendations**: Analyzes user research interests and pain points
- **Smart Filtering**: Uses AI to score papers on novelty, results, and completeness
- **Duplicate Detection**: Semantic search to avoid showing similar papers
- **Beautiful Reports**: Generates HTML dashboards with visual metrics
- **Long-term Memory**: Remembers papers user've seen to prevent duplicates
- **Edge-Ready**: Runs locally on CPU/GPU/MPS (Apple Silicon)

## Project Structure

```
ai-paper-filter/
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── brain.py           # AI reasoning engine (Qwen LLM)
│   ├── tools.py           # Web scraping utilities
│   ├── archive.py         # Long-term paper memory
│   ├── curator.py         # Relevance matching
│   ├── pipeline.py        # Main orchestrator
│   └── report_generator.py # HTML report builder
├── data/
│   └── paper_memory.json  # Archive of seen papers
└── output/
    ├── daily_briefing.json
    └── daily_briefing.html
```

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/ai-paper-filter
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Using venv (Python 3.8+)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using conda
conda create -n paper-filter python=3.10
conda activate paper-filter
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First run will download:
- Qwen 14B model (~8GB) - for paper analysis
- Sentence transformer model (~80MB) - for semantic search

## Usage

### Basic Command

```bash
python main.py --prompt "I work on machine learning and am interested in AI agents and RAG systems"
```

### All Options

```bash
python main.py \
  --prompt "Your research interests here" \
  --date "2024-01-05" \
  --max-papers 10 \
  --output-dir "./my_results" \
  --db-path "./my_archive.json"
```

### Arguments Explained

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--prompt` | Yes | - | Your research interests and pain points |
| `--date` | No | Latest | Target date (YYYY-MM-DD). Weekends auto-adjust to Friday |
| `--max-papers` | No | 6 | Number of papers to analyze |
| `--output-dir` | No | `output/` | Where to save reports |
| `--db-path` | No | `data/paper_memory.json` | Archive database path |
| `--no-html` | No | False | Skip HTML generation (JSON only) |

### Example Commands

**1. Get latest papers on AI agents:**
```bash
python main.py --prompt "AI agents, autonomous systems, and tool use"
```

**2. Check papers from a specific date:**
```bash
python main.py --prompt "RAG and retrieval systems" --date "2024-01-05"
```

**3. Analyze more papers with custom output:**
```bash
python main.py \
  --prompt "I work on legal AI and need papers on document understanding" \
  --max-papers 15 \
  --output-dir "./legal_papers"
```

**4. Describe your pain points for better matching:**
```bash
python main.py --prompt "I work on package pricing ML and am interested in AI agent applications that improve efficiency. I need groundbreaking applications but NOT image generation or crypto papers"
```

## How It Works

### Pipeline Flow

```
1. User Prompt → [Brain: Intent Analysis]
   Extracts: interests, context, pain points, negative keywords

2. Fetch Papers → [Perception Tools]
   Gets latest papers from Hugging Face Daily Papers API

3. For each paper:
   a. [Brain: Think] - Analyze & score (0-10 scale)
   b. [Archive: Check] - Compare against history
   c. [Curator: Match] - Calculate relevance to your interests
   d. [Brain: Hook] - Generate personalized "why it matters"

4. Ranking → Priority = Quality + (Relevance × 20) + Topic Bonus

5. Output → Top 3 papers with visual metrics
```

### Scoring Rubric (The Brain is Strict!)

**Novelty (0-4 points)**
- 1 = Minor variation
- 2 = Good combination of techniques
- 3 = Significant architectural change
- 4 = Paradigm shift (very rare)

**Results (0-3 points)**
- 1 = Matches SOTA
- 2 = Clear improvement
- 3 = Beats SOTA by >10%

**Completeness (0-3 points)**
- 0 = No code
- 1 = "Code will be released"
- 2 = GitHub link provided
- 3 = Full reproducible code + ablations

**Quality Threshold**: Papers scoring < 6/10 are automatically rejected.

## Output Files

### 1. JSON Output (`daily_briefing.json`)
```json
{
  "user_intent": ["AI agents", "RAG"],
  "timestamp": "2024-01-05",
  "cards": [
    {
      "rank": 1,
      "title": "Paper Title",
      "tldr": "One sentence summary",
      "personalized_reason": "Why this matters to you",
      "raw_novelty": 3,
      "raw_results": 2,
      "raw_completeness": 2,
      "badges": ["Top Pick", "Topic Match"],
      "read_link": "https://huggingface.co/papers/..."
    }
  ]
}
```

### 2. HTML Report (`daily_briefing.html`)
Beautiful dashboard with:
- Visual metric bars
- Badge indicators
- Personalized explanations
- Direct paper links

Open in any browser - no server needed!

## Hardware Requirements

### Minimum (CPU Only)
- 16GB RAM
- ~10GB free disk space
- Runtime: ~5-10 min for 6 papers

### Recommended (GPU)
- NVIDIA GPU with 8GB+ VRAM (CUDA)
- OR Apple Silicon Mac (MPS)
- Runtime: ~2-3 min for 6 papers

### Model Customization
To use a smaller/faster model, edit `src/brain.py` line 62:
```python
# Default (14B model - high quality)
def __init__(self, model_path="Qwen/Qwen2.5-14B-Instruct"):

# Alternative (7B model - faster)
def __init__(self, model_path="Qwen/Qwen2.5-7B-Instruct"):
```

## Troubleshooting

### Issue: "Out of Memory" Error
**Solution**: Use the 7B model (see Model Customization above) or reduce `--max-papers`

### Issue: "Abstract not found" for all papers
**Solution**: Check your internet connection. HuggingFace might be rate-limiting. Wait a few minutes.

### Issue: Weekend dates show no papers
**Solution**: This is expected! The tool automatically slides Sat/Sun to Friday. ArXiv doesn't publish on weekends.

### Issue: "No papers matched your criteria"
**Solutions**:
1. Use broader keywords (e.g., "machine learning" instead of "meta-learning for few-shot RL")
2. Try `--max-papers 15` to analyze more candidates
3. Remove negative keywords that might be too restrictive

## Advanced Usage

### Use as a Library in Your Code

```python
from src.pipeline import ResearchPipeline
from src.report_generator import generate_html_report

# Initialize
pipeline = ResearchPipeline(db_path="./my_archive.json")

# Run
result = pipeline.run(
    user_prompt_text="AI agents and tool use",
    target_date="2024-01-05",
    max_papers=10
)

# Generate report
generate_html_report(result, output_path="./my_report.html")
```

### Customize Filtering Logic

Edit `src/pipeline.py` line 107-109 to change quality threshold:
```python
# Current: Reject papers scoring < 6/10
if insight.score < 6:
    print(f"  Rejected: Low quality score ({insight.score}/10)")
    continue

# Change to be more lenient (accept 5+)
if insight.score < 5:
```

### Customize Relevance Threshold

Edit `src/pipeline.py` line 122 to change relevance cutoff:
```python
# Current: Only show papers with >0.2 relevance
if relevance > 0.2:

# Change to be stricter (only highly relevant papers)
if relevance > 0.5:
```

## Contributing

This is a personal project, but feel free to fork and adapt for your needs!

## Credits

- **LLM**: Qwen 2.5 by Alibaba Cloud
- **Embeddings**: all-MiniLM-L6-v2 by Sentence-Transformers
- **Data Source**: Hugging Face Daily Papers

## License

MIT License - Use freely for personal or commercial projects.

---

**Built for researchers who want smarter paper discovery**
