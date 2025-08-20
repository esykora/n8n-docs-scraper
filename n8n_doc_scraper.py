#!/usr/bin/env python3
"""
n8n Documentation Scraper
Scrapes the n8n documentation and creates a comprehensive markdown file for LLM context.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import json
from typing import Set, Dict, List
import os
from datetime import datetime

class N8NDocScraper:
    def __init__(self, base_url="https://docs.n8n.io"):
        self.base_url = base_url
        self.visited_urls: Set[str] = set()
        self.content_dict: Dict[str, Dict] = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; Documentation Scraper; +http://localhost)'
        })
        
    def is_valid_doc_url(self, url: str) -> bool:
        """Check if URL is a valid n8n documentation page"""
        parsed = urlparse(url)
        # Only scrape URLs from the docs domain
        if not parsed.netloc.startswith('docs.n8n.io'):
            return False
        # Avoid assets, images, etc.
        excluded_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js', '.pdf']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        return True
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract main content from the page"""
        content = {
            'url': url,
            'title': '',
            'content': '',
            'code_blocks': [],
            'category': self.categorize_url(url)
        }
        
        # Try to find the main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if not main_content:
            # Fallback to finding content by common class names
            main_content = soup.find('div', class_=re.compile('doc|content|main', re.I))
        
        if main_content:
            # Extract title
            title = soup.find('h1')
            if title:
                content['title'] = title.get_text(strip=True)
            
            # Extract code blocks separately to preserve formatting
            code_blocks = main_content.find_all(['pre', 'code'])
            for i, block in enumerate(code_blocks):
                code_text = block.get_text(strip=False)
                content['code_blocks'].append({
                    'index': i,
                    'language': block.get('class', [''])[0] if block.get('class') else '',
                    'code': code_text
                })
                # Replace with placeholder
                block.string = f"[CODE_BLOCK_{i}]"
            
            # Extract main text content
            text_content = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th']):
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short text
                    if element.name.startswith('h'):
                        text_content.append(f"\n{'#' * int(element.name[1])} {text}\n")
                    elif element.name == 'li':
                        text_content.append(f"- {text}")
                    else:
                        text_content.append(text)
            
            content['content'] = '\n\n'.join(text_content)
        
        return content
    
    def categorize_url(self, url: str) -> str:
        """Categorize URL based on its path"""
        path = urlparse(url).path.lower()
        
        # Define categories based on URL patterns
        if '/nodes/' in path or '/integrations/' in path:
            return 'Nodes & Integrations'
        elif '/workflows/' in path:
            return 'Workflows'
        elif '/api/' in path:
            return 'API Reference'
        elif '/hosting/' in path or '/deploy/' in path:
            return 'Hosting & Deployment'
        elif '/troubleshooting/' in path or '/errors/' in path:
            return 'Troubleshooting'
        elif '/courses/' in path or '/tutorials/' in path:
            return 'Tutorials & Courses'
        elif '/core-concepts/' in path or '/getting-started/' in path:
            return 'Core Concepts'
        elif '/credentials/' in path:
            return 'Credentials'
        elif '/code/' in path or '/expressions/' in path:
            return 'Code & Expressions'
        else:
            return 'General Documentation'
    
    def scrape_page(self, url: str) -> Set[str]:
        """Scrape a single page and return found links"""
        if url in self.visited_urls:
            return set()
        
        print(f"Scraping: {url}")
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = self.extract_content(soup, url)
            if content['content'] or content['code_blocks']:
                self.content_dict[url] = content
            
            # Find all links
            links = set()
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                # Remove fragment identifiers
                absolute_url = absolute_url.split('#')[0]
                if self.is_valid_doc_url(absolute_url) and absolute_url not in self.visited_urls:
                    links.add(absolute_url)
            
            # Be respectful with rate limiting
            time.sleep(0.5)
            
            return links
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return set()
    
    def crawl(self, start_urls: List[str] = None, max_pages: int = 500):
        """Crawl the documentation starting from given URLs"""
        if start_urls is None:
            start_urls = [
                f"{self.base_url}/",
                f"{self.base_url}/getting-started/",
                f"{self.base_url}/nodes/",
                f"{self.base_url}/workflows/",
                f"{self.base_url}/api/",
                f"{self.base_url}/hosting/",
                f"{self.base_url}/code/",
                f"{self.base_url}/troubleshooting/"
            ]
        
        urls_to_visit = set(start_urls)
        
        while urls_to_visit and len(self.visited_urls) < max_pages:
            url = urls_to_visit.pop()
            new_urls = self.scrape_page(url)
            urls_to_visit.update(new_urls - self.visited_urls)
            
            print(f"Progress: {len(self.visited_urls)} pages scraped, {len(urls_to_visit)} in queue")
    
    def generate_markdown(self) -> str:
        """Generate a comprehensive markdown document from scraped content"""
        markdown_parts = []
        
        # Add header
        markdown_parts.append(f"""# n8n Documentation
*Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Total pages: {len(self.content_dict)}*

## Table of Contents
""")
        
        # Group content by category
        categories = {}
        for url, content in self.content_dict.items():
            category = content['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(content)
        
        # Generate TOC
        for category in sorted(categories.keys()):
            markdown_parts.append(f"- [{category}](#{category.lower().replace(' ', '-').replace('&', 'and')})")
        
        markdown_parts.append("\n---\n")
        
        # Add content by category
        for category in sorted(categories.keys()):
            markdown_parts.append(f"\n## {category}\n")
            
            for content in categories[category]:
                # Add title and URL
                if content['title']:
                    markdown_parts.append(f"\n### {content['title']}")
                markdown_parts.append(f"*Source: {content['url']}*\n")
                
                # Add main content
                text = content['content']
                
                # Restore code blocks
                for code_block in content['code_blocks']:
                    placeholder = f"[CODE_BLOCK_{code_block['index']}]"
                    code_markdown = f"\n```{code_block['language']}\n{code_block['code']}\n```\n"
                    text = text.replace(placeholder, code_markdown)
                
                markdown_parts.append(text)
                markdown_parts.append("\n---\n")
        
        return '\n'.join(markdown_parts)
    
    def save_markdown(self, filename: str = "n8n_documentation.md"):
        """Save the generated markdown to a file"""
        markdown = self.generate_markdown()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Documentation saved to {filename}")
        print(f"File size: {os.path.getsize(filename) / 1024 / 1024:.2f} MB")
        
        # Also save a JSON version for structured access
        json_filename = filename.replace('.md', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.content_dict, f, indent=2)
        print(f"JSON data saved to {json_filename}")

def main():
    """Main execution function"""
    print("Starting n8n Documentation Scraper...")
    print("=" * 50)
    
    scraper = N8NDocScraper()
    
    # You can customize the max_pages parameter based on your needs
    # Set to None to scrape everything (be careful - this might take a while)
    scraper.crawl(max_pages=200)
    
    print("\n" + "=" * 50)
    print(f"Scraping complete! Scraped {len(scraper.visited_urls)} pages")
    print("Generating markdown document...")
    
    scraper.save_markdown("n8n_documentation.md")
    
    print("\nDone! You can now use n8n_documentation.md as context for your LLM.")

if __name__ == "__main__":
    main()
