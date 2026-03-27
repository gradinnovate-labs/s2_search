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
- Download open-access PDFs
- Export paper metadata to CSV

**Trigger phrases:**
- "Search for papers about..."
- "Find academic articles on..."
- "Look up papers from NeurIPS/ICML/ACL..."
- "Search Semantic Scholar for..."
- "Find highly-cited papers in..."

## Quick Start

### Basic Search

```bash
python scripts/s2_search.py \
  --input '{"keywords":["machine learning"],"logic":"OR"}' \
  --columns "title,authors,year,venue"
```

### Advanced Search with Filters

```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count,url" \
  --output results.csv \
  --max-results 2000
```

## Input Format

Create a JSON file or string with the following structure:

```json
{
  "keywords": ["keyword1", "keyword2"],
  "logic": "AND",
  "filters": {
    "year": "2020-2024",
    "venue": ["NeurIPS", "ICML"],
    "publicationTypes": ["Conference"],
    "minCitationCount": 50
  }
}
```

### Parameters

- **keywords** (required): List of search terms
- **logic**: "AND" or "OR" (default: "AND")
- **filters** (optional):
  - **year**: Date range (see formats below)
  - **venue**: Conference/journal names
  - **publicationTypes**: Conference, JournalArticle, Review, etc.
  - **minCitationCount**: Minimum citations

### Year Formats

- `"2024"` - Single year
- `"2020-2024"` - Year range
- `"2020-"` - After 2020
- `"-2024"` - Before 2024

## Venue Name Expansion

Semantic Scholar recognizes various venue name formats. When users provide venue names, expand them to include common variations:

### Common Conference Abbreviations

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| **Machine Learning** | | |
| NeurIPS | Neural Information Processing Systems | Conference on Neural Information Processing Systems, NIPS |
| ICML | International Conference on Machine Learning | |
| ICLR | International Conference on Learning Representations | |
| **Natural Language Processing** | | |
| ACL | Annual Meeting of the Association for Computational Linguistics | Association for Computational Linguistics |
| EMNLP | Conference on Empirical Methods in Natural Language Processing | Empirical Methods in Natural Language Processing |
| NAACL | North American Chapter of the Association for Computational Linguistics | North American Association for Computational Linguistics |
| COLING | International Conference on Computational Linguistics | |
| **Computer Vision** | | |
| CVPR | Computer Vision and Pattern Recognition | Conference on Computer Vision and Pattern Recognition |
| ICCV | IEEE International Conference on Computer Vision | International Conference on Computer Vision |
| **General AI** | | |
| AAAI | AAAI Conference on Artificial Intelligence | Association for the Advancement of Artificial Intelligence |
| IJCAI | International Joint Conference on Artificial Intelligence | |
| **Data & Web** | | |
| KDD | Knowledge Discovery and Data Mining | ACM SIGKDD Conference on Knowledge Discovery and Data Mining |
| WWW | The Web Conference | World Wide Web Conference, International World Wide Web Conference |
| SIGIR | Annual International ACM SIGIR Conference on Research and Development in Information Retrieval | |
| **Robotics** | | |
| ICRA | IEEE International Conference on Robotics and Automation | International Conference on Robotics and Automation |
| **Databases & Systems** | | |
| SIGMOD | ACM SIGMOD International Conference on Management of Data | Management of Data |
| VLDB | Very Large Data Bases | |
| **Graphics** | | |
| SIGGRAPH | ACM SIGGRAPH Conference | Special Interest Group on Computer Graphics |
| **VLSI & EDA** | | |
| DAC | Design Automation Conference | ACM/IEEE Design Automation Conference |
| ICCAD | International Conference on Computer Aided Design | IEEE/ACM International Conference on Computer-Aided Design |
| ISPD | ACM International Symposium on Physical Design | International Symposium on Physical Design |
| ASP-DAC | Asia and South Pacific Design Automation Conference | |
| DATE | Design, Automation and Test in Europe | |
| FPGA Symposium | Symposium on Field Programmable Gate Arrays | ACM/SIGDA International Symposium on Field Programmable Gate Arrays |
| VLSI Design | International Conference on VLSI Design | IEEE International Conference on VLSI Design |
| CAV | International Conference on Computer Aided Verification | Computer Aided Verification |
| ITC | International Test Conference | IEEE International Test Conference |
| CICC | IEEE Custom Integrated Circuits Conference | Custom Integrated Circuits Conference |
| SLIP | International Workshop on System-Level Interconnect Prediction | System Level Interconnect Prediction |

### Common Journal Abbreviations

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| **Top Science Journals** | | |
| Nature | Nature | |
| Science | Science | |
| Cell | Cell | |
| PNAS | Proceedings of the National Academy of Sciences of the United States of America | Proceedings of the National Academy of Sciences |
| **EDA & Hardware** | | |
| TCAD | IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems | IEEE TCAD |
| TODAES | ACM Transactions on Design Automation of Electronic Systems | ACM Trans. Design Autom. Electr. Syst. |
| **Computer Systems** | | |
| ACM TOCS | ACM Transactions on Computer Systems | Transactions on Computer Systems |
| IEEE TPDS | IEEE Transactions on Parallel and Distributed Systems | |
| **Software & AI** | | |
| IEEE TSE | IEEE Transactions on Software Engineering | |
| IEEE TPAMI | IEEE Transactions on Pattern Analysis and Machine Intelligence | |
| IEEE TNNLS | IEEE Transactions on Neural Networks and Learning Systems | |
| JMLR | Journal of Machine Learning Research | Journal of machine learning research |
| **ACM Transactions** | | |
| TODS | ACM Transactions on Database Systems | |
| TOIS | ACM Transactions on Information Systems | |
| Computing Surveys | ACM Computing Surveys | |
| JACM | Journal of the ACM | |

