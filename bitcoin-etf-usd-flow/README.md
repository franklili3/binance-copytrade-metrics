# Bitcoin ETF Flow Data Scraper

A Python-based web scraper that extracts Bitcoin ETF flow data from [Farside Investors](https://farside.co.uk/btc/) and integrates with Supabase database for automated data collection and storage.

## Project Overview

This scraper monitors daily Bitcoin ETF flow data from Farside Investors, a London-based investment management firm that provides real-time tracking of US spot Bitcoin ETF flows. The data is extracted, validated, and stored in a Supabase database for further analysis.

### Key Features

- **Automated Web Scraping**: Uses Selenium WebDriver to bypass anti-bot protection
- **Real-time Data Extraction**: Captures daily Bitcoin ETF flow data in US$ millions
- **Database Integration**: Seamless integration with Supabase for data storage
- **Data Validation**: Comprehensive validation and error handling
- **Logging & Monitoring**: Detailed execution logs and data summaries
- **JSON Export**: Local data backup in JSON format

## ETF Providers Tracked

The scraper monitors the following Bitcoin ETFs:

| Symbol | ETF Name | Provider | Database Column |
|--------|----------|----------|-----------------|
| IBIT | iShares Bitcoin Trust | BlackRock | ibit_flow |
| FBTC | Fidelity Wise Origin Bitcoin Fund | Fidelity | fbtc_flow |
| BITB | Bitwise Bitcoin ETF | Bitwise | bitb_flow |
| ARKB | ARK 21Shares Bitcoin ETF | ARK Invest | arkb_flow |
| BTCO | Invesco Galaxy Bitcoin ETF | Invesco | btco_flow |
| EZBC | Franklin Bitcoin ETF | Franklin Templeton | ezbc_flow |
| BRRR | Valkyrie Bitcoin Fund | Valkyrie | brrr_flow |
| HODL | VanEck Bitcoin Trust | VanEck | hodl_flow |
| BTCW | WisdomTree Bitcoin Fund | WisdomTree | btcw_flow |
| GBTC | Grayscale Bitcoin Trust | Grayscale | gbtc_flow |

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- Supabase account and project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Chrome WebDriver Setup

The scraper uses Selenium with Chrome WebDriver. Ensure Chrome is installed on your system. The WebDriver will be automatically managed by Selenium 4.x.

### 3. Supabase Configuration

#### Create Supabase Table

Create a table named `Bitcoin_ETF_Flow_US$m` in your Supabase project with the following schema:

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

#### Set Environment Variables

Set your Supabase credentials as environment variables:

```bash
export SUPABASE_URL="https://supabase.com/docs/guides/platform/custom-domains"
export SUPABASE_KEY="your-supabase-anon-key-here"
```

Or modify the `config.py` file directly (not recommended for production).

### 4. Create Required Directories

```bash
mkdir -p data
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python btc_etf_scraper_fixed.py
```

### Expected Output

The scraper will:

1. **Initialize**: Set up Selenium WebDriver and Supabase client
2. **Scrape**: Extract data from farside.co.uk/btc/
3. **Parse**: Process HTML table data into structured format
4. **Validate**: Clean and validate extracted data
5. **Store**: Save to JSON file and update Supabase database
6. **Report**: Generate execution summary

### Output Files

- `./data/extracted_data.json` - Extracted data in JSON format
- `./data/execution_log.txt` - Detailed execution logs

### Sample Data Structure

```json
{
  "date": "2025-06-18",
  "created_at": "2025-06-19T13:17:24.968194",
  "updated_at": "2025-06-19T13:17:24.968196",
  "ibit_flow": 278.9,
  "fbtc_flow": 104.4,
  "bitb_flow": 11.3,
  "arkb_flow": 0.0,
  "btco_flow": 0.0,
  "ezbc_flow": 0.0,
  "brrr_flow": 0.0,
  "hodl_flow": 0.0,
  "btcw_flow": 0.0,
  "gbtc_flow": -16.4,
  "btc_flow": 10.1,
  "total_net_flow": 0.0
}
```

## Configuration

The `config.py` file contains all configuration settings:

- **Database Settings**: Supabase connection and table configuration
- **Scraping Settings**: Target URL, user agents, retry logic
- **Selenium Settings**: WebDriver options and timeouts
- **ETF Providers**: Complete mapping of ETF symbols to database columns
- **Validation Rules**: Data validation and cleaning parameters

## Troubleshooting

### Common Issues

#### 1. 403 Forbidden Errors

**Problem**: Website blocks programmatic access
**Solution**: The scraper uses Selenium with anti-detection measures:
- Headless Chrome with realistic user agent
- Random delays between requests
- Disabled automation indicators

#### 2. Selenium WebDriver Issues

**Problem**: WebDriver initialization fails
**Solutions**:
- Ensure Chrome browser is installed
- Update Chrome to latest version
- Check system PATH for Chrome executable
- Install/update ChromeDriver if needed

#### 3. Supabase Connection Errors

**Problem**: "Invalid API key" or connection failures
**Solutions**:
- Verify SUPABASE_URL and SUPABASE_KEY environment variables
- Check Supabase project settings and API keys
- Ensure table `Bitcoin_ETF_Flow_US$m` exists
- Verify network connectivity to Supabase

#### 4. Data Parsing Issues

**Problem**: No data extracted or parsing errors
**Solutions**:
- Check if website structure has changed
- Review execution logs for specific errors
- Verify table selectors in HTML content
- Test with different date ranges

### Debug Mode

For detailed debugging, check the execution logs:

```bash
tail -f ./data/execution_log.txt
```

### Manual Testing

Test individual components:

```python
from btc_etf_scraper_fixed import BitcoinETFScraper

scraper = BitcoinETFScraper()
html_content = scraper.scrape_data()
data = scraper.parse_html_data(html_content)
print(f"Extracted {len(data)} records")
```

## Data Quality & Validation

### Validation Rules

- **Date Format**: Supports multiple date formats (DD MMM YYYY, YYYY-MM-DD, etc.)
- **Numerical Values**: Handles positive/negative flows, parentheses notation
- **Missing Data**: Defaults to 0.0 for missing ETF flows
- **Range Validation**: Checks for reasonable flow values (-10,000 to +10,000 US$M)

### Data Integrity

- **Duplicate Prevention**: Uses date as primary key with upsert operations
- **Timestamp Tracking**: Records creation and update timestamps
- **Backup Storage**: Local JSON backup for all extracted data

## Deployment Considerations

### Production Setup

1. **Environment Variables**: Use secure environment variable management
2. **Scheduling**: Set up cron jobs or task schedulers for regular execution
3. **Monitoring**: Implement alerting for failed extractions
4. **Error Handling**: Configure retry logic and fallback mechanisms
5. **Resource Management**: Monitor memory and CPU usage for Selenium

### Recommended Schedule

- **Daily Execution**: Run once daily in the evening (after market close)
- **Weekend Handling**: ETF data typically not updated on weekends
- **Holiday Awareness**: Consider market holidays in scheduling

## Performance Notes

- **Execution Time**: Typically 15-30 seconds per run
- **Memory Usage**: ~100-200MB during Selenium execution
- **Network Requirements**: Stable internet connection required
- **Rate Limiting**: Built-in delays to respect website resources

## Legal & Ethical Considerations

- **Data Usage**: Respect Farside Investors' terms of service
- **Rate Limiting**: Implemented delays to avoid overwhelming the server
- **Attribution**: Data sourced from Farside Investors (farside.co.uk)
- **Commercial Use**: Review licensing requirements for commercial applications

## Support & Maintenance

### Regular Maintenance

- **Website Changes**: Monitor for HTML structure changes
- **Dependency Updates**: Keep Python packages updated
- **Chrome Updates**: Ensure Chrome browser compatibility
- **Data Validation**: Regularly verify data accuracy

### Version History

- **v1.0**: Initial implementation with basic scraping
- **v1.1**: Added Selenium support for 403 bypass
- **v1.2**: Enhanced error handling and validation (current)

## Contributing

When contributing to this project:

1. Test thoroughly with real data
2. Maintain compatibility with existing database schema
3. Follow existing code style and documentation standards
4. Update this README for any significant changes

---

**Data Source**: [Farside Investors](https://farside.co.uk/btc/)  
**Last Updated**: June 19, 2025  
**Python Version**: 3.8+  
**License**: Review terms of use for data source