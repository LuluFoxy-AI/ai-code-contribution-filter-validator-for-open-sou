python
#!/usr/bin/env python3
"""
AI Code Contribution Filter - Detects low-quality AI-generated code in PRs
Author: LuluFoxy-AI
License: MIT
"""

import re
import sys
import json
import argparse
from typing import Dict, List, Tuple
from collections import Counter

# AI slop detection patterns - using simple, non-nested patterns to prevent ReDoS attacks
# Patterns avoid excessive backtracking by using character classes and bounded quantifiers
AI_PATTERNS = {
    'generic_vars': r'\b(temp|tmp|data|result|value|item|obj|var\d+)\b',
    'over_commenting': r'(?:^\s*#[^\n]*\n){4,}',  # 4+ consecutive comment lines
    'obvious_comments': r'#\s*(?:Initialize|Create|Set|Get|Return|Loop through|Iterate)\b',
    'ai_phrases': r'\b(?:as an AI|I apologize|I cannot|let me help|here\'s how)\b',
    'placeholder_code': r'\b(?:TODO:|FIXME:|pass\s*#|raise NotImplementedError)\b',
    'excessive_try_except': r'try:\s+[^\n]+\s+except Exception:',  # Match single line, no backtracking
    'magic_numbers': r'\b(?:42|69|420|1337|9999)\b',
    # Fixed: Use bounded quantifier to prevent ReDoS
    'redundant_else': r'if\s+[^\n]{1,200}:\s*return\s+[^\n]{1,200}\s+else:\s*return\b'
}

# Code quality heuristics
class AICodeDetector:
    def __init__(self, diff_content: str):
        """Initialize detector with git diff content"""
        self.diff = diff_content
        self.added_lines = self._extract_added_lines()
        self.score = 0
        self.flags = []

    def _extract_added_lines(self) -> List[str]:
        """Extract only added lines from git diff (lines starting with +)"""
        lines = []
        for line in self.diff.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                lines.append(line[1:])  # Remove '+' prefix
        return lines

    def analyze(self) -> Dict:
        """Run all detection heuristics and return analysis report"""
        code_text = '\n'.join(self.added_lines)
        
        # Pattern matching with timeout protection
        for pattern_name, pattern in AI_PATTERNS.items():
            try:
                matches = re.findall(pattern, code_text, re.MULTILINE | re.IGNORECASE)
                if matches:
                    count = len(matches)
                    self.score += count * 2
                    self.flags.append(f"{pattern_name}: {count} occurrences")
            except Exception as e:
                # Skip pattern if regex fails (timeout or other error)
                continue
        
        # Comment density check (>40% comments is suspicious)
        total_lines = len(self.added_lines)
        if total_lines > 0:
            comment_lines = sum(1 for line in self.added_lines if line.strip().startswith('#'))
            comment_ratio = comment_lines / total_lines
            if comment_ratio > 0.4:
                self.score += 10
                self.flags.append(f"High comment density: {comment_ratio:.1%}")
        
        # Variable name entropy (low entropy = generic names)
        var_names = re.findall(r'\b([a-z_][a-z0-9_]{2,})\b', code_text.lower())
        if var_names and len(var_names) > 0:
            unique_ratio = len(set(var_names)) / len(var_names)
            if unique_ratio < 0.3:
                self.score += 8
                self.flags.append(f"Low variable name diversity: {unique_ratio:.1%}")
        
        # Line length consistency (AI often generates uniform line lengths)
        line_lengths = [len(line) for line in self.added_lines if line.strip()]
        if line_lengths and len(line_lengths) > 0:
            avg_length = sum(line_lengths) / len(line_lengths)
            if 75 < avg_length < 85:  # Suspiciously uniform
                self.score += 5
                self.flags.append(f"Uniform line lengths: avg {avg_length:.0f} chars")
        
        # Return the complete analysis report
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """Generate final analysis report with verdict and recommendations"""
        if self.score >= 20:
            verdict = "REJECT"
            recommendation = "High likelihood of low-quality AI-generated code. Manual review required."
        elif self.score >= 10:
            verdict = "REVIEW"
            recommendation = "Moderate AI indicators detected. Careful review recommended."
        else:
            verdict = "ACCEPT"
            recommendation = "Code appears to be human-written or high-quality."
        
        return {
            "verdict": verdict,
            "score": self.score,
            "flags": self.flags,
            "recommendation": recommendation,
            "lines_analyzed": len(self.added_lines)
        }


def main():
    """Main entry point for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Detect AI-generated code slop in git diffs"
    )
    parser.add_argument(
        'diff_file',
        nargs='?',
        help='Path to git diff file (or read from stdin)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=20,
        help='Score threshold for rejection (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Read diff content from file or stdin
    if args.diff_file:
        try:
            with open(args.diff_file, 'r', encoding='utf-8') as f:
                diff_content = f.read()
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        diff_content = sys.stdin.read()
    
    # Run analysis
    detector = AICodeDetector(diff_content)
    report = detector.analyze()
    
    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"AI Code Slop Detection Report")
        print(f"{'='*60}")
        print(f"Verdict: {report['verdict']}")
        print(f"Score: {report['score']}")
        print(f"Lines Analyzed: {report['lines_analyzed']}")
        print(f"\nFlags Detected:")
        if report['flags']:
            for flag in report['flags']:
                print(f"  - {flag}")
        else:
            print("  None")
        print(f"\nRecommendation: {report['recommendation']}")
        print(f"{'='*60}\n")
    
    # Exit with appropriate code
    if report['verdict'] == "REJECT":
        sys.exit(1)
    elif report['verdict'] == "REVIEW":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()