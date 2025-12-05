"""
Test script to verify HTML generation in the research automation system.

This script tests:
1. ReportAgent HTML generation
2. Markdown to HTML conversion
3. Output structure validation
"""

from src.agents.report import ReportAgent

def test_html_generation():
    """Test that ReportAgent generates HTML correctly."""

    # Initialize ReportAgent
    reporter = ReportAgent()

    # Sample analysis output for overview mode
    analysis_output = {
        "summary": "This is a test summary about AI and machine learning.",
        "key_points": [
            "AI is transforming industries",
            "Machine learning requires large datasets",
            "Deep learning uses neural networks"
        ],
        "pros": [
            "Automation of repetitive tasks",
            "Improved decision making"
        ],
        "cons": [
            "High computational costs",
            "Data privacy concerns"
        ],
        "sources": [
            {
                "title": "Introduction to AI",
                "url": "https://example.com/ai-intro"
            },
            {
                "title": "Machine Learning Basics",
                "url": "https://example.com/ml-basics"
            }
        ]
    }

    # Run report generation
    result = reporter.run(
        mode="overview",
        analysis_output=analysis_output,
        topic="Artificial Intelligence"
    )

    # Verify result
    assert result.success, f"Report generation failed: {result.error}"
    assert "report_path" in result.data, "Missing report_path"
    assert "report_html" in result.data, "Missing report_html in result"
    assert "pdf_path" in result.data, "Missing pdf_path"

    # Verify HTML content
    html_content = result.data["report_html"]
    assert "<!DOCTYPE html>" in html_content, "Missing HTML doctype"
    assert "<html" in html_content, "Missing html tag"
    assert "Artificial Intelligence" in html_content, "Missing topic in HTML"
    assert "This is a test summary" in html_content, "Missing summary in HTML"

    print("[PASS] HTML Generation Test PASSED")
    print(f"   - Report path: {result.data['report_path']}")
    print(f"   - PDF path: {result.data['pdf_path']}")
    print(f"   - HTML length: {len(html_content)} characters")

    return result

if __name__ == "__main__":
    try:
        result = test_html_generation()
        print("\n[SUCCESS] All tests passed successfully!")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
