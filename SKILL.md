---
name: s2-search
description: Search academic papers on Semantic Scholar with advanced filtering (year, venue, citations). Use when users need to search for research papers, find academic articles, or query papers from specific conferences/journals. Triggers: "search papers", "find papers", "Semantic Scholar", "academic search", "paper lookup", "citation search", "conference papers", "journal articles".
license: MIT
compatibility: Python 3.7+, requests library, internet access
---

# Semantic Scholar Paper Search

Search and retrieve academic papers from Semantic Scholar with powerful filtering capabilities.

## When to Use This Skill

Use this skill when the user asks to:
- Search for academic papers on specific topics
- Find papers from particular conferences or journals
- Filter papers by year, citations, or publication type
- Sort papers by citation count
- Download open-access PDFs (with ArXiv fallback)
- Export paper metadata to CSV or JSON
- Search multiple keywords independently and merge results
- Get ArXiv IDs or DOIs for papers

**Trigger phrases:**
- "Search for papers about..."
- "Find academic articles on..."
- "Look up papers from NeurIPS/ICML/ACL..."
- "Search Semantic Scholar for..."
- "Find highly-cited papers in..."
- "Search multiple keywords and merge results..."

## Quick Start

```bash
# Simple search (outputs all columns by default)
python scripts/s2_search.py --input '{"keywords":["machine learning"],"logic":"OR"}'

# With specific columns
python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count" \
  --output results.csv
```

## Input Format

```json
{
  "keywords": ["keyword1", "keyword2"],
  "logic": "AND",
  "multiSearch": false,
  "filters": {
    "year": "2020-2024",
    "venue": ["NeurIPS", "ICML"],
    "publicationTypes": ["Conference"],
    "minCitationCount": 50,
    "sort": "citationCount:desc"
  }
}
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `keywords` | List of search terms (required) | - |
| `logic` | "AND" or "OR" (ignored if multiSearch=true) | "AND" |
| `multiSearch` | Search each keyword independently, merge & dedupe | false |
| `filters.year` | Date range (see formats below) | - |
| `filters.venue` | Conference/journal names | - |
| `filters.publicationTypes` | Conference, JournalArticle, Review, etc. | - |
| `filters.minCitationCount` | Minimum citations | - |
| `filters.sort` | Sort: "citationCount:desc", "publicationDate:desc" | - |

### Year Formats

- `"2024"` - Single year
- `"2020-2024"` - Year range
- `"2020-"` - After 2020
- `"-2024"` - Before 2024

## Venue Name Expansion

When users mention venue abbreviations (NeurIPS, ICML, ACL, etc.), expand them to include full names and variations.

**Example:**
```json
// User says: "Find papers from ACL"
{
  "venue": [
    "ACL",
    "Annual Meeting of the Association for Computational Linguistics",
    "Association for Computational Linguistics"
  ]
}
```

See [references/venues.md](references/venues.md) for the complete venue abbreviation table.

## Output Columns

Default columns (when `--columns` not specified):
`index`, `title`, `authors`, `venue`, `year`, `citation_count`, `abstract`, `url`, `paper_id`, `open_access_pdf`, `external_ids`, `arxiv_id`, `doi`, `pdf_url`, `pdf_source`

All available columns:

| Column | Description |
|--------|-------------|
| `index` | Row number |
| `title` | Paper title |
| `authors` | Author names (semicolon-separated) |
| `venue` | Publication venue |
| `year` | Publication year |
| `citation_count` | Number of citations |
| `abstract` | Paper abstract |
| `url` | Semantic Scholar URL |
| `paper_id` | Unique paper identifier |
| `open_access_pdf` | PDF download URL (if available) |
| `arxiv_id` | ArXiv ID |
| `doi` | DOI |
| `pdf_url` | PDF URL (with ArXiv fallback) |
| `pdf_source` | PDF source: "openAccess" or "arxiv" |
| `match_keywords` | Matched keywords (multiSearch mode) |

## Output Formats

```bash
# CSV (default)
--output results.csv

# JSON
--output results.json --output-format json
```

## Examples

### Example 1: Basic Search with Filters

```bash
cat > query.json << 'EOF'
{
  "keywords": ["transformer", "attention mechanism"],
  "logic": "OR",
  "filters": {
    "year": "2022-2024",
    "minCitationCount": 100,
    "sort": "citationCount:desc"
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count" \
  --output transformers.csv \
  --max-results 500
```

### Example 2: Multi-Keyword Independent Search

```bash
# Search each keyword separately, merge and deduplicate
cat > query.json << 'EOF'
{
  "keywords": ["LLM", "large language model", "GPT", "chatbot"],
  "multiSearch": true,
  "filters": {
    "year": "2023-2024"
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,match_keywords,citation_count,arxiv_id" \
  --output-format json \
  --output llm_papers.json
```

### Example 3: Download PDFs with ArXiv Fallback

```bash
python scripts/s2_search.py \
  --input query.json \
  --download-pdf \
  --pdf-naming "{index}_{title}" \
  --pdf-dir ./pdfs \
  --output papers.csv
```

PDFs are downloaded from:
1. `openAccessPdf.url` first
2. ArXiv (`https://arxiv.org/pdf/{arxiv_id}`) as fallback

### Example 4: Search Specific Venues

```bash
# User asks: "Find recent papers from NeurIPS and ICML about diffusion models"
cat > query.json << 'EOF'
{
  "keywords": ["diffusion models", "score-based generative models"],
  "logic": "OR",
  "filters": {
    "venue": [
      "NeurIPS",
      "Neural Information Processing Systems",
      "ICML",
      "International Conference on Machine Learning"
    ],
    "year": "2023-2024",
    "publicationTypes": ["Conference"]
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count" \
  --output diffusion_papers.csv
```

## PDF Naming Templates

| Variable | Description |
|----------|-------------|
| `{index}` | Zero-padded index (0001, 0002, ...) |
| `{paperId}` | Semantic Scholar paper ID |
| `{title}` | Paper title (truncated to 100 chars) |
| `{year}` | Publication year |
| `{arxivId}` | ArXiv ID (or "no_arxiv") |

**Examples:**
```bash
--pdf-naming "{paperId}.pdf"           # Default
--pdf-naming "{index}_{title}.pdf"     # 0001_Attention Is All You Need.pdf
--pdf-naming "{year}_{arxivId}.pdf"    # 2023_2301.12345.pdf
```

## API Key Configuration

```bash
export S2_API_KEY="your_api_key_here"
```

**Rate Limits:**
- Without API key: 100 requests / 5 minutes
- With API key: 5,000 requests / 5 minutes

Get your API key at: https://www.semanticscholar.org/product/api

## Troubleshooting

For common issues, see [references/troubleshooting.md](references/troubleshooting.md).

### Quick Tips

- **No results**: Broaden keywords, expand venue names, relax filters
- **Rate limited**: Configure `S2_API_KEY` environment variable
- **PDF download fails**: ArXiv fallback is automatic; check `pdf_source` column
- **Use `--verbose`**: See detailed API interactions for debugging