### Venue Expansion Strategy

When a user mentions a venue name or abbreviation:

1. **Identify the venue type**: Conference or Journal
2. **Expand abbreviations**: Include both full name and common variations
3. **Add related venues**: Suggest similar top-tier venues in the same field
4. **Handle multiple formats**: Some venues have multiple valid names

**Example expansion:**
```json
// User says: "Find papers from ACL"
// Expand to:
{
  "venue": [
    "ACL",
    "Annual Meeting of the Association for Computational Linguistics",
    "Association for Computational Linguistics"
  ]
}
```

```json
// User says: "Search TODAES"
// Expand to:
{
  "venue": [
    "TODAES",
    "ACM Transactions on Design Automation of Electronic Systems",
    "ACM Trans. Design Autom. Electr. Syst.",
    "Transactions on Design Automation of Electronic Systems"
  ]
}
```

## Output Columns

Choose which columns to include in the output:

| Column | Description |
|--------|-------------|
| `index` | Row number |
| `title` | Paper title |
| `authors` | Author names (semicolon-separated) |
| `venue` | Publication venue |
| `year` | Publication year |
| `published_date` | Full publication date |
| `citation_count` | Number of citations |
| `abstract` | Paper abstract |
| `url` | Semantic Scholar URL |
| `paper_id` | Unique paper identifier |
| `open_access_pdf` | PDF download URL (if available) |

## Examples

### Example 1: Search Machine Learning Papers

```bash
# Create query.json
cat > query.json << 'EOF'
{
  "keywords": ["transformer", "attention mechanism"],
  "logic": "OR",
  "filters": {
    "year": "2022-2024",
    "minCitationCount": 100
  }
}
EOF

# Run search
python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count,url" \
  --output ml_papers.csv \
  --max-results 500
```

### Example 2: Search Specific Conference

```bash
# User asks: "Find recent papers from NeurIPS and ICML about diffusion models"

# Create query with expanded venue names
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

### Example 3: Search Journal Articles

```bash
# User asks: "Find papers from TODAES about hardware acceleration"

cat > query.json << 'EOF'
{
  "keywords": ["hardware acceleration", "FPGA", "ASIC"],
  "logic": "OR",
  "filters": {
    "venue": [
      "TODAES",
      "ACM Transactions on Design Automation of Electronic Systems",
      "ACM Trans. Design Autom. Electr. Syst."
    ],
    "publicationTypes": ["JournalArticle"],
    "year": "2020-"
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,year,citation_count,abstract" \
  --output todaes_papers.csv
```

### Example 4: Search TCAD Papers

```bash
# User asks: "Search TCAD for EDA papers"

cat > query.json << 'EOF'
{
  "keywords": ["EDA", "placement", "routing"],
  "logic": "OR",
  "filters": {
    "venue": [
      "TCAD",
      "IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems",
      "IEEE TCAD"
    ],
    "publicationTypes": ["JournalArticle"],
    "year": "2022-"
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count" \
  --output tcad_papers.csv
```

### Example 5: Search EDA Conference Papers

```bash
# User asks: "Find papers from DAC and ICCAD about placement and routing"

cat > query.json << 'EOF'
{
  "keywords": ["placement", "routing", "global placement", "detailed routing"],
  "logic": "OR",
  "filters": {
    "venue": [
      "Design Automation Conference",
      "International Conference on Computer Aided Design",
      "IEEE/ACM International Conference on Computer-Aided Design"
    ],
    "publicationTypes": ["Conference"],
    "year": "2020-"
  }
}
EOF

python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,venue,year,citation_count" \
  --output eda_papers.csv \
  --max-results 500
```

### Example 6: Download PDFs

```bash
python scripts/s2_search.py \
  --input query.json \
  --columns "title,authors,year,open_access_pdf" \
  --output papers.csv \
  --download-pdf \
  --pdf-dir ./downloaded_pdfs
```

## API Key Configuration

For higher rate limits, configure an API key:

**Option 1: Environment variable (recommended)**
```bash
export S2_API_KEY="your_api_key_here"
```

**Option 2: Command line**
```bash
python scripts/s2_search.py --api-key YOUR_API_KEY ...
```

**Rate Limits:**
- Without API key: 100 requests / 5 minutes
- With API key: 5,000 requests / 5 minutes

## Common Workflows

### Workflow 1: Literature Review

```bash
# Step 1: Broad search to identify key papers
python scripts/s2_search.py \
  --input '{"keywords":["large language models"],"logic":"OR"}' \
  --columns "title,citation_count,year" \
  --max-results 100

# Step 2: Focused search with venue filter
python scripts/s2_search.py \
  --input focused_query.json \
  --columns "title,authors,venue,year,citation_count,abstract" \
  --output literature_review.csv \
  --max-results 2000
```

### Workflow 2: Track Recent Publications

```bash
# Monitor new papers from top venues
python scripts/s2_search.py \
  --input '{"keywords":["your research topic"],"filters":{"year":"2024","venue":["NeurIPS","ICML","ICLR"]}}' \
  --columns "title,authors,venue,url" \
  --output recent_papers.csv
```

### Workflow 3: Find Highly-Cited Papers

```bash
python scripts/s2_search.py \
  --input '{"keywords":["attention mechanism"],"filters":{"minCitationCount":500,"year":"2017-"}}' \
  --columns "title,authors,year,citation_count" \
  --output highly_cited.csv
```

## Troubleshooting & Tips

For common issues and solutions, see the [Troubleshooting Guide](references/troubleshooting.md):

- **No Results Found**: How to broaden searches and check venue names
- **Rate Limited**: API key configuration and retry strategies
- **PDF Download Fails**: Understanding open access limitations
- **Best Practices**: Tips for effective searching

