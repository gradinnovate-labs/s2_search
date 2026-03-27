# s2-search

A Semantic Scholar paper search skill for AI coding agents. Search academic papers with advanced filtering capabilities.

## Overview

This skill enables AI coding agents (Claude Code, OpenCode, Codex, etc.) to search and retrieve academic papers from Semantic Scholar with powerful filtering:

- **Keyword search** with AND/OR logic
- **Advanced filters**: year range, venue, publication type, citation count
- **Venue name expansion**: Automatically handles conference/journal abbreviations (NeurIPS, ICML, ACL, etc.)
- **PDF download**: Download open-access papers
- **CSV export**: Export metadata for analysis

## Installation for Coding Agents

**For Claude Code, OpenCode, Codex, or other AI coding agents:**

Install this skill to enable Semantic Scholar paper search capabilities:

```bash
# Determine your agent's skill directory
# Claude Code: ~/.claude/skills/
# OpenCode: ~/.config/opencode/skills/
# Codex: ~/.codex/skills/

# Clone the repository
git clone https://github.com/gradinnovate-labs/s2_search.git

# Move to your agent's skill directory (example for OpenCode)
mv s2_search ~/.config/opencode/skills/

# Or for Claude Code
# mv s2_search ~/.claude/skills/

# Or for Codex
# mv s2_search ~/.codex/skills/
```

**After installation, the agent will automatically:**
1. Recognize trigger phrases like "search papers", "find papers", "Semantic Scholar"
2. Load the skill when paper search is needed
3. Use `scripts/s2_search.py` to execute searches

## Quick Start

### Prerequisites

```bash
pip install requests
```

### Basic Usage

```bash
# Simple search
python scripts/s2_search.py \
  --input '{"keywords":["machine learning"],"logic":"OR"}' \
  --columns "title,authors,year,venue"

# Search with filters
python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count,url" \
  --output results.csv \
  --max-results 2000
```

### Example Query

```json
{
  "keywords": ["transformer", "attention mechanism"],
  "logic": "OR",
  "filters": {
    "year": "2022-2024",
    "venue": ["NeurIPS", "ICML"],
    "publicationTypes": ["Conference"],
    "minCitationCount": 100
  }
}
```

## Features

### Supported Venues

The skill recognizes 50+ venue abbreviations and expands them automatically:

**AI Conferences:**
- NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, CVPR, ICCV, AAAI, IJCAI

**EDA & Hardware:**
- DAC, ICCAD, ISPD, ASP-DAC, DATE, TCAD, TODAES

**Top Journals:**
- Nature, Science, Cell, PNAS, IEEE TPAMI, JMLR

See [SKILL.md](SKILL.md) for the complete list.

### Output Columns

- `title`, `authors`, `venue`, `year`, `citation_count`
- `abstract`, `url`, `paper_id`, `open_access_pdf`

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation for agents
- **[references/troubleshooting.md](references/troubleshooting.md)** - Troubleshooting guide

## API Key (Optional)

For higher rate limits, configure a Semantic Scholar API key:

```bash
export S2_API_KEY="your_api_key_here"
```

**Rate Limits:**
- Without API key: 100 requests / 5 minutes
- With API key: 5,000 requests / 5 minutes

Get your API key at: https://www.semanticscholar.org/product/api

## License

MIT

## Repository

https://github.com/gradinnovate-labs/s2_search
