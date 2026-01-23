# GitHub Actions Deployment Flow

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT PROCESS                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: PREPARE CODE
┌──────────────────┐
│  Your Computer   │
│                  │
│  EventScraper/   │
│  ├── spider      │
│  ├── converter   │
│  └── workflow    │
└────────┬─────────┘
         │ git push
         ▼
┌──────────────────┐
│     GitHub       │
│   Repository     │
└────────┬─────────┘
         │
         │
Step 2: CONFIGURE SECRETS
         │
         ▼
┌──────────────────┐
│  GitHub Secrets  │
│                  │
│  AWS_ACCESS_KEY  │
│  AWS_SECRET_KEY  │
│  AWS_REGION      │
│  S3_BUCKET       │
└────────┬─────────┘
         │
         │
Step 3: TRIGGER WORKFLOW
         │
         ▼
┌──────────────────────────────────────────┐
│         GitHub Actions Runner            │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 1. Setup Ubuntu VM                 │ │
│  │ 2. Install Python 3.11             │ │
│  │ 3. Install Chrome                  │ │
│  │ 4. Install dependencies            │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 5. Run Scraper                     │ │
│  │    ├── Load Selenium               │ │
│  │    ├── Scrape 3 URLs               │ │
│  │    ├── Extract events              │ │
│  │    └── Convert to Excel            │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 6. Upload to S3                    │ │
│  │    ├── latest_events.xlsx          │ │
│  │    └── archive/timestamped.xlsx    │ │
│  └────────────────────────────────────┘ │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│            AWS S3 Bucket                 │
│   aws-experience-events-anz              │
│                                          │
│   ├── latest_events.xlsx                │
│   └── archive/                           │
│       ├── aws_events_20260123.xlsx      │
│       ├── aws_events_20260124.xlsx      │
│       └── ...                            │
└──────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Flow

### Phase 1: Setup (One-time)

```
1. Local Development
   └─> Write/test scraper locally
   └─> Commit to git

2. GitHub Repository
   └─> Create repo on GitHub
   └─> Push code

3. AWS IAM Setup
   └─> Create IAM user
   └─> Generate access keys
   └─> Attach S3 permissions

4. GitHub Secrets
   └─> Add AWS credentials
   └─> Add S3 bucket name
```

### Phase 2: Execution (Automatic)

```
Trigger (Daily 9 AM UTC or Manual)
   │
   ▼
GitHub Actions Starts
   │
   ├─> Checkout Code
   │   └─> Clone repository
   │
   ├─> Setup Environment
   │   ├─> Install Python 3.11
   │   ├─> Install Chrome browser
   │   └─> Install pip packages
   │
   ├─> Run Scraper
   │   ├─> Initialize Selenium
   │   ├─> Visit aws-experience.com
   │   │   ├─> Virtual events
   │   │   ├─> AU events
   │   │   └─> NZ events
   │   ├─> Extract event data
   │   └─> Convert to Excel
   │
   ├─> Upload to S3
   │   ├─> Authenticate with AWS
   │   ├─> Upload latest_events.xlsx
   │   └─> Archive timestamped copy
   │
   └─> Complete
       ├─> Save artifact (optional)
       └─> Send notification (if failed)
```

---

## Timeline Example

```
Day 1 - Setup
09:00 - Create GitHub repo
09:15 - Create IAM user
09:20 - Add GitHub secrets
09:25 - Push code
09:30 - Manual test run
09:40 - ✓ Success! Excel in S3

Day 2 - Automatic
09:00 UTC - Workflow triggers automatically
09:08 UTC - ✓ Complete, new Excel in S3

Day 3 - Automatic
09:00 UTC - Workflow triggers automatically
09:07 UTC - ✓ Complete, new Excel in S3

...continues daily...
```

---

## Data Flow

```
aws-experience.com
       │
       │ (Selenium scrapes)
       ▼
┌─────────────────┐
│  Raw HTML Data  │
└────────┬────────┘
         │
         │ (Scrapy parses)
         ▼
┌─────────────────┐
│   JSON Data     │
│   {             │
│     event_name  │
│     date        │
│     time        │
│     location    │
│     url         │
│   }             │
└────────┬────────┘
         │
         │ (excel_convert.py)
         ▼
┌─────────────────┐
│  Excel File     │
│  .xlsx          │
└────────┬────────┘
         │
         │ (AWS CLI)
         ▼
┌─────────────────┐
│   S3 Bucket     │
│   latest_events │
└─────────────────┘
```

---

## Monitoring Dashboard

```
GitHub Actions Tab
├── Workflow Runs
│   ├── ✓ Jan 23, 2026 - 9:00 AM (Success)
│   ├── ✓ Jan 22, 2026 - 9:00 AM (Success)
│   └── ✗ Jan 21, 2026 - 9:00 AM (Failed)
│
├── Current Run (Live)
│   ├── Setup (✓ Complete)
│   ├── Install (✓ Complete)
│   ├── Scrape (⏳ Running...)
│   └── Upload (⏸ Waiting)
│
└── Artifacts
    └── scraped-events.zip (7 days retention)
```

---

## Cost Breakdown

```
GitHub Actions (Free Tier)
├── 2,000 minutes/month
├── This scraper: ~10 min/run
└── Capacity: 200 runs/month
    └── Daily runs: 30/month
        └── Usage: 300 minutes/month
            └── Remaining: 1,700 minutes ✓

AWS S3
├── Storage: $0.023/GB/month
│   └── Excel files: ~1 MB each
│       └── 30 files: ~30 MB
│           └── Cost: < $0.01/month
│
└── Requests: $0.005/1,000 PUT
    └── 60 uploads/month (2 per run)
        └── Cost: < $0.01/month

Total: FREE (within free tiers)
```

---

## Troubleshooting Decision Tree

```
Workflow Failed?
    │
    ├─> Setup Failed?
    │   ├─> Python install issue
    │   │   └─> Check Python version in workflow
    │   └─> Chrome install issue
    │       └─> Check browser-actions/setup-chrome
    │
    ├─> Scraper Failed?
    │   ├─> No events found
    │   │   ├─> Website structure changed
    │   │   │   └─> Update selectors in events.py
    │   │   └─> Network timeout
    │   │       └─> Increase wait times
    │   └─> Selenium error
    │       └─> Check Chrome/driver compatibility
    │
    └─> Upload Failed?
        ├─> AWS credentials invalid
        │   └─> Verify GitHub secrets
        ├─> S3 permission denied
        │   └─> Check IAM policy
        └─> Bucket not found
            └─> Verify bucket name in secrets
```

---

## Success Indicators

✓ **Workflow completes** - Green checkmark in Actions tab
✓ **Excel file in S3** - `aws s3 ls` shows latest_events.xlsx
✓ **Data is current** - File timestamp is recent
✓ **Events found** - Excel contains rows of data
✓ **No errors in logs** - All steps show success

---

## Next Actions After Deployment

```
Week 1: Monitor
├── Check daily runs
├── Verify data quality
└── Fix any issues

Week 2: Optimize
├── Adjust schedule if needed
├── Add error notifications
└── Archive old files

Month 1: Maintain
├── Update selectors if website changes
├── Review S3 storage costs
└── Document any changes
```
