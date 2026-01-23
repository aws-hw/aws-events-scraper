# AWS Events Scraper

A Scrapy spider that scrapes AWS events from aws-experience.com and converts them to Excel format.

## Features

- Scrapes events from 3 locations: Virtual, Australia, and New Zealand
- Uses Selenium for JavaScript rendering
- Handles lazy loading and "Load More" buttons
- Extracts: event name, date, time, location, and registration URL
- Converts output to Excel format

## Requirements

- Python 3.8+
- Chrome browser (for Selenium)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Local Testing

Run the scraper locally:

```bash
python run_scraper.py
```

This will:
1. Run the Scrapy spider
2. Scrape events from all 3 locations
3. Convert the data to Excel
4. Save as `aws_events_YYYYMMDD_HHMMSS.xlsx`

### Manual Scrapy Command

```bash
scrapy crawl Event -o events.json
```

## Project Structure

```
EventScraper/
├── EventScraper/
│   ├── spiders/
│   │   └── events.py          # Main spider
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py
├── excel_convert.py           # Excel conversion utility
├── run_scraper.py            # Simple run script
├── requirements.txt
└── scrapy.cfg
```

## GitHub Actions Deployment

Coming soon - will run automatically on a schedule and upload results to S3.

## Cleanup AWS Resources

If you previously deployed to Lambda, run:

```bash
# Refresh AWS credentials first
mwinit

# Then run cleanup
./cleanup-aws.sh
```

This will delete:
- Lambda function: `aws-event-scraper`
- ECR repository: `aws-event-scraper`
- IAM role: `aws-event-scraper-role`

Note: S3 bucket is NOT deleted to preserve any existing data.
