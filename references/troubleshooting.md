# Troubleshooting Guide for s2-search

This guide helps you resolve common issues when using the Semantic Scholar search tool.

## Table of Contents

- [No Results Found](#no-results-found)
- [Rate Limited](#rate-limited)
- [PDF Download Fails](#pdf-download-fails)
- [Tips for Best Results](#tips-for-best-results)

## No Results Found

If your search returns no papers:

### 1. Broaden Keywords

Use OR logic instead of AND:

```bash
# Too restrictive
--input '{"keywords":["machine learning","transformer"],"logic":"AND"}'

# More inclusive
--input '{"keywords":["machine learning","transformer"],"logic":"OR"}'
```

### 2. Check Venue Names

Expand abbreviations to full names. Semantic Scholar may use different formats:

```json
// Wrong - may not match
{"venue": ["ACL"]}

// Better - includes variations
{"venue": [
  "ACL",
  "Annual Meeting of the Association for Computational Linguistics",
  "Association for Computational Linguistics"
]}
```

**Special cases:**
- **TODAES**: Use `"ACM Trans. Design Autom. Electr. Syst."` (abbreviated form works better)
- **JMLR**: Use `"Journal of machine learning research"` (lowercase)
- **PNAS**: Use `"Proceedings of the National Academy of Sciences of the United States of America"`

See [SKILL.md](../SKILL.md#venue-name-expansion) for complete venue name tables.

### 3. Adjust Filters

Remove or relax filters:

```json
// Too restrictive
{
  "filters": {
    "year": "2024",
    "minCitationCount": 500,
    "venue": ["NeurIPS"],
    "publicationTypes": ["Conference"]
  }
}

// More flexible
{
  "filters": {
    "year": "2020-2024",
    "venue": ["NeurIPS", "ICML", "ICLR"]
  }
}
```

### 4. Use Verbose Mode

Add `--verbose` to see detailed logs:

```bash
python scripts/s2_search.py \
  --input query.json \
  --verbose
```

This shows:
- Query being sent to API
- Number of results retrieved
- API response details
- Error messages

### 5. Check Keyword Specificity

Use more specific keywords:

```bash
# Too vague
"transformer"

# Better
"transformer architecture"

# Even better
"vision transformer", "ViT", "transformer for computer vision"
```

## Rate Limited

If you hit Semantic Scholar's rate limit:

### Symptoms

- HTTP 429 errors
- "Rate limited. Waiting X seconds..." messages
- Long delays between results

### Solutions

#### 1. Wait and Retry (Automatic)

The tool automatically retries with exponential backoff:
- First retry: 1 second
- Second retry: 2 seconds  
- Third retry: 4 seconds
- Maximum: 3 retries

#### 2. Get an API Key

Sign up at https://www.semanticscholar.org/product/api

**Rate Limits:**
- Without API key: 100 requests / 5 minutes
- With API key: 5,000 requests / 5 minutes

**Configure API key:**

```bash
# Option 1: Environment variable (recommended)
export S2_API_KEY="your_api_key_here"

# Option 2: Command line
python scripts/s2_search.py --api-key YOUR_API_KEY ...
```

#### 3. Reduce Request Frequency

Process in smaller batches:

```bash
# Instead of searching all at once
--max-results 10000

# Split into multiple searches
--max-results 1000  # Run 10 times
```

#### 4. Use Bulk Search

Bulk search is more efficient than relevance search:

```bash
# Default (recommended)
python scripts/s2_search.py --input query.json ...

# Only use if you need relevance ranking (slower, more requests)
python scripts/s2_search.py --input query.json --use-relevance-search ...
```

## PDF Download Fails

### Common Reasons

PDFs may fail to download because they are:

1. **Behind paywall**: Requires institutional access or payment
2. **Not openly accessible**: Author did not provide open access version
3. **Temporarily unavailable**: Server issues or broken links
4. **Large file**: Timeout during download

### ArXiv Fallback (New Feature)

The tool now automatically tries ArXiv as a fallback source:

1. First, attempts to download from `openAccessPdf.url`
2. If unavailable, checks `externalIds.ArXiv` and tries `https://arxiv.org/pdf/{arxiv_id}`

**Check PDF sources:**

```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,pdf_url,pdf_source,arxiv_id" \
  --output papers_with_sources.csv
```

The `pdf_source` column shows:
- `openAccess`: PDF from Semantic Scholar's open access collection
- `arxiv`: PDF from ArXiv

### Behavior

The tool:
- Logs failures to `s2_search.log`
- Continues processing other papers
- Does NOT interrupt the search
- Returns empty string for `pdf_url` field if both sources fail

### Check PDF Availability

Before downloading, check if PDFs exist:

```bash
# First, search without downloading
python scripts/s2_search.py \
  --input query.json \
  --columns "title,pdf_url,pdf_source,arxiv_id" \
  --output papers_with_pdfs.csv

# Count how many have PDFs (non-empty pdf_url)
grep -v ",," papers_with_pdfs.csv | wc -l
```

Or just check the output directly:
```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,pdf_source" \
  | grep -c "arxiv\|openAccess"
```

### Custom PDF Naming

Use `--pdf-naming` to organize downloaded PDFs:

```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,arxiv_id" \
  --download-pdf \
  --pdf-naming "{index}_{title}" \
  --pdf-dir ./pdfs
```

### Solutions

#### 1. Use Verbose Mode

See which PDFs are failing:

```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,open_access_pdf" \
  --download-pdf \
  --pdf-dir ./pdfs \
  --verbose
```

#### 2. Manual Download

If automatic download fails, use the `pdf_url` column:

```bash
# Export PDF URLs (includes ArXiv fallback)
python scripts/s2_search.py \
  --input query.json \
  --columns "title,pdf_url,arxiv_id" \
  --output papers.csv

# Manually download from URLs in the CSV
wget -i <(tail -n +2 papers.csv | cut -d',' -f2)
```

If ArXiv PDFs also fail, try directly:
```bash
# Direct ArXiv download using arxiv_id
wget https://arxiv.org/pdf/2301.12345.pdf
```

#### 3. Increase Timeout

For slow connections, the tool uses 60-second timeout by default. If you need more time, modify the script:

```python
# In s2_search.py, line 231
response = self.session.get(pdf_url, timeout=120, stream=True)  # Increase to 120 seconds
```

## Tips for Best Results

### 1. Use Specific Keywords

```bash
# Too generic - too many irrelevant results
"AI"

# Better - more focused
"artificial intelligence"

# Even better - specific technique
"deep reinforcement learning", "Q-learning", "policy gradient"
```

### 2. Use Multi-Keyword Search for Related Terms

When searching for related terms, use `multiSearch` to get better coverage:

```json
{
  "keywords": ["LLM", "large language model", "GPT", "chatbot"],
  "multiSearch": true,
  "filters": {
    "year": "2023-2024"
  }
}
```

This searches each keyword independently and merges results with `match_keywords` showing which terms matched.

### 3. Combine Filters Wisely

Too many filters exclude relevant papers:

```json
// Too restrictive
{
  "keywords": ["machine learning"],
  "filters": {
    "year": "2024",
    "venue": ["NeurIPS"],
    "publicationTypes": ["Conference"],
    "minCitationCount": 100
  }
}

// Balanced
{
  "keywords": ["machine learning"],
  "filters": {
    "year": "2022-2024",
    "venue": ["NeurIPS", "ICML", "ICLR"]
  }
}
```

### 4. Sort by Citation Count for Impact

Use `sort` filter to find influential papers:

```json
{
  "keywords": ["transformer"],
  "filters": {
    "sort": "citationCount:desc",
    "year": "2020-"
  }
}
```

### 5. Expand Venue Names

Always include multiple venue name variations:

```json
{
  "venue": [
    "NeurIPS",
    "Neural Information Processing Systems",
    "Conference on Neural Information Processing Systems"
  ]
}
```

### 4. Set Realistic max-results

```bash
# Start small
--max-results 100

# Increase if needed
--max-results 500

# Large searches (use with API key)
--max-results 5000
```

### 5. Use API Key for Bulk Searches

```bash
# Set environment variable once
export S2_API_KEY="your_api_key_here"

# Then all searches use it automatically
python scripts/s2_search.py --input query1.json ...
python scripts/s2_search.py --input query2.json ...
```

### 6. Check CSV Output

Use `--verbose` only for debugging:

```bash
# Debugging (verbose)
python scripts/s2_search.py --input query.json --verbose

# Production (quiet, clean output)
python scripts/s2_search.py --input query.json --output results.csv
```

### 7. Validate JSON Input

Before running large searches, validate your JSON:

```bash
# Quick validation
python -m json.tool query.json

# Or use jq
jq . query.json
```

### 8. Process Results Efficiently

```bash
# Use grep to filter results
python scripts/s2_search.py --input query.json | grep "2024"

# Use wc to count results
python scripts/s2_search.py --input query.json | wc -l

# Pipe to other tools
python scripts/s2_search.py --input query.json --columns "title,citation_count" | sort -t',' -k2 -nr | head -10
```

## Common Error Messages

### "No papers found matching the criteria"

**Cause:** Query too restrictive or no matching papers

**Solution:** Broaden keywords, expand venue names, or relax filters

### "API Error 400: Bad request"

**Cause:** Invalid parameter format

**Solution:** Check JSON syntax and parameter values

### "Request timeout after 3 attempts"

**Cause:** Network issues or API server slow

**Solution:** 
1. Check internet connection
2. Retry later
3. Reduce batch size

### "Permission denied: Cannot write to [file]"

**Cause:** No write permission to output directory

**Solution:** 
```bash
# Check permissions
ls -la /path/to/output

# Create directory with write permission
mkdir -p /path/to/output
chmod 755 /path/to/output
```

### "Connection failed after 3 attempts"

**Cause:** Network connectivity issues

**Solution:**
1. Check firewall settings
2. Verify API endpoint accessible: `curl https://api.semanticscholar.org`
3. Check proxy settings if needed

## Getting Help

1. **Check logs**: Review `s2_search.log` for detailed error messages
2. **Verbose mode**: Run with `--verbose` to see API interactions
3. **Test with simple query**: Verify basic functionality works
4. **Check API status**: Visit https://status.semanticscholar.org/

