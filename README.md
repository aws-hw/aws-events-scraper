# AWS Events Scraper :space_invader:


A Scrapy spider that scrapes AWS events from aws-experience.com and converts them to Excel format with automatic timezone conversion and filtering.

## Features

- **Automated Scraping**: Runs daily via GitHub Actions
- **Multi-Location Support**: Scrapes Virtual, Australia, and New Zealand events
- **Timezone Conversion**: Automatically converts times to NZ timezone (NZDT/NZST)
- **Excel Output**: Clean, formatted Excel files with clickable registration links
- **S3 Integration**: Automatic upload to AWS S3 bucket
- **Selenium + Scrapy**: Handles JavaScript-heavy pages with lazy loading

## Output Format

The Excel file includes:
- **Event Name**: Full event title
- **Time**: NZ timezone with NZDT/NZST label (e.g., "12:00 - 16:00 NZDT")
- **Location**: Filtered to show only NZ, Australia, or Online events
- **Event Link**: Clickable "Register Here" hyperlinks

## Requirements

- Python 3.11+
- Chrome browser (for Selenium)
- AWS account (for S3 upload)

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
1. Run the Scrapy spider with Selenium
2. Scrape events from all 3 locations
3. Filter to NZ, Australia, and Online events only
4. Convert times to NZ timezone (NZDT/NZST)
5. Save as `aws_events_YYYYMMDD_HHMMSS.xlsx`

### Manual Scrapy Command

```bash
scrapy crawl Event -o events.json
```

## Project Structure

```
EventScraper/
├── .github/
│   └── workflows/
│       └── scrape-events.yml     # GitHub Actions workflow
├── EventScraper/
│   ├── spiders/
│   │   └── events.py             # Main spider (Selenium + Scrapy)
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py               # Scrapy configuration
├── excel_convert.py              # Excel conversion with filtering & sorting
├── run_scraper.py                # Main entry point
├── requirements.txt              # Python dependencies
├── scrapy.cfg                    # Scrapy project config
├── README.md                     # This file
├── GITHUB_ACTIONS_GUIDE.md       # Detailed deployment guide
├── QUICK_START.md                # Quick setup guide
├── PROJECT_STATUS.md             # Current project status
└── DEPLOYMENT_FLOW.md            # Visual deployment flow
```

## GitHub Actions Deployment

The scraper runs automatically via GitHub Actions:

- **Schedule**: Daily at 4 AM NZDT (3 PM UTC)
- **Manual Trigger**: Via GitHub Actions UI
- **On Push**: Runs when code is pushed to main branch

### Quick Setup

1. Push code to GitHub
2. Create AWS IAM user with S3 permissions
3. Add 4 GitHub secrets (AWS credentials, region, bucket)
4. Workflow runs automatically

See `GITHUB_ACTIONS_GUIDE.md` for detailed step-by-step instructions.

## Current Status

✅ **Production Ready**
- Scraper working correctly (retrieves all events from current date on aws-experience)
- GitHub Actions workflow configured and tested
- S3 upload working
- Excel formatting complete with:
  - Location filtering (NZ, Australia, Online only)
  - Timezone conversion (NZDT/NZST labels)
  - Clickable registration hyperlinks

## Recent Updates

- **2026-01-23**: Fixed ChromeDriver compatibility for GitHub Actions
- **2026-01-23**: Added location filtering (removed Malaysia events)
- **2026-01-23**: Implemented date sorting (earliest to latest)
- **2026-01-23**: Added timezone labels (NZDT/NZST) to all times
- **2026-01-23**: Fixed UTC time conversion

## Monitoring

- **GitHub Actions**: View runs at `https://github.com/YOUR_USERNAME/REPO_NAME/actions`
- **S3 Bucket**: `s3://aws-experience-events-anz/`
  - `latest_aws_experience_events_ANZ.xlsx` - Always current
  - `archive/` - Historical files with timestamps
- **Artifacts**: Available for 7 days in GitHub Actions

## Cost

- **GitHub Actions**: FREE (within 2,000 min/month free tier)
- **AWS S3**: < $0.01/month (minimal storage and requests)
- **Total**: Essentially FREE

## Troubleshooting

### No events found locally
- Delete old `events_output.json` file before running
- Check Chrome/ChromeDriver compatibility
- Verify website is accessible

### GitHub Actions fails
- Check workflow logs in Actions tab
- Verify GitHub secrets are configured correctly
- Ensure IAM user has S3 permissions
- See `GITHUB_ACTIONS_GUIDE.md` troubleshooting section

### Wrong timezone or missing events
- Times should show NZDT (daylight saving) or NZST (standard time)
- Only NZ, Australia, and Online events should appear
- Events should be sorted by date (earliest first)

## Documentation

- **GITHUB_ACTIONS_GUIDE.md**: Complete deployment guide with troubleshooting
- **QUICK_START.md**: 5-step quick setup guide
- **PROJECT_STATUS.md**: Current project status and structure
- **DEPLOYMENT_FLOW.md**: Visual deployment flow and architecture

## Support

For issues:
1. Check GitHub Actions logs
2. Review troubleshooting sections in documentation
3. Test locally first: `python run_scraper.py`
4. Verify AWS credentials and S3 permissions
