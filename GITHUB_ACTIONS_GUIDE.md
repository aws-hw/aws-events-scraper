# GitHub Actions Deployment Guide

## Overview

This guide will help you deploy the AWS Events Scraper using GitHub Actions. The workflow will:
- Run automatically on a schedule (daily at 4 AM NZDT / 3 PM UTC)
- Scrape events from aws-experience.com (Virtual, AU, NZ locations)
- Filter to only NZ, Australia, and Online events
- Convert times to NZ timezone (NZDT/NZST)
- Sort events by date (earliest to latest)
- Convert results to Excel format
- Upload to your S3 bucket: `aws-experience-events-anz`

**Estimated Setup Time:** 15-20 minutes

---

## Prerequisites

Before starting, make sure you have:
- [ ] A GitHub account
- [ ] Git installed on your computer
- [ ] AWS account access
- [ ] S3 bucket already created: `aws-experience-events-anz`

---

## Step 1: Push Your Code to GitHub

### 1.1 Initialize Git Repository (if not already done)

Open your terminal and navigate to the project root directory:

```bash
cd /path/to/your/project
cd EventScraper
```

Initialize git and make your first commit:

```bash
git init
git add .
git commit -m "Initial commit: AWS Events Scraper with GitHub Actions"
```

### 1.2 Create a New GitHub Repository

1. Open your browser and go to: https://github.com/new
2. Fill in the repository details:
   - **Repository name:** `aws-events-scraper` (or your preferred name)
   - **Description:** "Automated AWS events scraper with GitHub Actions"
   - **Visibility:** Choose Private or Public
   - **⚠️ IMPORTANT:** Do NOT check any boxes (no README, no .gitignore, no license)
3. Click **"Create repository"**

### 1.3 Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Copy your repository URL and run:

```bash
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/aws-events-scraper.git
git branch -M main
git push -u origin main
```

**✅ Checkpoint:** Refresh your GitHub repository page - you should see all your files uploaded.

---

## Step 2: Create AWS IAM User for GitHub Actions

GitHub Actions needs AWS credentials to upload files to S3. Let's create a dedicated IAM user.

### 2.1 Open AWS IAM Console

1. Log in to AWS Console: https://console.aws.amazon.com/
2. Make sure you're in the **us-east-1** region (top-right corner)
3. Search for "IAM" in the search bar and click **IAM**

### 2.2 Create New IAM User

1. In the left sidebar, click **Users**
2. Click **Create user** (orange button)
3. Enter user name: `github-actions-scraper`
4. Click **Next**

### 2.3 Set Permissions

1. Select **Attach policies directly**
2. In the search box, type: `AmazonS3FullAccess`
3. Check the box next to **AmazonS3FullAccess**
4. Click **Next**
5. Click **Create user**

**🔒 More Secure Option (Recommended):**

Instead of `AmazonS3FullAccess`, create a custom policy:

1. Click **Create policy** (opens new tab)
2. Click **JSON** tab
3. Paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::aws-experience-events-anz",
                "arn:aws:s3:::aws-experience-events-anz/*"
            ]
        }
    ]
}
```

4. Click **Next**
5. Policy name: `GitHubActionsS3Upload`
6. Click **Create policy**
7. Go back to the user creation tab and attach this policy instead

### 2.4 Create Access Keys

1. Click on the newly created user: `github-actions-scraper`
2. Click the **Security credentials** tab
3. Scroll down to **Access keys** section
4. Click **Create access key**
5. Select use case: **Application running outside AWS**
6. Click **Next**
7. (Optional) Add description: "GitHub Actions scraper"
8. Click **Create access key**

### 2.5 Save Your Credentials

**⚠️ CRITICAL:** You'll only see these once!

1. You'll see two values:
   - **Access key ID** (starts with `AKIA...`)
   - **Secret access key** (long random string)
2. Click **Download .csv file** OR copy both values to a secure location
3. Click **Done**

**✅ Checkpoint:** You should have both the Access Key ID and Secret Access Key saved.

---

## Step 3: Add AWS Credentials to GitHub Secrets

Now we'll securely store your AWS credentials in GitHub.

### 3.1 Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/aws-events-scraper`
2. Click the **Settings** tab (top menu)
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**

### 3.2 Add Each Secret

You need to add 4 secrets. For each one:

