"""
Perception Tools - Web scraping and data fetching utilities
"""
import requests
import re
import random
from datetime import datetime, timedelta
from typing import Literal, List, Dict


class PerceptionTools:
    """Tools for fetching papers from Hugging Face"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def get_research_date(self, strategy: Literal['random', 'today', 'yesterday'] = 'random') -> str:
        """
        Returns a valid arXiv research date based on strategy.
        Automatically slides weekends (Sat/Sun) back to Friday.
        """
        now = datetime.now()

        if strategy == 'today':
            candidate = now
            print(f"[Time] Selected: today ({candidate.strftime('%Y-%m-%d')})")
        elif strategy == 'yesterday':
            candidate = now - timedelta(days=1)
        else:
            days_ago = random.randint(1, 30)
            candidate = now - timedelta(days=days_ago)

        weekday = candidate.weekday()

        if weekday == 5:
            print(f"[Time] {strategy.title()} was Saturday. Sliding to Friday.")
            candidate -= timedelta(days=1)
        elif weekday == 6:
            print(f"[Time] {strategy.title()} was Sunday. Sliding to Friday.")
            candidate -= timedelta(days=2)

        return candidate.strftime("%Y-%m-%d")

    def fetch_daily_papers(self, date: str = None, limit: int = 5) -> List[Dict]:
        """
        Fetches trending papers from HuggingFace API for a specific date.
        If date is None, fetches the latest trending papers.
        """
        base_url = "https://huggingface.co/api/daily_papers"

        if date:
            print(f"[Perception] Fetching papers for {date}...")
            api_url = f"{base_url}?date={date}"
        else:
            print("[Perception] Fetching latest trending papers...")
            api_url = base_url

        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"[Error] API Request Failed: {response.status_code}")
                return []

            data = response.json()
            papers = []

            if not isinstance(data, list):
                print("[Warning] API returned unexpected format.")
                return []

            for item in data[:limit]:
                try:
                    title = item.get('title')

                    paper_obj = item.get('paper', {})
                    paper_id = paper_obj.get('id')

                    if not paper_id:
                        continue

                    full_url = f"https://huggingface.co/papers/{paper_id}"
                    upvotes = item.get('upvotes') or paper_obj.get('upvotes') or 0

                    papers.append({
                        "title": title,
                        "url": full_url,
                        "upvotes": upvotes,
                        "arxiv_id": paper_id
                    })
                except Exception as e:
                    print(f"[Warning] Skipping item: {e}")

            print(f"[Success] Fetched {len(papers)} papers")
            return papers

        except Exception as e:
            print(f"[Error] API Error: {e}")
            return []

    def fetch_paper_details(self, paper_id: str) -> str:
        """
        Fetches the abstract from the Hugging Face paper page.
        """
        url = f"https://huggingface.co/papers/{paper_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            html = response.text

            if "Abstract</h2>" in html:
                abstract_section = html.split("Abstract</h2>")[1]

                ai_summary = ""
                ai_match = re.search(
                    r'class="text-blue-700[^"]*">(.*?)</p>',
                    abstract_section,
                    re.DOTALL
                )
                if ai_match:
                    ai_summary = ai_match.group(1).strip()

                abstract_match = re.search(
                    r'class="text-gray-600">(.*?)</p>',
                    abstract_section,
                    re.DOTALL
                )

                real_abstract = ""
                if abstract_match:
                    real_abstract = abstract_match.group(1).strip()

                final_output = f"Source: Hugging Face Page\n"
                if ai_summary:
                    final_output += f"AI Summary: {ai_summary}\n\n"
                if real_abstract:
                    final_output += f"Full Abstract: {real_abstract}"
                else:
                    final_output += "Abstract text could not be parsed."

                return final_output

            return "Abstract header not found on page."

        except Exception as e:
            print(f"[Warning] Scraping Error: {e}")
            return "Page fetch failed."
