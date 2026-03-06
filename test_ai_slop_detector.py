python
#!/usr/bin/env python3
"""
Test suite for ai_slop_detector.py
Tests AI code contribution filter/validator functionality
"""

import pytest
import sys
from unittest.mock import Mock, patch, mock_open
from io import StringIO

# Import the script under test
import ai_slop_detector as script_under_test


class TestAICodeDetector:
    """Test suite for AICodeDetector class"""

    def test_detector_initialization_with_valid_diff(self):
        """Test that detector initializes correctly with valid diff content"""
        diff_content = "+def foo():\n+    pass\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        assert detector.diff == diff_content
        assert detector.score == 0
        assert detector.flags == []
        assert isinstance(detector.added_lines, list)

    def test_extract_added_lines_filters_correctly(self):
        """Test that only added lines (starting with +) are extracted"""
        diff_content = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,5 @@
 existing line
+new line 1
-removed line
+new line 2
 another existing"""
        
        detector = script_under_test.AICodeDetector(diff_content)
        
        assert len(detector.added_lines) == 2
        assert "new line 1" in detector.added_lines
        assert "new line 2" in detector.added_lines
        assert "existing line" not in detector.added_lines
        assert "removed line" not in detector.added_lines

    def test_extract_added_lines_excludes_diff_headers(self):
        """Test that +++ diff headers are not included in added lines"""
        diff_content = "+++ b/file.py\n+actual code line\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        assert len(detector.added_lines) == 1
        assert detector.added_lines[0] == "actual code line"

    def test_analyze_detects_generic_variable_names(self):
        """Test detection of generic variable names like temp, data, result"""
        diff_content = "+temp = 5\n+data = get_data()\n+result = process(data)\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("generic_vars" in flag for flag in detector.flags)

    def test_analyze_detects_obvious_comments(self):
        """Test detection of obvious/redundant comments"""
        diff_content = "+# Initialize the variable\n+x = 0\n+# Return the value\n+return x\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("obvious_comments" in flag for flag in detector.flags)

    def test_analyze_detects_ai_phrases(self):
        """Test detection of AI-specific phrases"""
        diff_content = "+# As an AI, I cannot access files\n+# Let me help you with this\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("ai_phrases" in flag for flag in detector.flags)

    def test_analyze_detects_placeholder_code(self):
        """Test detection of placeholder code like TODO, FIXME, pass"""
        diff_content = "+def foo():\n+    # TODO: implement this\n+    pass\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("placeholder_code" in flag for flag in detector.flags)

    def test_analyze_detects_high_comment_density(self):
        """Test detection of excessive comment ratio (>40%)"""
        diff_content = "+# Comment 1\n+# Comment 2\n+# Comment 3\n+x = 1\n+# Comment 4\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("comment density" in flag.lower() for flag in detector.flags)

    def test_analyze_with_empty_diff(self):
        """Test analyzer handles empty diff gracefully"""
        diff_content = ""
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score == 0
        assert isinstance(report, dict)

    def test_analyze_with_clean_code(self):
        """Test that clean code produces low or zero score"""
        diff_content = "+def calculate_sum(numbers):\n+    total = sum(numbers)\n+    return total\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        # Clean code should have minimal flags
        assert detector.score < 10

    def test_analyze_returns_dict_structure(self):
        """Test that analyze returns a dictionary report"""
        diff_content = "+temp = 1\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert isinstance(report, dict)

    def test_regex_pattern_exception_handling(self):
        """Test that regex exceptions are handled gracefully"""
        diff_content = "+some code\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        # Mock re.findall to raise an exception
        with patch('re.findall', side_effect=Exception("Regex error")):
            report = detector.analyze()
            
            # Should not crash, should continue with other checks
            assert isinstance(report, dict)

    def test_analyze_detects_magic_numbers(self):
        """Test detection of common magic numbers"""
        diff_content = "+value = 42\n+other = 1337\n+test = 420\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("magic_numbers" in flag for flag in detector.flags)

    def test_analyze_detects_excessive_try_except(self):
        """Test detection of bare except Exception patterns"""
        diff_content = "+try: x = 1\n+except Exception: pass\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        assert detector.score > 0
        assert any("excessive_try_except" in flag for flag in detector.flags)

    def test_comment_ratio_calculation_with_zero_lines(self):
        """Test comment ratio calculation doesn't divide by zero"""
        diff_content = ""
        detector = script_under_test.AICodeDetector(diff_content)
        
        # Should not raise ZeroDivisionError
        report = detector.analyze()
        assert isinstance(report, dict)

    def test_multiple_pattern_matches_accumulate_score(self):
        """Test that multiple pattern matches increase the score"""
        diff_content = "+temp = 42  # Initialize the variable\n+# TODO: fix this\n+data = result\n"
        detector = script_under_test.AICodeDetector(diff_content)
        
        report = detector.analyze()
        
        # Should have multiple flags and higher score
        assert detector.score > 5
        assert len(detector.flags) > 1

    def test_detector_with_multiline_diff(self):
        """Test detector handles realistic multi-line diffs"""
        diff_content = """--- a/test.py
+++ b/test.py
@@ -10,5 +10,8 @@
+def process_data(data):
+    # Initialize result
+    result = []
+    temp = data
+    return result"""
        
        detector = script_under_test.AICodeDetector(diff_content)
        report = detector.analyze()
        
        assert len(detector.added_lines) > 0
        assert detector.score > 0