1. Click **New repository secret** (green button)
2. Enter the **Name** and **Secret** value
3. Click **Add secret**

**Add these 4 secrets:**

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ACCESS_KEY_ID` | Your Access Key ID from Step 2.5 | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key from Step 2.5 | `wJalrXUtnFEMI/K7MDENG/bPxRfiCY...` |
| `AWS_REGION` | `us-east-1` | `us-east-1` |
| `S3_BUCKET` | `aws-experience-events-anz` | `aws-experience-events-anz` |

**✅ Checkpoint:** You should see 4 secrets listed on the Actions secrets page.

---

## Step 4: Verify the Workflow File Exists

The workflow file should already be in your repository. Let's verify:

### 4.1 Check Workflow File

1. Go to your GitHub repository
2. Navigate to: `.github/workflows/scrape-events.yml`
3. You should see the workflow configuration file

**If the file is missing**, create it:

1. In your repository, click **Add file** → **Create new file**
2. Name it: `.github/workflows/scrape-events.yml`
3. Copy the content from your local file or from the repository
4. Click **Commit changes**

**✅ Checkpoint:** The workflow file exists at `.github/workflows/scrape-events.yml`

---

## Step 5: Test the Workflow (First Run)

Now let's test everything works!

### 5.1 Trigger the Workflow Manually

1. Go to your GitHub repository
2. Click the **Actions** tab (top menu)
3. In the left sidebar, click **Scrape AWS Events**
4. Click the **Run workflow** button (right side)
5. Keep "Branch: main" selected
6. Click the green **Run workflow** button

### 5.2 Monitor the Workflow

1. You'll see a new workflow run appear (may take 5-10 seconds)
2. Click on the workflow run (it will have a yellow dot 🟡 while running)
3. Click on the **scrape** job to see detailed logs
4. Watch the steps execute:
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install Chrome
   - ✅ Install dependencies
   - ✅ Run scraper (this takes 5-10 minutes)
   - ✅ Upload to S3
   - ✅ Upload artifact

**Expected Duration:** 5-10 minutes

### 5.3 Check for Success

When complete, you should see:
- Green checkmark ✅ next to the workflow run
- All steps showing green checkmarks
- "Upload to S3" step showing successful upload

**If it fails:**
- Click on the failed step (red X)
- Read the error message
- See the Troubleshooting section below

### 5.4 Verify Files in S3

Check that files were uploaded to S3:

**Option A: Using AWS Console**
1. Go to: https://s3.console.aws.amazon.com/s3/buckets/aws-experience-events-anz
2. You should see:
   - `latest_events.xlsx` (in root)
   - `archive/` folder with timestamped file

**Option B: Using AWS CLI**
```bash
aws s3 ls s3://aws-experience-events-anz/
aws s3 ls s3://aws-experience-events-anz/archive/
```

**Option C: Download from GitHub Artifacts**
1. Go back to the workflow run page
2. Scroll to the bottom
3. Under **Artifacts**, click **scraped-events** to download

**✅ Checkpoint:** Excel file successfully uploaded to S3!

---

## Step 6: Configure Automatic Schedule (Optional)

The workflow is already configured to run automatically **daily at 9 AM UTC**.

### 6.1 Current Schedule

The workflow runs:
- ⏰ **Daily at 4 AM NZDT (3 PM UTC)** (automatically)
- 🖱️ **Manual trigger** (via GitHub Actions UI)
- 🔄 **On push to main** (when you push code changes)

### 6.2 Change the Schedule (Optional)

To change when the scraper runs automatically:

1. Open `.github/workflows/scrape-events.yml` in your repository
2. Find the `schedule` section:
```yaml
schedule:
  - cron: '0 15 * * *'  # Daily at 3 PM UTC (4 AM NZDT)
```

3. Replace with your preferred schedule:

**Common Schedules:**
```yaml
# Every 6 hours
- cron: '0 */6 * * *'

# Twice daily (9 AM and 9 PM UTC)
- cron: '0 9,21 * * *'

# Every Monday at midnight UTC
- cron: '0 0 * * 1'

# Every weekday at 8 AM UTC
- cron: '0 8 * * 1-5'

