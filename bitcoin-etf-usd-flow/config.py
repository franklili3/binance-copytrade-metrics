"""
Configuration file for Bitcoin ETF Flow Scraper
Contains placeholder credentials and settings for Supabase integration
"""

import os
from typing import Dict, Any

# Supabase Configuration (Placeholder values)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://supabase.com/docs/guides/getting-started/tutorials/with-react')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-supabase-anon-key-here')

# Database Configuration
DATABASE_CONFIG = {
    'table_name': 'Bitcoin_ETF_Flow_US$m',
    'primary_key': 'date',
    'batch_size': 100,
    'timeout': 30
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'target_url': 'https://farside.co.uk/bitcoin-etf-flow-all-data/',#https://farside.co.uk/btc/
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'timeout': 30,
    'retry_attempts': 3,
    'retry_delay': 5,
    'random_delay_range': (2, 6),
    'binance_copy_trade_url': ['https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=180D','https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=90D','https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=30D','https://www.binance.com/en/copy-trading/lead-details/4458914342020236800?timeRange=7D']
}

# Binance Copy Trade Table Configuration
BINANCE_COPY_TRADE_CONFIG = {
    'table_name': 'binance_spot_copy_trade',
    'upsert_conflict_key': 'lead_trader_id,scraped_date,performance_days', # Include performance_days to uniquely identify different time ranges
    'batch_size': 100,
    'timeout': 30
}

# Selenium WebDriver Configuration
SELENIUM_CONFIG = {
    'headless': True,
    'window_size': '1920,1080',
    'page_load_timeout': 20,
    'implicit_wait': 10,
    'chrome_options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled'
    ]
}

# ETF Provider Configuration (Based on verified data from farside.co.uk)
ETF_PROVIDERS = {
    'IBIT': {
        'name': 'iShares Bitcoin Trust',
        'provider': 'BlackRock',
        'column_name': 'ibit_flow'
    },
    'FBTC': {
        'name': 'Fidelity Wise Origin Bitcoin Fund',
        'provider': 'Fidelity',
        'column_name': 'fbtc_flow'
    },
    'BITB': {
        'name': 'Bitwise Bitcoin ETF',
        'provider': 'Bitwise',
        'column_name': 'bitb_flow'
    },
    'ARKB': {
        'name': 'ARK 21Shares Bitcoin ETF',
        'provider': 'ARK Invest',
        'column_name': 'arkb_flow'
    },
    'BTCO': {
        'name': 'Invesco Galaxy Bitcoin ETF',
        'provider': 'Invesco',
        'column_name': 'btco_flow'
    },
    'EZBC': {
        'name': 'Franklin Bitcoin ETF',
        'provider': 'Franklin Templeton',
        'column_name': 'ezbc_flow'
    },
    'BRRR': {
        'name': 'Valkyrie Bitcoin Fund',
        'provider': 'Valkyrie',
        'column_name': 'brrr_flow'
    },
    'HODL': {
        'name': 'VanEck Bitcoin Trust',
        'provider': 'VanEck',
        'column_name': 'hodl_flow'
    },
    'BTCW': {
        'name': 'WisdomTree Bitcoin Fund',
        'provider': 'WisdomTree',
        'column_name': 'btcw_flow'
    },
    'GBTC': {
        'name': 'Grayscale Bitcoin Trust',
        'provider': 'Grayscale',
        'column_name': 'gbtc_flow'
    }
}

# Data Validation Configuration
VALIDATION_CONFIG = {
    'required_fields': ['date', 'total_net_flow'],
    'date_formats': ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'],
    'max_flow_value': 10000.0,  # Maximum reasonable flow value in US$ millions
    'min_flow_value': -10000.0,  # Minimum reasonable flow value (outflows)
    'default_flow_value': 0.0
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': './data/execution_log.txt',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Output Configuration
OUTPUT_CONFIG = {
    'json_file': './data/extracted_data.json',
    'log_file': './data/execution_log.txt',
    'backup_data': True,
    'timestamp_format': '%Y-%m-%d_%H-%M-%S'
}

# Error Handling Configuration
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,
    'timeout_errors': ['TimeoutException', 'WebDriverException'],
    'http_errors': [403, 429, 500, 502, 503, 504],
    'fallback_enabled': True
}

def get_database_schema() -> Dict[str, str]:
    """
    Returns the expected Supabase table schema
    Based on verified ETF providers and data structure
    """
    schema = {
        'date': 'DATE PRIMARY KEY',
        'total_net_flow': 'DECIMAL',
        'created_at': 'TIMESTAMP DEFAULT NOW()',
        'updated_at': 'TIMESTAMP DEFAULT NOW()'
    }
    
    # Add ETF-specific columns
    for etf_code, etf_info in ETF_PROVIDERS.items():
        schema[etf_info['column_name']] = 'DECIMAL DEFAULT 0'
    
    return schema

def validate_config() -> bool:
    """
    Validates configuration settings
    Returns True if configuration is valid
    """
    try:
        # Check required environment variables
        if SUPABASE_URL == 'https://supabase.com/docs/guides/getting-started/tutorials/with-react':
            print("WARNING: Using placeholder Supabase URL. Please set SUPABASE_URL environment variable.")
            
        if SUPABASE_KEY == 'your-supabase-anon-key-here':
            print("WARNING: Using placeholder Supabase key. Please set SUPABASE_KEY environment variable.")
            
        # Validate ETF providers
        if len(ETF_PROVIDERS) == 0:
            raise ValueError("No ETF providers configured")
            
        # Validate required directories exist
        import os
        os.makedirs('./data', exist_ok=True)
        os.makedirs('./final', exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

# Configuration validation on import
if __name__ == "__main__":
    if validate_config():
        print("Configuration validated successfully")
        print(f"Configured ETF providers: {list(ETF_PROVIDERS.keys())}")
        print(f"Database table: {DATABASE_CONFIG['table_name']}")
    else:
        print("Configuration validation failed")