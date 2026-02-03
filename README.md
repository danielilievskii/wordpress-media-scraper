# WordPress Media Scraper

A Python-based web scraper for extracting articles from multiple WordPress sites using the WordPress REST API - part of the Vezilka project. The scraper supports incremental updates, concurrent fetching, rate limiting, and stores articles in structured JSON format.


## Supported Sites

The scraper currently supports 22 news & media sites:

- kurik.mk
- republika.mk
- centar.mk
- sportmedia.mk
- magazin.mk
- smartportal.mk
- makpress.mk
- irl.mk
- a1on.mk
- plusinfo.mk
- mkd-news.com
- mkinfo.mk
- slobodenpecat.mk
- press24.mk
- nezavisen.mk
- trn.mk
- 4news.mk
- racin.mk
- netpress.com.mk
- makedonija24.mk
- infomax.mk
- puls24.mk


## Features

- **Multi-site scraping**: Scrape articles from multiple WordPress sites in a single run
- **Incremental updates**: Only fetches new articles on subsequent runs
- **Concurrent fetching**: Efficient parallel requests with configurable concurrency limits
- **Rate limiting**: Built-in rate limiting to respect server resources
- **Retry logic**: Automatic retries with exponential backoff for failed requests
- **HTML parsing**: Extracts clean text content from HTML articles

## Project Structure

```
wordpress-media-scraper/
├── config/            
│   ├── logging.py      # Logging configuration
│   ├── scraper_settings.py   # Scraper-specific settings
│   └── store_settings.py     # Storage-specific settings
├── scraper/          
│   ├── fetcher.py      # Data fetching with pagination
│   ├── parser.py       # Data parsing 
│   ├── scraper.py      # Main scraper orchestration
│   ├── http_client.py  # HTTP client with retry/rate limiting
│   └── models.py       # Article data model
├── store/          
│   ├── base_store.py   # Abstract storage interface
│   ├── json_store.py   # JSON-based storage implementation
│   └── factory.py      # Store factory
├── utils/ 
│   ├── rate_limiter.py # Rate limiting implementation
│   └── retry.py        # Retry decorator
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wordpress-media-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The scraper is configured through `config/scraper_settings.py`. You can customize:

- **Site registry**: List of sites to scrape (name, URL pairs)
- **Posts per page**: Number of posts to fetch per API request (default: 100)
- **Concurrency**: Maximum concurrent requests (default: 10)
- **Rate limiting**: Requests per second (default: 5)
- **Retry settings**: Maximum retries and backoff strategy
- **Logging**: Log level, format, and file output

### Environment Variables

You can override settings using a `.env` file:

```env
LOG_LEVEL=INFO
POSTS_PER_PAGE=100
MAX_CONCURRENT_REQUESTS=10
REQUESTS_PER_SECOND=5
```

## Usage

Run the scraper:

```bash
python main.py
```

The scraper will:
1. Load previously seen article IDs from storage
2. Fetch metadata (total pages, categories) for each site
3. Fetch articles (concurrently for first run, sequentially for incremental updates)
4. Parse HTML content and extract structured data
5. Save new articles to JSON files in the `data/` directory

## How It Works

### First Run
- Fetches all pages concurrently for maximum speed
- Stores all articles and their IDs

### Incremental Runs
- Fetches pages sequentially
- Stops early when encountering previously seen articles
- Only processes and stores new articles

### Data Storage

Articles are stored in JSON format:
- Each site has its own directory under `data/`
- Articles are stored in `articles.json`
- Seen IDs are tracked in `seen_ids.json`

### Article Structure

Each article contains:
- `id`: Unique identifier (site_name_post_id)
- `title`: Article title
- `site_url`: Base URL of the source site
- `page_url`: Full URL to the article
- `content`: Plain text content (HTML stripped)
- `published_at`: Publication date
- `categories`: List of category names
- `metadata`: Optional additional metadata

## Logging

Logs are written to the console by default. To enable file logging, set `log_to_file=True` in settings. Logs will be written to `logs/scraper.log`.

## Error Handling

- Failed requests are automatically retried with exponential backoff
- Individual article parsing errors are logged but don't stop the scraping process
- Site-level failures are logged and reported at the end

## Dependencies

- `aiohttp`: Async HTTP client
- `beautifulsoup4`: HTML parsing
- `langdetect`: Language detection
- `pydantic`: Data validation
- `pydantic-settings`: Settings management