# First day of every month at noon UTC
- cron: '0 12 1 * *'
```

**Cron Format Reference:**
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

**Time Zone Converter:**
- 3 PM UTC = 4 AM NZDT (Auckland, summer)
- 3 PM UTC = 3 AM NZST (Auckland, winter)
- Use: https://www.worldtimebuddy.com/

4. Commit the changes to apply the new schedule

---

## Troubleshooting

### ❌ Workflow fails with "Chrome not found"

**Symptoms:** Error during "Install Chrome" or "Run scraper" step

**Solution:**
1. The `browser-actions/setup-chrome` action should handle this automatically
2. If it still fails, update the workflow to install Chrome manually:

```yaml
- name: Install Chrome manually
  run: |
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
```

---

### ❌ "No events found" or empty Excel file

**Symptoms:** Workflow completes but Excel file is empty or has no events

**Solution:**
1. Check the scraper logs:
   - Go to **Actions** → Click on the workflow run
   - Expand **"Run scraper"** step
   - Look for error messages or warnings
2. The website structure may have changed:
   - Test locally first: `python run_scraper.py`
   - Update selectors in `EventScraper/EventScraper/spiders/events.py`
3. Check if the website is blocking automated access:
   - Look for "403 Forbidden" or "Access Denied" errors
   - May need to add user-agent headers

---

### ❌ S3 upload fails with "Access Denied"

**Symptoms:** Error in "Upload to S3" step: `An error occurred (AccessDenied)`

**Solution:**
1. **Verify IAM permissions:**
   - Go to AWS IAM Console
   - Check user `github-actions-scraper` has S3 permissions
   - Ensure policy includes `s3:PutObject` action

2. **Check GitHub secrets:**
   - Go to repository **Settings** → **Secrets and variables** → **Actions**
   - Verify all 4 secrets are set correctly
   - Secret names are case-sensitive!

3. **Verify bucket name:**
   - Bucket: `aws-experience-events-anz`
   - Region: `us-east-1`
   - Check bucket exists and is in the correct region

4. **Test AWS credentials locally:**
```bash
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
aws s3 ls s3://aws-experience-events-anz/
```

---

### ❌ Workflow doesn't run on schedule

**Symptoms:** Workflow doesn't trigger automatically at scheduled time

**Solution:**
1. **GitHub Actions schedule delays:**
   - Schedules can be delayed up to 15 minutes during high load
   - This is normal GitHub behavior

2. **Inactive repository:**
   - GitHub disables scheduled workflows in inactive repos after 60 days
   - Make a commit or manually run the workflow to reactivate

3. **Check workflow status:**
   - Go to **Actions** tab
   - Look for disabled workflows (gray icon)
   - Click **Enable workflow** if needed

4. **Verify cron syntax:**
   - Use https://crontab.guru/ to validate your cron expression
   - Remember: GitHub uses UTC time

---

### ❌ "Error: No Excel file found"

**Symptoms:** Error in "Upload to S3" step: `No Excel file found`

**Solution:**
1. The scraper didn't generate an Excel file
2. Check the "Run scraper" step logs for errors
3. Verify `excel_convert.py` is working correctly
4. Test locally: `python run_scraper.py`

---

### ❌ Workflow times out or takes too long

**Symptoms:** Workflow runs for 30+ minutes and times out

**Solution:**
1. **Reduce wait times in spider:**
   - Edit `EventScraper/EventScraper/spiders/events.py`
   - Reduce `time.sleep()` values
   - Reduce scroll iterations

2. **Limit URLs:**
   - Temporarily scrape only one location to test
   - Comment out URLs in `start_urls`

3. **Check for infinite loops:**
   - Look for stuck "Load More" button clicks
   - Add timeout limits to Selenium waits

---

### 🔍 General Debugging Steps

1. **Check workflow logs:**
   - Actions → Click workflow run → Click job → Expand steps

2. **Test locally first:**
   ```bash
   cd EventScraper
   python run_scraper.py
   ```

3. **Download artifacts:**
   - Scroll to bottom of workflow run page
   - Download artifacts to inspect Excel file

4. **Enable debug logging:**
   - Add to workflow file:
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
   ```

5. **Check GitHub Actions status:**
   - Visit: https://www.githubstatus.com/
   - Verify no ongoing incidents

---

## Monitoring & Maintenance

### 📊 View Workflow Runs

1. Go to your repository
2. Click **Actions** tab
3. See all workflow runs with status:
   - ✅ Green checkmark = Success
   - ❌ Red X = Failed
   - 🟡 Yellow dot = Running
   - ⚪ Gray circle = Queued

