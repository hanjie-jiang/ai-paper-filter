#!/usr/bin/env python3
"""
Basic test script to verify the installation works
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")

    try:
        from brain import CognitiveBrain, PaperInsight, ResearchProfile
        print("  - brain.py: OK")
    except Exception as e:
        print(f"  - brain.py: FAILED - {e}")
        return False

    try:
        from tools import PerceptionTools
        print("  - tools.py: OK")
    except Exception as e:
        print(f"  - tools.py: FAILED - {e}")
        return False

    try:
        from archive import PaperArchive
        print("  - archive.py: OK")
    except Exception as e:
        print(f"  - archive.py: FAILED - {e}")
        return False

    try:
        from curator import Curator
        print("  - curator.py: OK")
    except Exception as e:
        print(f"  - curator.py: FAILED - {e}")
        return False

    try:
        from pipeline import ResearchPipeline
        print("  - pipeline.py: OK")
    except Exception as e:
        print(f"  - pipeline.py: FAILED - {e}")
        return False

    try:
        from report_generator import generate_html_report
        print("  - report_generator.py: OK")
    except Exception as e:
        print(f"  - report_generator.py: FAILED - {e}")
        return False

    return True

def test_tools_basic():
    """Test basic functionality of PerceptionTools"""
    print("\nTesting PerceptionTools...")

    try:
        from tools import PerceptionTools
        tools = PerceptionTools()

        # Test date generation
        date = tools.get_research_date(strategy='yesterday')
        print(f"  - Date generation: OK (got {date})")

        return True
    except Exception as e:
        print(f"  - PerceptionTools: FAILED - {e}")
        return False

def main():
    print("=" * 60)
    print("AI PAPER FILTER - BASIC TEST SUITE")
    print("=" * 60)
    print()

    # Test imports
    if not test_imports():
        print("\nIMPORT TEST FAILED")
        print("Make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        return 1

    # Test basic tools
    if not test_tools_basic():
        print("\nBASIC FUNCTIONALITY TEST FAILED")
        return 1

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print("\nYour installation is working correctly!")
    print("\nNext steps:")
    print("1. Run: python main.py --prompt 'Your research interests here'")
    print("2. Check the output/ directory for results")

    return 0

if __name__ == "__main__":
    sys.exit(main())
