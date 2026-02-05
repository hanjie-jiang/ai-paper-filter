"""
HTML Report Generator - Creates beautiful HTML briefings
"""
import os
from typing import Dict


def get_badge_class(badge: str) -> str:
    """Map badge text to CSS class"""
    if "Top" in badge:
        return "badge-top"
    if "SOTA" in badge:
        return "badge-sota"
    if "New" in badge:
        return "badge-new"
    if "Topic" in badge:
        return "badge-match"
    return "badge-sota"


def generate_html_report(data: Dict, output_path: str = None) -> str:
    """
    Generate a beautiful HTML report from the briefing data
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'daily_briefing.html')

    css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .dashboard-container { font-family: 'Inter', sans-serif; background-color: #F8F9FA; padding: 20px; border-radius: 8px; }
    .header { margin-bottom: 20px; border-bottom: 1px solid #E5E7EB; padding-bottom: 10px; }
    .header h1 { margin: 0; color: #111827; font-size: 24px; }
    .meta { color: #6B7280; font-size: 14px; margin-top: 5px; }

    .paper-card {
        background-color: white; border: 1px solid #E5E7EB; border-radius: 12px;
        padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    .badge-container { margin-bottom: 12px; }
    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 99px;
        font-size: 11px; font-weight: 700; margin-right: 6px; text-transform: uppercase;
    }
    .badge-top { background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .badge-sota { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-new { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-match { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }

    .card-title { font-size: 18px; font-weight: 700; color: #1F2937; margin: 0 0 8px 0; }
    .card-tldr { color: #4B5563; font-size: 14px; line-height: 1.5; margin-bottom: 16px; }

    .reason-box { background: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 4px; margin-bottom: 20px; }
    .reason-text { color: #1E3A8A; font-size: 13px; font-style: italic; }

    .metrics-grid { display: flex; gap: 20px; margin-top: 20px; border-top: 1px solid #F3F4F6; padding-top: 15px; }
    .metric { flex: 1; }
    .metric-label { font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-bottom: 5px; }
    .bar-bg { background: #E5E7EB; height: 6px; border-radius: 3px; overflow: hidden; }
    .bar-fill { height: 100%; background: #3B82F6; border-radius: 3px; }

    .btn-container { text-align: right; margin-top: 15px; }
    .read-btn {
        background: #111827; color: white !important; padding: 8px 16px; border-radius: 6px;
        text-decoration: none; font-size: 13px; font-weight: 600; display: inline-block;
    }
</style>
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Daily Research Briefing</title>
    {css}
</head>
<body>
<div class="dashboard-container">
    <div class="header">
        <h1>Daily Research Briefing</h1>
        <div class="meta">Date: {data.get('timestamp')} | Focused on: {', '.join(data.get('user_intent', []))}</div>
    </div>
"""

    for card in data['cards']:
        badges_html = "".join([
            f'<span class="badge {get_badge_class(b)}">{b}</span>'
            for b in card['badges']
        ])

        html_content += f"""
    <div class="paper-card">
        <div class="badge-container">{badges_html}</div>
        <div class="card-title">#{card['rank']} {card['title']}</div>
        <div class="card-tldr">{card['tldr']}</div>

        <div class="reason-box">
            <div class="reason-text"><b>Why it matters:</b> {card['personalized_reason']}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">Novelty ({card['raw_novelty']}/4)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {card['metrics_novelty_pct']}%;"></div></div>
            </div>
            <div class="metric">
                <div class="metric-label">Results ({card['raw_results']}/3)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {card['metrics_results_pct']}%;"></div></div>
            </div>
            <div class="metric">
                <div class="metric-label">Completeness ({card['raw_completeness']}/3)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {card['metrics_completeness_pct']}%;"></div></div>
            </div>
        </div>

        <div class="btn-container">
            <a href="{card['read_link']}" target="_blank" class="read-btn">Read Paper ↗</a>
        </div>
    </div>
"""

    html_content += """
</div>
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n[Report] HTML report generated: {output_path}")
    return output_path
