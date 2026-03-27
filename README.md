# s2-search

A Semantic Scholar paper search skill for AI coding agents. Search academic papers with advanced filtering capabilities.

## Overview

This skill enables AI coding agents (Claude Code, OpenCode, Codex, etc.) to search and retrieve academic papers from Semantic Scholar with powerful filtering:

- **Keyword search** with AND/OR logic
- **Multi-keyword independent search**: Search each keyword separately, merge & deduplicate results
- **Advanced filters**: year range, venue, publication type, citation count, sort by citations
- **Venue name expansion**: Automatically handles conference/journal abbreviations (NeurIPS, ICML, ACL, etc.)
- **External IDs**: ArXiv, DOI, and other external identifiers
- **PDF download**: Download open-access papers with ArXiv fallback
- **Custom PDF naming**: Template-based PDF file naming
- **CSV/JSON export**: Export metadata for analysis

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
# Simple search (outputs all columns)
python scripts/s2_search.py \
  --input '{"keywords":["machine learning"],"logic":"OR"}'

# Search with specific columns
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
  "multiSearch": false,
  "filters": {
    "year": "2022-2024",
    "venue": ["NeurIPS", "ICML"],
    "publicationTypes": ["Conference"],
    "minCitationCount": 100,
    "sort": "citationCount:desc"
  }
}
```

### Multi-Keyword Independent Search

Set `"multiSearch": true` to search each keyword independently, then merge and deduplicate:

```json
{
  "keywords": ["LLM", "large language model", "GPT"],
  "multiSearch": true,
  "filters": {
    "year": "2023-2024"
  }
}
```

Results will include a `match_keywords` field showing which keywords matched each paper.

## Features

### Supported Venues

The skill recognizes 50+ venue abbreviations and expands them automatically.

**AI Conferences:** NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, ICCV, AAAI, IJCAI

**EDA & Hardware:** DAC, ICCAD, ISPD, TCAD, TODAES

See [references/venues.md](references/venues.md) for the complete list.

### Output Columns

- `title`, `authors`, `venue`, `year`, `citation_count`
- `abstract`, `url`, `paper_id`, `open_access_pdf`
- `external_ids`, `arxiv_id`, `doi`
- `pdf_url`, `pdf_source` (with ArXiv fallback)
- `match_keywords` (for multi-keyword search)

### Output Formats

```bash
# CSV output (default)
--output results.csv

# JSON output
--output results.json --output-format json
```

### PDF Download with ArXiv Fallback

```bash
# Download PDFs (automatically falls back to ArXiv if openAccessPdf is unavailable)
python scripts/s2_search.py \
  --input query.json \
  --columns "title,arxiv_id,pdf_url,pdf_source" \
  --download-pdf \
  --pdf-naming "{index}_{title}" \
  --pdf-dir ./pdfs
```

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