4. Click any run to see:
   - Detailed logs for each step
   - Duration and timestamps
   - Artifacts (Excel files)

### 📧 Email Notifications

GitHub automatically sends emails for:
- ❌ Failed workflow runs
- ✅ First successful run after failures
- 🔔 Workflow dispatch (manual triggers)

**To configure notifications:**
1. Go to GitHub **Settings** (your profile, not repository)
2. Click **Notifications**
3. Under **Actions**, choose your preferences

### 📥 Download Scraped Data

**Option 1: From S3 (Recommended)**
```bash
# Download latest file
aws s3 cp s3://aws-experience-events-anz/latest_events.xlsx ./

# List all archived files
aws s3 ls s3://aws-experience-events-anz/archive/

# Download specific archived file
aws s3 cp s3://aws-experience-events-anz/archive/aws_events_20250123_090000.xlsx ./
```

**Option 2: From GitHub Artifacts**
1. Go to completed workflow run
2. Scroll to **Artifacts** section at the bottom
3. Click **scraped-events** to download ZIP file
4. Artifacts are kept for 7 days

**Option 3: From AWS Console**
1. Go to: https://s3.console.aws.amazon.com/s3/buckets/aws-experience-events-anz
2. Click on `latest_events.xlsx`
3. Click **Download**

### 🔔 Set Up Slack Notifications (Optional)

Get notified in Slack when scraper fails:

1. Create a Slack webhook: https://api.slack.com/messaging/webhooks
2. Add webhook URL as GitHub secret: `SLACK_WEBHOOK`
3. Add this step to your workflow (after "Upload to S3"):

```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "⚠️ AWS Events Scraper failed!",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "❌ *AWS Events Scraper Failed*\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View logs>"
            }
          }
        ]
      }
```

### 📈 Monitor Scraper Health

**Weekly Checklist:**
- [ ] Check last 7 workflow runs are successful
- [ ] Verify Excel files are being uploaded to S3
- [ ] Spot-check data quality (open a recent Excel file)
- [ ] Check S3 storage usage (should be minimal)

**Monthly Checklist:**
- [ ] Review archived files in S3
- [ ] Clean up old archived files if needed (optional)
- [ ] Verify IAM credentials haven't expired
- [ ] Check for website structure changes

---

## 💰 Cost Estimate

### GitHub Actions (Free Tier)
- **2,000 minutes/month** for public repos (FREE)
- **500 MB storage** for artifacts (FREE)
- This scraper uses ~10 minutes per run
- **You can run ~200 times/month** on free tier
- Daily runs = 30/month (well within limits)

### AWS Costs
- **S3 Storage**: ~$0.023/GB/month
  - Excel files are tiny (~100 KB each)
  - 30 files/month = ~3 MB = **$0.0001/month**
- **S3 PUT requests**: $0.005 per 1,000 requests
  - 60 uploads/month (2 per run) = **$0.0003/month**
- **S3 GET requests**: Usually free for occasional downloads

**💵 Total Monthly Cost: < $0.01** (essentially FREE)

---

## ✅ Deployment Checklist

Use this checklist to track your progress:

### Initial Setup
- [ ] **Step 1:** Code pushed to GitHub repository
- [ ] **Step 2:** IAM user `github-actions-scraper` created
- [ ] **Step 2:** Access keys downloaded and saved securely
- [ ] **Step 3:** All 4 GitHub secrets configured:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION`
  - [ ] `S3_BUCKET`
- [ ] **Step 4:** Workflow file exists at `.github/workflows/scrape-events.yml`

### Testing
- [ ] **Step 5:** First manual workflow run completed successfully
- [ ] **Step 5:** Excel file uploaded to S3 bucket
- [ ] **Step 5:** Downloaded and verified Excel file contains events
- [ ] **Step 6:** Schedule configured (if changed from default)

### Monitoring
- [ ] Email notifications enabled for workflow failures
- [ ] Bookmarked GitHub Actions page for monitoring
- [ ] Tested downloading files from S3
- [ ] (Optional) Slack notifications configured

### Maintenance
- [ ] Documented any custom changes made
- [ ] Set calendar reminder to check workflow health monthly
- [ ] Saved IAM credentials in secure password manager

---

## 🎯 Quick Reference

### Common Tasks

**Manually trigger scraper:**
1. Go to repository → Actions → Scrape AWS Events
2. Click "Run workflow" → "Run workflow"

**Download latest data:**
```bash
aws s3 cp s3://aws-experience-events-anz/latest_events.xlsx ./
```

**View recent runs:**
- Go to: `https://github.com/YOUR_USERNAME/aws-events-scraper/actions`

