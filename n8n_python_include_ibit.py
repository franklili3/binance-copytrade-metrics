import re
from datetime import datetime

# Function to convert date to yyyy-mm-dd format
def convert_date(date_str):
    try:
        # Try to parse the date in the format 'dd MMM yyyy' (e.g., '09 Oct 2025')
        date_obj = datetime.strptime(date_str.strip(), '%d %b %Y')
        # Convert to yyyy-mm-dd format
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        # If parsing fails, return the original string
        return date_str

# Loop over input items and process the data
results = []

# Access the first item's JSON data (assuming all data is in one item)
input_item = _input.first()
input_data = input_item.json

# Extract and clean table headers
table_head = []
if hasattr(input_data, 'table_head') and input_data.table_head:
    # Remove brackets and split by comma, then clean up each header
    table_head = [h.strip() for h in input_data.table_head.strip('[]').split(',') if h.strip()]
else:
    # Fallback to default headers if table_head is not available
    table_head = ["date", "IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC", "BRRR", "HODL", "BTCW", "GBTC", "BTC", "Total"]

# Parse numeric value function
def parse_numeric_value(value_str):
    """Clean and convert string to numeric value"""
    if not value_str:
        return 0
        
    # Convert to string if needed
    value_str = str(value_str)
        
    # Remove extra spaces and parentheses (parentheses indicate negative numbers)
    cleaned = value_str.strip()
    is_negative = False
    
    if cleaned.startswith('(') and cleaned.endswith(')'):
        is_negative = True
        cleaned = cleaned[1:-1]
        
    # Remove non-numeric characters, keep decimal point and minus sign
    cleaned = re.sub(r'[^\d.-]', '', cleaned)
    
    try:
        value = float(cleaned) if cleaned else 0
        return -value if is_negative else value
    except ValueError:
        return 0

# Calculate number of columns (fields) and rows
num_columns = len(table_head)
total_data_points = len(input_data.table_data)
num_rows = (total_data_points + num_columns - 1) // num_columns  # Ceiling division

# Process each row
for row in range(num_rows):
    result = {}
    skip_row = False
    
    # Process each column in the row
    for col, field in enumerate(table_head):
        data_index = row * num_columns + col
        if data_index < total_data_points:
            if field == 'date':
                # Convert date to yyyy-mm-dd format
                date_str = str(input_data.table_data[data_index]).strip()
                result[field] = convert_date(date_str)
                
                # Check if this row should be skipped
                date_lower = date_str.lower()
                if any(x in date_lower for x in ['total', 'average', 'minimum', 'maximum']):
                    skip_row = True
                    break  # Skip processing other fields for this row
            else:
                result[field] = parse_numeric_value(input_data.table_data[data_index])
        else:
            # Fill missing values with appropriate defaults
            result[field] = 0 if field != 'date' else ''
    
    # Add the processed row to results if it's not marked to be skipped
    if not skip_row:
        results.append({
            'json': result
        })

return results