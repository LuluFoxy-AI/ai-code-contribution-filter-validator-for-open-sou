# AI Code Contribution Filter

🛡️ **Protect your open source project from AI-generated code slop**

A lightweight CLI tool that detects low-quality AI-generated code contributions in pull requests. Stop wasting hours reviewing garbage PRs that don't compile, use generic variable names, or contain obvious AI hallucinations.

## The Problem

Open source maintainers are drowning in AI-generated PRs:
- 🤖 ChatGPT/Copilot spam with generic variable names (`temp`, `data`, `result`)
- 📝 Over-commented code explaining obvious operations
- 🚫 Code that doesn't compile or add real value
- ⏰ Hours wasted on manual review

## The Solution

This tool scans PR diffs and assigns a "slop score" based on common AI patterns:
- Generic variable naming patterns
- Excessive or obvious commenting
- AI-specific phrases and placeholders
- Low code entropy and suspicious uniformity
- Common hallucination patterns

## Installation

```bash
# Clone the repository
git clone https://github.com/LuluFoxy-AI/ai-code-contribution-filter-validator-for-open-sou.git
cd ai-code-contribution-filter-validator-for-open-sou

# Make executable
chmod +x ai_code_filter.py
```

## Usage

```bash
# Analyze a PR diff file
./ai_code_filter.py pr_diff.txt

# Pipe git diff directly
git diff main...feature-branch | ./ai_code_filter.py -

# JSON output for CI/CD integration
./ai_code_filter.py pr_diff.txt --json

# Custom threshold (default: 20)
./ai_code_filter.py pr_diff.txt --threshold 15
```

## Example Output

```
============================================================
AI Code Slop Detection Report
============================================================
Verdict: HIGH_RISK
Score: 24 (threshold: 20)
Message: Strong indicators of AI-generated slop detected
Lines Analyzed: 87

Flags Detected:
  - generic_vars: 12 occurrences
  - obvious_comments: 8 occurrences
  - High comment density: 45.2%
  - Low variable name diversity: 28.3%
============================================================
```

## CI/CD Integration

Use as a GitHub Action or pre-commit hook:

```yaml
# .github/workflows/pr-check.yml
- name: Check for AI slop
  run: |
    git diff origin/main...HEAD | python ai_code_filter.py - --json
```

## Roadmap

- [ ] GitHub Action marketplace release
- [ ] Custom rule configuration
- [ ] Team dashboards
- [ ] Integration APIs
- [ ] Machine learning model for detection

## Premium Features (Coming Soon)

- Custom detection rules per repository
- Historical analytics dashboard
- Slack/Discord notifications
- Enterprise SSO support
- Priority support

**Pricing:** $29-99/mo per organization

## License

MIT License - Free for public repositories

## Contributing

Ironically, we manually review all contributions to ensure they're not AI slop. 😉

---

**Star this repo** if you're tired of reviewing AI-generated garbage!