**Check S3 files:**
```bash
aws s3 ls s3://aws-experience-events-anz/
aws s3 ls s3://aws-experience-events-anz/archive/
```

**Test locally:**
```bash
cd EventScraper
python run_scraper.py
```

### Important URLs

- **Your Repository:** `https://github.com/YOUR_USERNAME/aws-events-scraper`
- **GitHub Actions:** `https://github.com/YOUR_USERNAME/aws-events-scraper/actions`
- **S3 Console:** `https://s3.console.aws.amazon.com/s3/buckets/aws-experience-events-anz`
- **IAM Console:** `https://console.aws.amazon.com/iam/`
- **Cron Helper:** `https://crontab.guru/`

---

## 🚀 Advanced Configuration

### Run on Multiple Schedules

Edit `.github/workflows/scrape-events.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'   # 9 AM UTC daily
    - cron: '0 21 * * *'  # 9 PM UTC daily
  workflow_dispatch:
```

### Save to Multiple S3 Buckets

Add after the main S3 upload step:

```yaml
- name: Upload to backup bucket
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    AWS_REGION: ${{ secrets.AWS_REGION }}
  run: |
    EXCEL_FILE=$(ls aws_events_*.xlsx | head -1)
    aws s3 cp "$EXCEL_FILE" s3://backup-bucket-name/events/
```

### Add Email Notifications on Success

Add this step at the end:

```yaml
- name: Send success email
  if: success()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "✅ AWS Events Scraper - Success"
    body: "Scraper completed successfully. Check S3 for latest data."
    to: your-email@example.com
    from: GitHub Actions
```

### Run Only on Weekdays

```yaml
schedule:
  - cron: '0 9 * * 1-5'  # Monday to Friday at 9 AM UTC
```

### Increase Artifact Retention

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: scraped-events
    path: aws_events_*.xlsx
    retention-days: 30  # Keep for 30 days instead of 7
```

---

## 📚 Additional Resources

### Documentation
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **AWS S3 CLI:** https://docs.aws.amazon.com/cli/latest/reference/s3/
- **Scrapy Documentation:** https://docs.scrapy.org/
- **Selenium Documentation:** https://selenium-python.readthedocs.io/

### Tools
- **Cron Expression Generator:** https://crontab.guru/
- **Time Zone Converter:** https://www.worldtimebuddy.com/
- **GitHub Actions Status:** https://www.githubstatus.com/
- **AWS Status:** https://status.aws.amazon.com/

### Support
- **GitHub Actions Community:** https://github.community/c/actions
- **AWS Support:** https://console.aws.amazon.com/support/

---

## 🎉 You're Done!

Your AWS Events Scraper is now deployed and will run automatically every day at 9 AM UTC.

**What happens next:**
1. ⏰ Workflow runs automatically on schedule
2. 🕷️ Scraper collects events from aws-experience.com
3. 📊 Data converted to Excel format
4. ☁️ File uploaded to S3 bucket
5. 📧 You get notified if anything fails

**Need help?** Check the Troubleshooting section or test locally first with `python run_scraper.py`

---

## Summary Checklist

- [ ] Git repository initialized and pushed to GitHub
- [ ] IAM user created with S3 permissions
- [ ] GitHub secrets configured (4 secrets)
- [ ] Workflow file created (`.github/workflows/scrape-events.yml`)
- [ ] Workflow tested manually
- [ ] S3 upload verified
- [ ] Schedule configured (if needed)
- [ ] Monitoring set up

---

## Next Steps After Setup

1. **Monitor first few runs** - Check logs for any issues
2. **Verify data quality** - Download Excel files from S3 and review
3. **Adjust schedule** - Change cron if needed
4. **Set up alerts** - Configure notifications for failures
5. **Document** - Update README with deployment info

---

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review this guide's troubleshooting section
3. Test locally first: `python run_scraper.py`
4. Check AWS CloudWatch for S3 access logs
