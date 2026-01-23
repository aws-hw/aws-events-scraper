#!/usr/bin/env python3
"""
Test script to verify excel_convert.py changes without running the scraper
"""

import json
from excel_convert import convert_data_to_excel_bytes
from datetime import datetime

# Sample test data matching the structure from the scraper
test_data = [
    {
        'event_name': 'Test Event Malaysia',
        'date': 'Friday 30th January 2026',
        'time': '14:00 - 21:30',
        'location': 'Malaysia - KUL Langkawi & Redang Room, AWS Malaysia, Level 35',
        'registration_url': 'https://example.com/malaysia'
    },
    {
        'event_name': 'Test Event New Zealand',
        'date': 'Tuesday 24th February 2026',
        'time': '12:00 - 16:00 GMT+13',
        'location': 'New Zealand - Level 13, 15 Customs Street West, Auckland Central',
        'registration_url': 'https://example.com/nz'
    },
    {
        'event_name': 'Test Event Australia',
        'date': 'Monday 23rd February 2026',
        'time': '15:30 - 21:00 GMT+11',
        'location': 'Australia - Level 12, 555 Collins St, Melbourne VIC 3000',
        'registration_url': 'https://example.com/au'
    },
    {
        'event_name': 'Test Event Online',
        'date': 'Tuesday 17th February 2026',
        'time': '08:30 - 10:30 GMT+13',
        'location': 'Online',
        'registration_url': 'https://example.com/online'
    },
    {
        'event_name': 'Test Event Early Date',
        'date': 'Tuesday 10th February 2026',
        'time': '08:30 - 10:30 GMT+13',
        'location': 'Online',
        'registration_url': 'https://example.com/early'
    }
]

print("Testing excel_convert.py with sample data...")
print("=" * 60)

# Test the conversion
excel_buffer = convert_data_to_excel_bytes(test_data)

# Save to test file
test_filename = f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with open(test_filename, 'wb') as f:
    f.write(excel_buffer.getvalue())

print(f"✓ Test Excel file created: {test_filename}")
print("\nExpected results:")
print("1. Malaysia event should be FILTERED OUT")
print("2. Events should be sorted by date (earliest first):")
print("   - Tuesday 10th February (earliest)")
print("   - Tuesday 17th February")
print("   - Monday 23rd February")
print("   - Tuesday 24th February (latest)")
print("3. Times should show NZDT or NZST label")
print("\nPlease open the file to verify!")
