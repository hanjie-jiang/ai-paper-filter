#!/usr/bin/env python3
"""
AI Paper Daily Debrief Agent
Main entry point for the application
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import ResearchPipeline
from report_generator import generate_html_report


def main():
    parser = argparse.ArgumentParser(
        description="AI Paper Daily Debrief - Get personalized research paper recommendations"
    )

    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Your research interests and preferences (e.g., "I work on AI agents and RAG systems")'
    )

    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Target date for papers (YYYY-MM-DD). If not specified, uses latest papers.'
    )

    parser.add_argument(
        '--max-papers',
        type=int,
        default=6,
        help='Maximum number of papers to analyze (default: 6)'
    )

    parser.add_argument(
        '--db-path',
        type=str,
        default=None,
        help='Path to paper archive database (default: data/paper_memory.json)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory for output files (default: output/)'
    )

    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline
    print("\n" + "=" * 70)
    print("AI PAPER DAILY DEBRIEF AGENT")
    print("=" * 70)
    print(f"\nUser Prompt: {args.prompt}")
    print(f"Target Date: {args.date if args.date else 'Latest'}")
    print(f"Max Papers: {args.max_papers}")
    print()

    pipeline = ResearchPipeline(db_path=args.db_path)

    # Run pipeline
    try:
        result = pipeline.run(
            user_prompt_text=args.prompt,
            target_date=args.date,
            max_papers=args.max_papers
        )

        # Save JSON output
        json_path = output_dir / 'daily_briefing.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n[Output] JSON saved to: {json_path}")

        # Generate HTML report
        if not args.no_html:
            html_path = output_dir / 'daily_briefing.html'
            generate_html_report(result, output_path=str(html_path))
            print(f"[Output] HTML report saved to: {html_path}")

            # Auto-open in browser
            import subprocess
            import platform
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', str(html_path)])
                elif platform.system() == 'Windows':
                    subprocess.run(['start', str(html_path)], shell=True)
                else:  # Linux
                    subprocess.run(['xdg-open', str(html_path)])
                print(f"Opening report in browser...")
            except Exception as e:
                print(f"Could not auto-open browser. Please open manually: {html_path}")

        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)

        # Print summary
        num_papers = len(result.get('cards', []))
        if num_papers > 0:
            print(f"\n✓ Found {num_papers} relevant paper(s) matching your interests")
            print("\nTop recommendations:")
            for card in result['cards']:
                print(f"  {card['rank']}. {card['title']}")
        else:
            print("\n⚠ No papers matched your criteria. Try:")
            print("  - Using more general keywords")
            print("  - Checking a different date")
            print("  - Increasing --max-papers")

        return 0

    except KeyboardInterrupt:
        print("\n\n[Interrupted] Pipeline stopped by user")
        return 1
    except Exception as e:
        print(f"\n[Error] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
