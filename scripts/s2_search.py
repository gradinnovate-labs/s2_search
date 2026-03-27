#!/usr/bin/env python3
"""
Semantic Scholar (S2) Paper Search Tool
搜尋 Semantic Scholar 論文並下載
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class S2SearchError(Exception):
    """Base exception for S2 search errors"""
    pass


class APIError(S2SearchError):
    """API related errors"""
    pass


class ValidationError(S2SearchError):
    """Input validation errors"""
    pass


class S2SearchClient:
    """Semantic Scholar API client with retry and error handling"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]
    
    FIELD_MAPPING = {
        'index': None,
        'title': 'title',
        'paper_title': 'title',
        'citation_count': 'citationCount',
        'citationcount': 'citationCount',
        'authors': 'authors',
        'venue': 'venue',
        'published_date': 'publicationDate',
        'publicationdate': 'publicationDate',
        'year': 'year',
        'abstract': 'abstract',
        'url': 'url',
        'paper_id': 'paperId',
        'paperid': 'paperId',
        'open_access_pdf': 'openAccessPdf',
        'openaccesspdf': 'openAccessPdf',
        'external_ids': 'externalIds',
        'externalids': 'externalIds',
        'arxiv_id': 'externalIds',
        'arxivid': 'externalIds',
        'doi': 'externalIds'
    }
    
    SUPPORTED_PUBLICATION_TYPES = [
        'Review', 'JournalArticle', 'CaseReport', 'ClinicalTrial',
        'Conference', 'Dataset', 'Editorial', 'LettersAndComments',
        'MetaAnalysis', 'News', 'Study', 'Book', 'BookSection'
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        if self.api_key:
            session.headers.update({"x-api-key": self.api_key})
            
        return session
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Requesting {endpoint} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 400:
                    error_msg = response.json().get('message', 'Bad request')
                    raise APIError(f"API Error 400: {error_msg}")
                else:
                    raise APIError(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAYS[attempt])
                else:
                    raise APIError("Request timeout after 3 attempts")
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAYS[attempt])
                else:
                    raise APIError(f"Connection failed after 3 attempts: {e}")
        
        raise APIError("Max retries exceeded")
    
    def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        venue: Optional[List[str]] = None,
        publication_types: Optional[List[str]] = None,
        min_citation_count: Optional[int] = None,
        fields: Optional[List[str]] = None,
        max_results: int = 1000,
        use_bulk: bool = True,
        sort: Optional[str] = None
    ) -> List[Dict]:
        
        if fields is None:
            fields = ['paperId', 'title', 'citationCount', 'authors', 'venue', 
                     'year', 'publicationDate', 'abstract', 'url', 'openAccessPdf', 'externalIds']
        
        api_fields = self._map_fields_to_api(fields)
        
        params: Dict[str, Any] = {
            'query': query,
            'fields': ','.join(api_fields)
        }
        
        if year:
            params['year'] = year
        if venue:
            params['venue'] = ','.join(venue)
        if publication_types:
            params['publicationTypes'] = ','.join(publication_types)
        if min_citation_count:
            params['minCitationCount'] = min_citation_count
        if sort:
            params['sort'] = sort
        
        all_papers = []
        endpoint = "/paper/search/bulk" if use_bulk else "/paper/search"
        
        if use_bulk:
            params['limit'] = min(1000, max_results)
        else:
            params['limit'] = min(100, max_results)
        
        token = None
        while len(all_papers) < max_results:
            if token:
                params['token'] = token
            
            try:
                response = self._make_request(endpoint, params)
            except APIError as e:
                logger.error(f"Search failed: {e}")
                raise
            
            papers = response.get('data', [])
            if not papers:
                break
            
            all_papers.extend(papers)
            logger.info(f"Retrieved {len(papers)} papers (total: {len(all_papers)})")
            
            if len(all_papers) >= max_results:
                all_papers = all_papers[:max_results]
                break
            
            if use_bulk:
                token = response.get('token')
                if not token:
                    break
            else:
                if len(papers) < params['limit']:
                    break
                params['offset'] = len(all_papers)
        
        return all_papers
    
    def _map_fields_to_api(self, user_fields: List[str]) -> List[str]:
        api_fields = []
        for field in user_fields:
            field_lower = field.lower().replace(' ', '_')
            if field_lower in self.FIELD_MAPPING:
                api_field = self.FIELD_MAPPING[field_lower]
                if api_field and api_field not in api_fields:
                    if api_field == 'authors':
                        api_fields.append('authors')
                    elif api_field == 'openAccessPdf':
                        api_fields.append('openAccessPdf')
                    elif api_field == 'externalIds':
                        api_fields.append('externalIds')
                    else:
                        api_fields.append(api_field)
            else:
                logger.warning(f"Unknown field '{field}', skipping")
        
        if 'paperId' not in api_fields:
            api_fields.insert(0, 'paperId')
        
        if 'externalIds' not in api_fields:
            api_fields.append('externalIds')
        
        return api_fields
    
    def download_pdf(self, pdf_url: str, output_path: str) -> bool:
        try:
            logger.info(f"Downloading PDF from {pdf_url}")
            response = self.session.get(pdf_url, timeout=60, stream=True)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"PDF saved to {output_path}")
                return True
            else:
                logger.error(f"Failed to download PDF: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"PDF download error: {e}")
            return False


def validate_json_input(input_source: str) -> Dict:
    if os.path.exists(input_source) and os.path.isfile(input_source):
        logger.info(f"Reading from file: {input_source}")
        try:
            with open(input_source, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format in file: {e}")
    else:
        logger.info("Parsing input as JSON string")
        try:
            data = json.loads(input_source)
        except json.JSONDecodeError as e:
            if input_source.endswith('.json'):
                raise ValidationError(f"File not found: {input_source}")
            raise ValidationError(f"Invalid JSON string: {e}")
    
    if not isinstance(data, dict):
        raise ValidationError("Input JSON must be an object")
    
    return data


def validate_date_format(date_str: str) -> bool:
    if ':' in date_str:
        parts = date_str.split(':')
        if len(parts) == 2:
            start, end = parts
            if start and not validate_date_format(start):
                return False
            if end and not validate_date_format(end):
                return False
            return True
        return False
    
    if re.match(r'^\d{4}-\d{4}$', date_str):
        parts = date_str.split('-')
        start_year, end_year = int(parts[0]), int(parts[1])
        return 1900 <= start_year <= 2100 and 1900 <= end_year <= 2100 and start_year <= end_year
    
    if date_str.endswith('-') or date_str.startswith('-'):
        core = date_str.strip('-')
        return bool(re.match(r'^\d{4}$', core))
    
    if re.match(r'^\d{4}$', date_str):
        year = int(date_str)
        return 1900 <= year <= 2100
    
    if re.match(r'^\d{4}-\d{2}$', date_str):
        parts = date_str.split('-')
        year, month = int(parts[0]), int(parts[1])
        return 1900 <= year <= 2100 and 1 <= month <= 12
    
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        try:
            parts = date_str.split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            datetime(year, month, day)
            return True
        except (ValueError, TypeError):
            return False
    
    return False


def build_search_query(input_data: Dict) -> tuple:
    keywords = input_data.get('keywords', [])
    logic = input_data.get('logic', 'AND').upper()
    multi_search = input_data.get('multiSearch', False)
    
    if isinstance(keywords, str):
        keywords = [keywords]
    
    if not keywords:
        raise ValidationError("No keywords provided")
    
    if multi_search:
        query = None
    elif logic == 'OR':
        query = ' | '.join(keywords)
    elif logic == 'AND':
        query = ' + '.join(keywords)
    else:
        query = ' '.join(keywords)
    
    filters = input_data.get('filters', {})
    
    year = filters.get('year')
    if year and not validate_date_format(str(year)):
        raise ValidationError(f"Invalid year format: {year}")
    
    venue = filters.get('venue')
    if isinstance(venue, str):
        venue = [venue]
    
    publication_types = filters.get('publicationTypes')
    if isinstance(publication_types, str):
        publication_types = [publication_types]
    
    if publication_types:
        invalid_types = [pt for pt in publication_types 
                        if pt not in S2SearchClient.SUPPORTED_PUBLICATION_TYPES]
        if invalid_types:
            logger.warning(f"Unsupported publication types: {invalid_types}")
    
    min_citation_count = filters.get('minCitationCount')
    if min_citation_count is not None:
        try:
            min_citation_count = int(min_citation_count)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid minCitationCount: {min_citation_count}")
    
    sort = filters.get('sort')
    
    return query, year, venue, publication_types, min_citation_count, sort, keywords, multi_search


def safe_get(data: Dict, key: str, default: Any = "") -> Any:
    value = data.get(key)
    if value is None:
        return default
    return value


def format_authors(authors: Optional[List[Dict]]) -> str:
    if not authors:
        return ""
    return "; ".join([a.get('name', '') for a in authors if a.get('name')])


def format_pdf_url(open_access_pdf: Any) -> str:
    if isinstance(open_access_pdf, dict):
        return open_access_pdf.get('url', '')
    return ""


def get_arxiv_id(external_ids: Any) -> Optional[str]:
    if not isinstance(external_ids, dict):
        return None
    return external_ids.get('ArXiv') or external_ids.get('arXiv') or external_ids.get('arxiv')


def get_doi(external_ids: Any) -> Optional[str]:
    if not isinstance(external_ids, dict):
        return None
    return external_ids.get('DOI') or external_ids.get('doi')


def build_arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}"


def get_pdf_url_with_fallback(paper: Dict) -> tuple:
    """
    Returns (pdf_url, source) tuple.
    source is 'openAccess' or 'arxiv' or None
    """
    open_access_pdf = paper.get('openAccessPdf')
    if isinstance(open_access_pdf, dict) and open_access_pdf.get('url'):
        return open_access_pdf['url'], 'openAccess'
    
    arxiv_id = get_arxiv_id(paper.get('externalIds'))
    if arxiv_id:
        return build_arxiv_pdf_url(arxiv_id), 'arxiv'
    
    return None, None


def format_external_ids(external_ids: Any, target: Optional[str] = None) -> str:
    if not isinstance(external_ids, dict):
        return ""
    
    if target:
        target_lower = target.lower()
        if target_lower in ['arxiv', 'arxiv_id']:
            return external_ids.get('ArXiv', '') or external_ids.get('arXiv', '')
        elif target_lower == 'doi':
            return external_ids.get('DOI', '')
        return str(external_ids.get(target, ''))
    
    parts = []
    for key in ['ArXiv', 'DOI', 'CorpusId', 'MAG', 'ACL', 'PMID', 'PMCID', 'DBLP']:
        if key in external_ids:
            parts.append(f"{key}:{external_ids[key]}")
    return "; ".join(parts)


def export_to_csv(papers: List[Dict], columns: List[str], output_path: Optional[str] = None):
    column_mapping = {
        'index': lambda p, i: i + 1,
        'title': lambda p, i: safe_get(p, 'title'),
        'paper_title': lambda p, i: safe_get(p, 'title'),
        'citation_count': lambda p, i: safe_get(p, 'citationCount', 0),
        'citationcount': lambda p, i: safe_get(p, 'citationCount', 0),
        'authors': lambda p, i: format_authors(safe_get(p, 'authors', [])),
        'venue': lambda p, i: safe_get(p, 'venue'),
        'published_date': lambda p, i: safe_get(p, 'publicationDate') or safe_get(p, 'year'),
        'publicationdate': lambda p, i: safe_get(p, 'publicationDate') or safe_get(p, 'year'),
        'year': lambda p, i: safe_get(p, 'year'),
        'abstract': lambda p, i: safe_get(p, 'abstract'),
        'url': lambda p, i: safe_get(p, 'url'),
        'paper_id': lambda p, i: safe_get(p, 'paperId'),
        'paperid': lambda p, i: safe_get(p, 'paperId'),
        'open_access_pdf': lambda p, i: format_pdf_url(safe_get(p, 'openAccessPdf')),
        'openaccesspdf': lambda p, i: format_pdf_url(safe_get(p, 'openAccessPdf')),
        'external_ids': lambda p, i: format_external_ids(safe_get(p, 'externalIds')),
        'externalids': lambda p, i: format_external_ids(safe_get(p, 'externalIds')),
        'arxiv_id': lambda p, i: get_arxiv_id(safe_get(p, 'externalIds')) or '',
        'arxivid': lambda p, i: get_arxiv_id(safe_get(p, 'externalIds')) or '',
        'doi': lambda p, i: get_doi(safe_get(p, 'externalIds')) or '',
        'pdf_url': lambda p, i: get_pdf_url_with_fallback(p)[0] or '',
        'pdfurl': lambda p, i: get_pdf_url_with_fallback(p)[0] or '',
        'pdf_source': lambda p, i: get_pdf_url_with_fallback(p)[1] or '',
        'pdfsource': lambda p, i: get_pdf_url_with_fallback(p)[1] or ''
    }
    
    try:
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            file_obj = open(output_path, 'w', newline='', encoding='utf-8')
        else:
            file_obj = sys.stdout
        
        with file_obj as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            
            for idx, paper in enumerate(papers):
                row = []
                for col in columns:
                    col_lower = col.lower().replace(' ', '_')
                    if col_lower in column_mapping:
                        row.append(column_mapping[col_lower](paper, idx))
                    else:
                        logger.warning(f"Unknown column '{col}', using empty value")
                        row.append('')
                writer.writerow(row)
        
        if output_path:
            logger.info(f"Exported {len(papers)} papers to {output_path}")
        else:
            logger.info(f"Exported {len(papers)} papers to stdout")
        
    except PermissionError:
        raise ValidationError(f"Permission denied: Cannot write to {output_path}")
    except Exception as e:
        raise ValidationError(f"Failed to write CSV: {e}")


def export_to_json(papers: List[Dict], columns: List[str], output_path: Optional[str] = None):
    column_mapping = {
        'index': lambda p, i: i + 1,
        'title': lambda p, i: safe_get(p, 'title'),
        'paper_title': lambda p, i: safe_get(p, 'title'),
        'citation_count': lambda p, i: safe_get(p, 'citationCount', 0),
        'citationcount': lambda p, i: safe_get(p, 'citationCount', 0),
        'authors': lambda p, i: format_authors(safe_get(p, 'authors', [])),
        'venue': lambda p, i: safe_get(p, 'venue'),
        'published_date': lambda p, i: safe_get(p, 'publicationDate') or safe_get(p, 'year'),
        'publicationdate': lambda p, i: safe_get(p, 'publicationDate') or safe_get(p, 'year'),
        'year': lambda p, i: safe_get(p, 'year'),
        'abstract': lambda p, i: safe_get(p, 'abstract'),
        'url': lambda p, i: safe_get(p, 'url'),
        'paper_id': lambda p, i: safe_get(p, 'paperId'),
        'paperid': lambda p, i: safe_get(p, 'paperId'),
        'open_access_pdf': lambda p, i: format_pdf_url(safe_get(p, 'openAccessPdf')),
        'openaccesspdf': lambda p, i: format_pdf_url(safe_get(p, 'openAccessPdf')),
        'external_ids': lambda p, i: safe_get(p, 'externalIds', {}),
        'externalids': lambda p, i: safe_get(p, 'externalIds', {}),
        'arxiv_id': lambda p, i: get_arxiv_id(safe_get(p, 'externalIds')) or None,
        'arxivid': lambda p, i: get_arxiv_id(safe_get(p, 'externalIds')) or None,
        'doi': lambda p, i: get_doi(safe_get(p, 'externalIds')) or None,
        'pdf_url': lambda p, i: get_pdf_url_with_fallback(p)[0],
        'pdfurl': lambda p, i: get_pdf_url_with_fallback(p)[0],
        'pdf_source': lambda p, i: get_pdf_url_with_fallback(p)[1],
        'pdfsource': lambda p, i: get_pdf_url_with_fallback(p)[1],
        'match_keywords': lambda p, i: p.get('_match_keywords', [])
    }
    
    result = []
    for idx, paper in enumerate(papers):
        row = {}
        for col in columns:
            col_lower = col.lower().replace(' ', '_')
            if col_lower in column_mapping:
                row[col] = column_mapping[col_lower](paper, idx)
            else:
                row[col] = paper.get(col)
        result.append(row)
    
    try:
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"Exported {len(papers)} papers to {output_path}")
        else:
            print(json_str)
            logger.info(f"Exported {len(papers)} papers to stdout")
            
    except PermissionError:
        raise ValidationError(f"Permission denied: Cannot write to {output_path}")
    except Exception as e:
        raise ValidationError(f"Failed to write JSON: {e}")


