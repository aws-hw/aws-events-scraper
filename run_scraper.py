#!/usr/bin/env python3
"""
Simple script to run the scraper and convert output to Excel
"""

import os
import subprocess
import sys
from datetime import datetime
from excel_convert import convert_data_to_excel_bytes
import json

def main():
    print("Starting AWS Events Scraper...")
    print("=" * 50)
    
    # Run the spider
    output_file = "events_output.json"
    
    print(f"Running Scrapy spider...")
    result = subprocess.run(
        ["scrapy", "crawl", "Event", "-o", output_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error running spider:")
        print(result.stderr)
        sys.exit(1)
    
    print(f"✓ Spider completed")
    
    # Check if output file exists and has data
    if not os.path.exists(output_file):
        print("No output file generated")
        sys.exit(1)
    
    # Load the scraped data
    with open(output_file, 'r') as f:
        events = json.load(f)
    
    print(f"✓ Found {len(events)} events")
    
    if len(events) == 0:
        print("No events found to convert")
        sys.exit(0)
    
    # Convert to Excel
    print("Converting to Excel...")
    excel_buffer = convert_data_to_excel_bytes(events)
    
    # Save Excel file
    excel_filename = f"aws_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    with open(excel_filename, 'wb') as f:
        f.write(excel_buffer.getvalue())
    
    print(f"✓ Excel file saved: {excel_filename}")
    print("=" * 50)
    print("Done!")
    
    # Clean up JSON file
    os.remove(output_file)

if __name__ == "__main__":
    main()
