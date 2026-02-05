"""
Cognitive Brain Module - AI reasoning and analysis engine
"""
import torch
import json
import re
from typing import Type, List, Literal
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForCausalLM


class PaperInsight(BaseModel):
    """Schema for paper analysis results"""
    title: str = Field(..., description="Paper Title")
    one_liner: str = Field(..., description="One Sentence Summary (TL;DR)")
    key_innovation: str = Field(..., description="Major Innovation")
    sota_comparison: str = Field(..., description="SOTA data comparison")

    score_novelty: int = Field(..., description="0-4 pts: 0=Old, 4=New Arch/Loss")
    score_results: int = Field(..., description="0-3 pts: 0=No metrics, 3=Sig. SOTA beat")
    score_completeness: int = Field(..., description="0-3 pts: 0=Theory only, 3=Code+Benchmarks")

    score: int = Field(..., description="Sum of novelty + results + completeness (Total 0-10)")


class ComparativeAnalysis(BaseModel):
    """Schema for comparing papers"""
    topic_overlap_score: int = Field(..., description="0-10 score of semantic overlap", ge=0, le=10)
    innovation_type: Literal['None', 'Incremental', 'Breakthrough', 'Different_Field'] = Field(..., description="Type of innovation")
    has_quantitative_improvement: bool = Field(..., description="True only if specific metrics are better")
    reasoning_brief: str = Field(..., description="Max 20 words explanation")


class IntentSchema(BaseModel):
    """Schema for user intent analysis"""
    core_interests: List[str]
    context_tags: List[str]
    pain_points: List[str]
    negative_keywords: List[str]


class HookSchema(BaseModel):
    """Schema for personalized paper hooks"""
    reason: str


class ResearchProfile(BaseModel):
    """User research profile"""
    user_id: str
    interests: List[str]
    context_tags: List[str]
    pain_points: List[str]
    negative_keywords: List[str]


