# Bitcoin ETF Scraper - Deployment Checklist

## Quick Start Guide

This checklist ensures you have everything needed to deploy and run the Bitcoin ETF Flow Data Scraper successfully.

## ✅ Pre-Deployment Requirements

### 1. System Requirements
- [ ] Python 3.8 or higher installed.
- [ ] Stable internet connection with access to Google APIs (`storage.googleapis.com`, `googlechromelabs.github.io`) for automatic browser/driver downloads.
- [ ] 200MB+ available disk space.
- [ ] **Automated Browser & Driver Setup**: The script now handles browser and driver installation automatically.
    - On **Linux** (e.g., Aliyun Function Compute), it downloads a compatible `headless-chromium` and `chromedriver`.
    - On **macOS/Windows**, it downloads a compatible `chromedriver`.
    - No manual installation of Chrome or chromedriver is needed.

### 2. Supabase Setup
- [ ] Supabase account created at [supabase.com](https://supabase.com)
- [ ] New Supabase project created
- [ ] Database table `Bitcoin_ETF_Flow_US$m` created with correct schema
- [ ] Supabase URL and API key obtained

### 3. Environment Setup
- [ ] Project files downloaded to local directory
- [ ] Python virtual environment created (recommended)
- [ ] All dependencies installed from requirements.txt

## 📋 Step-by-Step Deployment

### Step 1: Download and Setup Project
```bash
# Create project directory
mkdir bitcoin-etf-scraper
cd bitcoin-etf-scraper

# Copy all files from ./final/ directory to your project folder
# Ensure you have:
# - serverless.py (main scraper)
# - config.py (configuration file)
# - requirements.txt (dependencies)
# - README.md (documentation)
```

> **注意：首次运行时，脚本会自动检测操作系统并下载所需文件，无需手动干预。**
> - **On Linux**: Downloads both `headless-chromium` (browser) and `chromedriver`.
> - **On macOS/Windows**: Downloads `chromedriver` only.
> 所有文件都会被存放在项目根目录下的 `./bin` 文件夹中。


### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Create Supabase Table
Execute this SQL in your Supabase SQL editor:

```sql
CREATE TABLE "Bitcoin_ETF_Flow_US$m" (
    date DATE PRIMARY KEY,
    total_net_flow DECIMAL DEFAULT 0,
    ibit_flow DECIMAL DEFAULT 0,
    fbtc_flow DECIMAL DEFAULT 0,
    bitb_flow DECIMAL DEFAULT 0,
    arkb_flow DECIMAL DEFAULT 0,
    btco_flow DECIMAL DEFAULT 0,
    ezbc_flow DECIMAL DEFAULT 0,
    brrr_flow DECIMAL DEFAULT 0,
    hodl_flow DECIMAL DEFAULT 0,
    btcw_flow DECIMAL DEFAULT 0,
    gbtc_flow DECIMAL DEFAULT 0,
    btc_flow DECIMAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Step 4: Configure Credentials
Choose one of these methods:

#### Option A: Environment Variables (Recommended)
```bash
export SUPABASE_URL="https://supabase.com/docs/guides/auth/auth-email-templates"
export SUPABASE_KEY="your-supabase-anon-key-here"
```

#### Option B: Direct Configuration
Edit `config.py` and replace placeholder values:
```python
SUPABASE_URL = "https://supabase.com/docs/guides/auth/auth-email-templates"
SUPABASE_KEY = "your-supabase-anon-key-here"
```

### Step 5: Create Data Directory
```bash
mkdir data
```

### Step 6: Test Installation
```bash
python serverless.py
```

## 🔍 Verification Checklist

After running the scraper, verify:

- [ ] No error messages in console output
- [ ] `./data/extracted_data.json` file created with valid JSON data
- [ ] `./data/execution_log.txt` shows successful execution
- [ ] Supabase table contains new records
- [ ] Summary output shows extracted record count > 0

## 📊 Expected Results

### Successful Execution Should Show:
```
BITCOIN ETF DATA EXTRACTION SUMMARY
==================================================
{
  "extraction_date": "2025-06-19T...",
  "total_records": 14,
  "date_range": {
    "earliest": "2025-06-02",
    "latest": "2025-06-19"
  },
  "etf_providers": ["IBIT", "FBTC", "BITB", ...],
  "json_file": "./data/extracted_data.json",
  "supabase_updated": true
}
```

### File Outputs:
- **extracted_data.json**: 14+ records of ETF flow data
- **execution_log.txt**: Detailed processing logs
- **Supabase table**: Updated with latest ETF flow data

## 🚨 Troubleshooting Common Issues

### Issue: "Invalid API key" Error
**Solution**: 
- Verify Supabase URL and key are correct
- Check environment variables are set properly
- Ensure Supabase project is active

### Issue: "Failed to initialize Selenium WebDriver" or "Exec format error"
**Solutions**:
- These errors usually point to a problem with the browser/driver setup, which is now fully automated by the script.
- **Check Network Access**: Ensure the execution environment (especially on cloud platforms like Aliyun FC) has outbound internet access to `storage.googleapis.com` and `googlechromelabs.github.io` to download the browser components.
- **Check Directory Permissions**: Verify the script has write permissions for the `./bin` directory in the project root.
- **Review Logs**: Check the execution logs for any specific errors that occurred during the automated download and unzip process.

### Issue: "403 Forbidden" or No Data Extracted
**Solutions**:
- Check internet connection
- Verify farside.co.uk is accessible
- Wait and retry (may be temporary blocking)
- Check execution logs for specific errors

### Issue: "No ETF table found"
**Solutions**:
- Website structure may have changed
- Check raw HTML output in logs
- May need code updates for new table structure

## 🔄 Production Deployment

### Automated Scheduling
Set up daily execution using cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Example cron entry (daily at 8 PM)
0 20 * * * cd /path/to/scraper && python serverless.py
```

### Monitoring Setup
- Monitor execution logs for errors
- Set up alerts for failed extractions
- Verify data freshness regularly
- Monitor Supabase storage usage

### Security Considerations
- Use environment variables for credentials
- Restrict file permissions on config files
- Regular dependency updates
- Monitor for unusual access patterns

## 📞 Support Resources

### Documentation
- **README.md**: Complete usage documentation
- **config.py**: Configuration options and ETF provider details
- **Execution logs**: Detailed processing information

### Data Source
- **Website**: https://farside.co.uk/btc/
- **Provider**: Farside Investors (London-based)
- **Update Frequency**: Daily (typically evening)

### Technical Support
- Check execution logs first: `./data/execution_log.txt`
- Review extracted data: `./data/extracted_data.json`
- Verify Supabase table structure and permissions
- Test individual components if needed

## ✅ Final Deployment Verification

Before considering deployment complete:

1. [ ] Scraper runs without errors
2. [ ] Data is successfully extracted (14+ records typical)
3. [ ] JSON file contains valid ETF flow data
4. [ ] Supabase table is populated with new records
5. [ ] All ETF providers are represented in data
6. [ ] Execution logs show no critical errors
7. [ ] Scheduled execution configured (if needed)
8. [ ] Monitoring and alerting set up (if needed)

## 🎯 Success Criteria

**Deployment is successful when:**
- Scraper extracts 10+ records of recent ETF flow data
- All 10+ ETF providers show data (may be 0.0 for some)
- Supabase integration works without errors
- JSON backup files are created properly
- System can run reliably on schedule

---

**Last Updated**: June 19, 2025  
**Version**: 1.2 (Fixed Implementation)  
**Tested With**: Python 3.8+, Chrome 120+, Supabase 2.0+