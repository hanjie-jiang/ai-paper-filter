"""
Main Pipeline - Orchestrates the entire paper filtering workflow
"""
import json
from typing import List
from pydantic import BaseModel

from brain import CognitiveBrain, ResearchProfile
from tools import PerceptionTools
from curator import Curator
from archive import PaperArchive


class FrontendCard(BaseModel):
    """Schema for frontend display cards"""
    id: str
    rank: int
    title: str
    badges: List[str]
    personalized_reason: str
    tldr: str
    metrics_novelty_pct: int
    metrics_results_pct: int
    metrics_completeness_pct: int
    raw_novelty: int
    raw_results: int
    raw_completeness: int
    read_link: str


class DailyBriefingResponse(BaseModel):
    """Full briefing response"""
    date: str
    user_name: str
    cards: List[FrontendCard]


class ResearchPipeline:
    """
    Main orchestrator for the paper filtering workflow
    """

    def __init__(self, db_path: str = None):
        print("\n" + "=" * 60)
        print("INITIALIZING AI PAPER FILTER")
        print("=" * 60)

        self.tools = PerceptionTools()
        self.brain = CognitiveBrain()
        self.curator = Curator()
        self.archive = PaperArchive(db_path=db_path)

    def run(self, user_prompt_text: str, target_date: str = None, max_papers: int = 6) -> dict:
        """
        Run the complete pipeline:
        1. Analyze user intent
        2. Fetch papers from HuggingFace
        3. Analyze each paper
        4. Filter by quality and relevance
        5. Return top 3 ranked papers
        """
        print(f"\n[Step 1] Analyzing User Intent...")
        print(f"User Query: {user_prompt_text[:100]}...")

        intent_res = self.brain.analyze_user_intent(user_prompt_text)
        if intent_res['status'] != 'success':
            return {"error": "Failed to analyze user intent"}

        i_data = intent_res['data']
        profile = ResearchProfile(
            user_id="u_live",
            interests=i_data.core_interests,
            context_tags=i_data.context_tags,
            pain_points=i_data.pain_points,
            negative_keywords=i_data.negative_keywords
        )
        print(f"Extracted Interests: {profile.interests}")
        print(f"Pain Points: {profile.pain_points}")

        print(f"\n[Step 2] Fetching Papers from Hugging Face...")
        candidates = self.tools.fetch_daily_papers(target_date, limit=max_papers)

        frontend_cards = []

        print(f"\n[Step 3] Analyzing {len(candidates)} Papers...")
        print("-" * 60)

        for i, p in enumerate(candidates, 1):
            pid = p.get('arxiv_id')
            if not pid:
                continue

            print(f"\n[{i}/{len(candidates)}] Processing: {p['title'][:50]}...")

            text = self.tools.fetch_paper_details(pid)
            if "Abstract not found" in text or "Page fetch failed" in text:
                print("  Skipped: Could not fetch abstract")
                continue

            insight_res = self.brain.think(text)
            if insight_res['status'] != 'success':
                print(f"  Skipped: Analysis failed")
                continue

            insight = insight_res['data']

            if insight.score < 5:
                print(f"  Rejected: Low quality score ({insight.score}/11)")
                continue

            hist_match = self.archive.retrieve_similar(insight.one_liner)
            if hist_match:
                critic_res = self.brain.compare_and_evaluate(insight, hist_match)
                if critic_res['status'] == 'success' and not critic_res['data']['is_significant']:
                    print(f"  Duplicate: {critic_res['data']['reason']}")
                    continue
                elif critic_res['status'] != 'success':
                    print(f"  Warning: Comparison failed, treating as new paper")

            self.archive.save(insight)

            relevance = self.curator.calculate_relevance(insight.one_liner, profile)

            if relevance > 0.2:
                reason = self.brain.generate_why_it_matters(insight.one_liner, profile)

                badges = []
                if insight.score_results == 3:
                    badges.append("SOTA Beat")
                if insight.score_novelty == 4:
                    badges.append("New Arch")

                priority_score = insight.score + (relevance * 20.0)

                title_lower = insight.title.lower()
                keywords = set()
                for interest in profile.interests:
                    words = interest.lower().split()
                    for w in words:
                        if len(w) > 2:
                            keywords.add(w)

                for kw in keywords:
                    if kw in title_lower or (kw.endswith('s') and kw[:-1] in title_lower) or (kw + 's' in title_lower):
                        priority_score += 5.0
                        badges.append("Topic Match")
                        break

                card_obj = FrontendCard(
                    id=pid,
                    rank=0,
                    title=insight.title,
                    badges=badges,
                    personalized_reason=reason,
                    tldr=insight.one_liner,
                    metrics_novelty_pct=int((insight.score_novelty / 4) * 100),
                    metrics_results_pct=int((insight.score_results / 3) * 100),
                    metrics_completeness_pct=int((insight.score_completeness / 3) * 100),
                    raw_novelty=insight.score_novelty,
                    raw_results=insight.score_results,
                    raw_completeness=insight.score_completeness,
                    read_link=f"https://huggingface.co/papers/{pid}"
                )
                frontend_cards.append((priority_score, card_obj))

                print(f"  ✓ Accepted | Priority: {priority_score:.1f} | Quality: {insight.score}/10 | Relevance: {relevance:.2f}")
            else:
                print(f"  Rejected: Low relevance ({relevance:.2f})")

        print("\n" + "=" * 60)
        print("[Step 4] FINAL RANKING")
        print("=" * 60)

        frontend_cards.sort(key=lambda x: x[0], reverse=True)

        final_cards = []
        for i, (score, c) in enumerate(frontend_cards[:3]):
            c.rank = i + 1
            if i == 0:
                c.badges.insert(0, "Top Pick")

            print(f"\n#{c.rank} {c.title}")
            print(f"   {c.personalized_reason}")
            print(f"   Scores: Novelty {c.raw_novelty}/4 | Results {c.raw_results}/3 | Completeness {c.raw_completeness}/3")
            print(f"   Badges: {', '.join(c.badges)}")

            final_cards.append(c)

        export_data = {
            "user_intent": profile.interests,
            "timestamp": target_date if target_date else "Today",
            "cards": [c.model_dump() for c in final_cards]
        }

        return export_data