def sanitize_filename(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    sanitized = sanitized.strip(' .')
    return sanitized[:200] if sanitized else 'unnamed'


def build_pdf_filename(template: str, paper: Dict, index: int) -> str:
    paper_id = safe_get(paper, 'paperId', 'unknown')
    title = safe_get(paper, 'title', 'untitled')
    year = safe_get(paper, 'year', '')
    arxiv_id = get_arxiv_id(safe_get(paper, 'externalIds')) or ''
    
    filename = template
    filename = filename.replace('{index}', str(index + 1).zfill(4))
    filename = filename.replace('{paperId}', sanitize_filename(paper_id))
    filename = filename.replace('{paper_id}', sanitize_filename(paper_id))
    filename = filename.replace('{title}', sanitize_filename(title)[:100])
    filename = filename.replace('{year}', str(year) if year else 'unknown')
    filename = filename.replace('{arxivId}', sanitize_filename(arxiv_id) if arxiv_id else 'no_arxiv')
    filename = filename.replace('{arxiv_id}', sanitize_filename(arxiv_id) if arxiv_id else 'no_arxiv')
    
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    return filename


def multi_keyword_search(
    client: S2SearchClient,
    keywords: List[str],
    year: Optional[str] = None,
    venue: Optional[List[str]] = None,
    publication_types: Optional[List[str]] = None,
    min_citation_count: Optional[int] = None,
    fields: Optional[List[str]] = None,
    max_results_per_keyword: int = 500,
    use_bulk: bool = True,
    sort: Optional[str] = None
) -> List[Dict]:
    """
    Search each keyword independently and merge results with deduplication.
    Each paper will have a _match_keywords field listing which keywords matched.
    """
    all_papers = {}  # paperId -> paper data
    
    for keyword in keywords:
        logger.info(f"Searching for keyword: {keyword}")
        papers = client.search_papers(
            query=keyword,
            year=year,
            venue=venue,
            publication_types=publication_types,
            min_citation_count=min_citation_count,
            fields=fields,
            max_results=max_results_per_keyword,
            use_bulk=use_bulk,
            sort=sort
        )
        
        for paper in papers:
            paper_id = paper.get('paperId')
            if paper_id:
                if paper_id in all_papers:
                    all_papers[paper_id]['_match_keywords'].append(keyword)
                else:
                    paper['_match_keywords'] = [keyword]
                    all_papers[paper_id] = paper
        
        logger.info(f"Found {len(papers)} papers for '{keyword}' (total unique: {len(all_papers)})")
    
    return list(all_papers.values())


DEFAULT_COLUMNS = ['index', 'title', 'authors', 'venue', 'year', 'citation_count', 
                   'abstract', 'url', 'paper_id', 'open_access_pdf', 'external_ids', 
                   'arxiv_id', 'doi', 'pdf_url', 'pdf_source']

def main():
    parser = argparse.ArgumentParser(
        description='Search Semantic Scholar papers and export to CSV/JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # From JSON file
  s2_search.py --input query.json --output results.csv
  
  # From JSON string
  s2_search.py --input '{"keywords":["machine learning"],"logic":"OR"}' --output-format json
  
  # With specific columns
  s2_search.py --input query.json --columns "title,authors,year" --output results.csv

  # Multi-keyword independent search with dedup
  s2_search.py --input '{"keywords":["LLM","large language model"],"multiSearch":true}' --output-format json
  
  # Sort by citation count
  s2_search.py --input '{"keywords":["transformer"],"filters":{"sort":"citationCount:desc"}}' --output results.csv

  # Custom PDF naming
  s2_search.py --input query.json --download-pdf --pdf-naming "{index}_{title}"

Input JSON format (file or string):
  {
    "keywords": ["machine learning", "deep learning"],
    "logic": "AND",
    "multiSearch": false,
    "filters": {
      "year": "2020-2024",
      "venue": ["NeurIPS", "ICML"],
      "publicationTypes": ["Conference"],
      "minCitationCount": 10,
      "sort": "citationCount:desc"
    }
  }

Default columns (when --columns not specified):
  index, title, authors, venue, year, citation_count, abstract, url, paper_id,
  open_access_pdf, external_ids, arxiv_id, doi, pdf_url, pdf_source

All available columns:
  index, title, citation_count, authors, venue, published_date, year, abstract, url, paper_id, 
  open_access_pdf, external_ids, arxiv_id, doi, pdf_url, pdf_source, match_keywords

PDF naming template variables:
  {index}, {paperId}, {title}, {year}, {arxivId}
        """
    )
    
    parser.add_argument('--input', required=True, 
                       help='JSON file path or JSON string with search criteria')
    parser.add_argument('--columns', help='Comma-separated column names (default: all columns)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--output-format', choices=['csv', 'json'], default='csv',
                       help='Output format: csv or json (default: csv)')
    parser.add_argument('--max-results', type=int, default=1000, help='Maximum number of results (default: 1000)')
    parser.add_argument('--download-pdf', action='store_true', help='Download PDFs (with ArXiv fallback)')
    parser.add_argument('--pdf-dir', default='./pdfs', help='Directory for downloaded PDFs')
    parser.add_argument('--pdf-naming', default='{paperId}.pdf',
                       help='PDF naming template: {index}, {paperId}, {title}, {year}, {arxivId} (default: {paperId}.pdf)')
    parser.add_argument('--use-relevance-search', action='store_true', 
                       help='Use relevance search instead of bulk search (max 1000 results)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Show detailed log messages (default: quiet mode)')
    
    args = parser.parse_args()
    
    handlers: List[logging.Handler] = [logging.FileHandler('s2_search.log')]
    if args.verbose:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    api_key = os.environ.get('S2_API_KEY') or os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
    if api_key:
        logger.info("Using API key for higher rate limits")
    
    try:
        logger.info("Starting S2 search...")
        
        logger.info(f"Validating input file: {args.input}")
        input_data = validate_json_input(args.input)
        
        logger.info("Building search query...")
        query, year, venue, pub_types, min_citations, sort, keywords, multi_search = build_search_query(input_data)
        if query:
            logger.info(f"Query: {query}")
        if sort:
            logger.info(f"Sort: {sort}")
        
        if args.columns:
            columns = [col.strip() for col in args.columns.split(',')]
        else:
            columns = DEFAULT_COLUMNS.copy()
            if multi_search and 'match_keywords' not in columns:
                columns.append('match_keywords')
        logger.info(f"Columns: {columns}")
        
        client = S2SearchClient(api_key=api_key)
        
        logger.info(f"Searching papers (max {args.max_results} results)...")
        
        if multi_search:
            logger.info(f"Multi-keyword search mode: {len(keywords)} keywords")
            papers = multi_keyword_search(
                client=client,
                keywords=keywords,
                year=year,
                venue=venue,
                publication_types=pub_types,
                min_citation_count=min_citations,
                fields=columns,
                max_results_per_keyword=args.max_results,
                use_bulk=not args.use_relevance_search,
                sort=sort
            )
        else:
            papers = client.search_papers(
                query=query,
                year=year,
                venue=venue,
                publication_types=pub_types,
                min_citation_count=min_citations,
                fields=columns,
                max_results=args.max_results,
                use_bulk=not args.use_relevance_search,
                sort=sort
            )
        
        if not papers:
            logger.warning("No papers found matching the criteria")
        else:
            logger.info(f"Found {len(papers)} papers")
        
        if args.output:
            logger.info(f"Exporting to {args.output_format.upper()}: {args.output}")
        else:
            logger.info(f"Exporting to stdout as {args.output_format.upper()}")
        
        if args.output_format == 'json':
            export_to_json(papers, columns, args.output)
        else:
            export_to_csv(papers, columns, args.output)
        
        if args.download_pdf and papers:
            logger.info(f"Downloading PDFs to {args.pdf_dir} (with ArXiv fallback)...")
            pdf_count = 0
            arxiv_count = 0
            for idx, paper in enumerate(papers):
                pdf_url, source = get_pdf_url_with_fallback(paper)
                if pdf_url:
                    paper_id = safe_get(paper, 'paperId')
                    filename = build_pdf_filename(args.pdf_naming, paper, idx)
                    output_path = os.path.join(args.pdf_dir, filename)
                    if client.download_pdf(pdf_url, output_path):
                        pdf_count += 1
                        if source == 'arxiv':
                            arxiv_count += 1
            logger.info(f"Downloaded {pdf_count} PDFs ({arxiv_count} from ArXiv)")
        
        logger.info("Search completed successfully!")
        if args.output:
            print(f"\n✓ Successfully exported {len(papers)} papers to {args.output}", file=sys.stderr)
        else:
            print(f"\n✓ Successfully exported {len(papers)} papers to stdout", file=sys.stderr)
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        logger.error(f"API error: {e}")
        print(f"\n✗ API Error: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        print("\n✗ Search interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(99)


if __name__ == '__main__':
    main()
