# n8n Documentation Scraper & LLM Context Builder

This toolkit helps you scrape n8n documentation and create a comprehensive markdown file that can be used as context for Large Language Models (LLMs) to assist with n8n workflow development and troubleshooting.

## 📁 Files Included

1. **`n8n_doc_scraper.py`** - Python script that scrapes n8n documentation
2. **`requirements.txt`** - Python dependencies
3. **`n8n_llm_prompt_template.md`** - Prompt template for using with LLMs
4. **`README_n8n_docs.md`** - This file

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Scraper

```bash
python n8n_doc_scraper.py
```

This will:
- Scrape up to 200 pages from n8n documentation (configurable)
- Create `n8n_documentation.md` with all content
- Create `n8n_documentation.json` for structured access
- Organize content by categories (Nodes, Workflows, Troubleshooting, etc.)

### Step 3: Customize Scraping (Optional)

Edit `n8n_doc_scraper.py` to adjust:
- `max_pages`: Number of pages to scrape (line 248)
- `start_urls`: Initial URLs to begin crawling (lines 158-166)
- Rate limiting: Delay between requests (line 142)

For comprehensive documentation coverage:
```python
scraper.crawl(max_pages=500)  # Or None for unlimited
```

## 📊 Output Files

### `n8n_documentation.md`
- Comprehensive markdown document
- Organized by categories
- Includes table of contents
- Preserves code examples and formatting
- Typical size: 2-10 MB depending on pages scraped

### `n8n_documentation.json`
- Structured JSON data
- Useful for programmatic access
- Contains URLs, titles, content, and code blocks

## 🤖 Using with LLMs

### Option 1: Direct Context Loading

1. Open your preferred LLM interface (ChatGPT, Claude, etc.)
2. Upload or paste the `n8n_documentation.md` file as context
3. Use the prompt template from `n8n_llm_prompt_template.md`

### Option 2: API Integration

```python
import openai

# Load documentation
with open('n8n_documentation.md', 'r') as f:
    n8n_docs = f.read()

# Load prompt template
with open('n8n_llm_prompt_template.md', 'r') as f:
    prompt_template = f.read()

# Create system message
system_message = f"{prompt_template}\n\nDocumentation Context:\n{n8n_docs}"

# Use with OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": "How do I create a webhook trigger?"}
    ]
)
```

### Option 3: Local LLM

For Ollama, LM Studio, or other local LLMs:
```bash
# Example with Ollama
ollama run llama2 --system "$(cat n8n_llm_prompt_template.md n8n_documentation.md)"
```

## 📝 Example LLM Queries

Once your LLM has the documentation context, you can ask:

- **Workflow Building**: "Create a workflow that monitors a Slack channel and saves messages to Google Sheets"
- **Troubleshooting**: "My PostgreSQL node is throwing a connection timeout error"
- **Node Configuration**: "How do I set up OAuth2 for the Google Drive node?"
- **Expressions**: "Write an expression to extract email domain from an email address"
- **Best Practices**: "What's the best way to handle errors in a workflow with multiple API calls?"

## ⚙️ Advanced Configuration

### Custom Categories

Edit the `categorize_url()` method in the scraper to add custom categories:

```python
def categorize_url(self, url: str) -> str:
    path = urlparse(url).path.lower()
    if '/your-pattern/' in path:
        return 'Your Category'
    # ... rest of the logic
```

### Selective Scraping

To scrape only specific sections:

```python
scraper = N8NDocScraper()
scraper.crawl(
    start_urls=["https://docs.n8n.io/workflows/"],
    max_pages=50
)
```

### Content Filtering

Modify `extract_content()` to filter specific content:

```python
def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
    # Skip certain pages
    if 'skip-this' in url:
        return {}
    # ... rest of the logic
```

## 🔧 Troubleshooting

### Issue: Scraper gets blocked
**Solution**: Increase delay between requests in `scrape_page()`:
```python
time.sleep(2)  # Increase from 0.5 to 2 seconds
```

### Issue: Missing content
**Solution**: The site might use JavaScript rendering. Consider using Selenium:
```python
from selenium import webdriver
driver = webdriver.Chrome()
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
```

### Issue: File too large for LLM
**Solution**: 
1. Reduce `max_pages` when scraping
2. Split the markdown into chunks
3. Use only relevant sections for specific queries

## 📊 Performance Tips

1. **Initial Test Run**: Start with `max_pages=50` to test
2. **Incremental Scraping**: Save progress periodically
3. **Caching**: The scraper avoids re-visiting URLs
4. **Rate Limiting**: Respect the site with appropriate delays

## 🔄 Updating Documentation

Run the scraper periodically to keep documentation current:

```bash
# Weekly update via cron
0 0 * * 0 cd /path/to/scripts && python n8n_doc_scraper.py
```

## 📚 Additional Resources

- [n8n Official Documentation](https://docs.n8n.io)
- [n8n Community Forum](https://community.n8n.io)
- [n8n GitHub Repository](https://github.com/n8n-io/n8n)

## 💡 Pro Tips

1. **Version Tracking**: Include n8n version in your documentation filename
2. **Selective Context**: For specific tasks, extract only relevant sections
3. **Combine Sources**: Add n8n forum posts or GitHub issues for troubleshooting context
4. **Regular Updates**: n8n updates frequently, refresh documentation monthly

## 🤝 Contributing

Feel free to improve the scraper or prompt template:
1. Add better content extraction logic
2. Improve categorization
3. Add support for video tutorials or images
4. Create specialized prompts for specific use cases

---

**Note**: Always respect the website's robots.txt and terms of service when scraping. This tool is for personal use to improve your n8n workflow development experience.