class CognitiveBrain:
    """
    AI reasoning engine powered by Qwen model.
    Handles paper analysis, comparison, and personalization.
    """

    def __init__(self, model_path="Qwen/Qwen2.5-7B-Instruct"):
        print(f"[Brain] Initializing Engine on {self._get_device()}...")
        self.device = self._get_device()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Use bfloat16 for CUDA or MPS (Apple Silicon), float32 for CPU only
        if torch.cuda.is_available() or torch.backends.mps.is_available():
            dtype = torch.bfloat16
        else:
            dtype = torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=dtype,
            device_map="auto"
        )
        print("[Brain] Ready.")

    def _get_device(self):
        """Detect available compute device"""
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _extract_json(self, text):
        """Extract JSON from model output, handling various formats"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            try:
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
        return None

    def _generate_json(self, system_prompt: str, user_prompt: str, schema_class: Type[BaseModel]):
        """Generate structured JSON output using the LLM"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                top_k=50
            )

        output_text = self.tokenizer.batch_decode(
            generated_ids[:, inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )[0]

        data_dict = self._extract_json(output_text)

        if data_dict:
            try:
                return {"status": "success", "data": schema_class(**data_dict)}
            except Exception as e:
                return {"status": "failed", "error": f"Validation: {str(e)}", "raw": output_text}
        else:
            return {"status": "failed", "error": "JSON Parsing Failed", "raw": output_text}

    def analyze_user_intent(self, user_prompt: str):
        """Extract research preferences from user's natural language input"""
        system = "You are an expert Librarian. Extract search metadata from the user's request. Output JSON only."
        user_content = (
            f"USER REQUEST: '{user_prompt}'\n\n"
            "Extract:\n"
            "1. core_interests (keywords)\n"
            "2. context_tags (field/domain)\n"
            "3. pain_points (problems to solve)\n"
            "4. negative_keywords (what to avoid)"
        )
        return self._generate_json(system, user_content, IntentSchema)

    def think(self, paper_text: str):
        """Analyze and grade a paper with strict academic standards"""
        scientist_instruction = (
            "You are an experienced ML researcher evaluating papers for quality and novelty.\n\n"
            "### TASK:\n"
            "Extract insights and grade this paper fairly.\n\n"
            "### SCORING RUBRIC:\n"
            "1. **NOVELTY (0-4)**\n"
            "   - 0: No novelty, trivial change.\n"
            "   - 1: Minor incremental improvement.\n"
            "   - 2: Good combination of techniques or clear new approach (MOST PAPERS).\n"
            "   - 3: Significant architectural or methodological innovation.\n"
            "   - 4: Paradigm shift or major breakthrough.\n\n"
            "2. **RESULTS (0-3)**\n"
            "   - 0: No quantitative results or worse than baseline.\n"
            "   - 1: Matches existing baselines or minor improvement.\n"
            "   - 2: Clear improvement with evidence (MOST PAPERS).\n"
            "   - 3: Significantly beats SOTA by large margin.\n\n"
            "3. **COMPLETENESS (0-3)**\n"
            "   - 0: Theoretical only, no implementation details.\n"
            "   - 1: Implementation described but no code.\n"
            "   - 2: Code available or detailed reproducible methodology (MOST PAPERS).\n"
            "   - 3: Full open source codebase with extensive experiments.\n\n"
            "*Total Score (score) = Sum of above. Max 11. Average paper should score 5-7.*\n\n"
            "### REQUIRED JSON FORMAT (USE EXACT FIELD NAMES - DO NOT ABBREVIATE):\n"
            "CRITICAL: You MUST use these EXACT field names. DO NOT shorten or change them.\n"
            "{\n"
            "    \"title\": \"Exact paper title\",\n"
            "    \"one_liner\": \"A brutal, honest summary of what it actually does (max 20 words).\",\n"
            "    \"key_innovation\": \"The specific technical change (FIELD NAME MUST BE key_innovation NOT novation)\",\n"
            "    \"sota_comparison\": \"How it compares to SOTA (be skeptical)\",\n"
            "    \"score_novelty\": <int>,\n"
            "    \"score_results\": <int>,\n"
            "    \"score_completeness\": <int>,\n"
            "    \"score\": <int total>\n"
            "}\n\n"
            "REMINDER: Use EXACTLY these field names: title, one_liner, key_innovation, sota_comparison, score_novelty, score_results, score_completeness, score"
        )
        system = "You are a JSON extractor. Respond ONLY in valid JSON."
        user_content = f"{scientist_instruction}\n\nPAPER TEXT:\n{paper_text[:6000]}"
        return self._generate_json(system, user_content, PaperInsight)

    def compare_and_evaluate(self, current_paper: PaperInsight, historical_paper: dict):
        """Compare paper against historical archive to detect duplicates"""
        if not historical_paper:
            return {
                "status": "success",
                "data": {"is_significant": True, "reason": "Cold Start"}
            }

        system = "You are a Patent Examiner. Compare two papers. Output JSON Only."
        user_content = (
            f"[OLD PAPER] {historical_paper['title']}\n"
            f"[NEW PAPER] {current_paper.title}\n\n"
            "IS [NEW] A DUPLICATE OR INCREMENTAL UPDATE OF [OLD]?\n\n"
            "Output JSON:\n"
            "{\n"
            "    \"topic_overlap_score\": <int 0-10>,\n"
            "    \"innovation_type\": \"None\" | \"Incremental\" | \"Breakthrough\" | \"Different_Field\",\n"
            "    \"has_quantitative_improvement\": <bool>,\n"
            "    \"reasoning_brief\": \"Max 15 words explaining the difference.\"\n"
            "}"
        )

        res = self._generate_json(system, user_content, ComparativeAnalysis)

        if res['status'] == 'success':
            data = res['data'].model_dump()

            is_duplicate = (
                data['topic_overlap_score'] >= 8 and
                data['innovation_type'] in ['None', 'Incremental']
            )

            data['is_significant'] = not is_duplicate
            data['reason'] = data['reasoning_brief']

            res['data'] = data

        return res

    def generate_why_it_matters(self, paper_summary: str, profile: ResearchProfile) -> str:
        """Generate personalized explanation of paper relevance"""
        system = "You are a Product Manager. Connect the paper to the user's pain points. Output JSON."
        user_content = (
            "[USER PROFILE]\n"
            f"Pain Points: {', '.join(profile.pain_points)}\n"
            f"Interests: {', '.join(profile.interests)}\n\n"
            "[PAPER]\n"
            f"{paper_summary}\n\n"
            "TASK: Write a 1-sentence hook explaining why this paper helps the user.\n"
            "CONSTRAINT: Start directly with \"This paper...\" or \"By using...\". Do not say \"Given your challenges\"."
        )

        res = self._generate_json(system, user_content, HookSchema)
        if res['status'] == 'success':
            return res['data'].reason
        return f"Relevant to {profile.pain_points[0] if profile.pain_points else 'your research'}."
