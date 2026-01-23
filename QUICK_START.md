# Quick Start Guide - GitHub Actions Deployment

## TL;DR - 5 Steps to Deploy

### 1. Push to GitHub
```bash
cd EventScraper
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

### 2. Create AWS IAM User
- Go to AWS IAM Console
- Create user: `github-actions-scraper`
- Attach policy: `AmazonS3FullAccess` (or custom S3 policy)
- Save Access Key ID and Secret Access Key

### 3. Add GitHub Secrets
Go to: **GitHub Repo → Settings → Secrets → Actions → New secret**

Add these 4 secrets:
- `AWS_ACCESS_KEY_ID` = your access key
- `AWS_SECRET_ACCESS_KEY` = your secret key
- `AWS_REGION` = `us-east-1`
- `S3_BUCKET` = `aws-experience-events-anz`

### 4. Test Workflow
- Go to **Actions** tab in GitHub
- Click **Scrape AWS Events**
- Click **Run workflow** → **Run workflow**
- Wait ~5-10 minutes

### 5. Verify
```bash
aws s3 ls s3://aws-experience-events-anz/
```

You should see `latest_aws_experience_events_ANZ.xlsx`

---

## What Happens Automatically

1. **Daily at 4 AM NZDT (3 PM UTC)**: Workflow runs automatically
2. **Scrapes events**: From virtual, AU, and NZ locations
3. **Filters events**: Only NZ, Australia, and Online events
4. **Converts times**: To NZ timezone (NZDT/NZST)
5. **Sorts by date**: Earliest to latest
6. **Converts to Excel**: Creates timestamped file
7. **Uploads to S3**: 
   - `latest_aws_experience_events_ANZ.xlsx` (always current)
   - `archive/aws_events_TIMESTAMP.xlsx` (historical)

---

## Monitoring

- **View runs**: GitHub → Actions tab
- **Check logs**: Click on any run → Click "scrape" job
- **Download files**: Scroll to Artifacts section in completed run
- **Email alerts**: GitHub sends emails on failures

---

## Troubleshooting

### No events found?
- Check logs in GitHub Actions
- Website structure may have changed
- Test locally: `python run_scraper.py`

### S3 upload fails?
- Verify GitHub secrets are correct
- Check IAM user has S3 permissions
- Verify bucket name

### Workflow doesn't run?
- Schedules can be delayed 15 minutes
- Check Actions tab for disabled workflows
- Try manual trigger first

---

## Cost

- **GitHub Actions**: FREE (2,000 min/month)
- **AWS S3**: < $0.10/month
- **Total**: Essentially FREE

---

## Full Documentation

See `GITHUB_ACTIONS_GUIDE.md` for complete step-by-step instructions.
