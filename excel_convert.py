from openpyxl import Workbook
from openpyxl.styles import Font
import pandas as pd
import datetime
import pytz
import re
from datetime import timezone, timedelta
from io import BytesIO


def convert_data_to_excel_bytes(data_list):
    """
    Convert scraped event data directly to Excel format in memory.
    Used by GitHub Actions to create Excel file from scraped JSON data.
    
    Args:
        data_list: List of dictionaries with keys: event_name, date, time, location, registration_url
        
    Returns:
        BytesIO object containing the Excel file
    """
    
    # Filter events: only keep New Zealand, Australia, or Online
    filtered_data = []
    for event in data_list:
        location = event.get('location', '').lower()
        if any(keyword in location for keyword in ['new zealand', 'australia', 'online']):
            filtered_data.append(event)
    
    # Convert list of dicts to pandas DataFrame
    df = pd.DataFrame(filtered_data)
    
    # Sort by date (earliest to latest)
    # Parse dates for sorting
    def parse_date_for_sort(date_str):
        """Parse date string to datetime for sorting"""
        if not date_str:
            return datetime.datetime.max  # Put empty dates at end
        
        try:
            # Try different date formats
            for fmt in ['%A %d%b %B %Y', '%A %dth %B %Y', '%A %dst %B %Y', '%A %dnd %B %Y', '%A %drd %B %Y']:
                try:
                    return datetime.datetime.strptime(date_str, fmt)
                except:
                    continue
            return datetime.datetime.max  # If parsing fails, put at end
        except:
            return datetime.datetime.max
    
    df['_sort_date'] = df['date'].apply(parse_date_for_sort)
    df = df.sort_values('_sort_date')
    df = df.drop('_sort_date', axis=1)  # Remove temporary sort column
    
    # Create a new Excel workbook in memory
    wb = Workbook()
    ws = wb.active
    ws.title = "Events"
    
    # Format column names: capitalize and remove underscores
    formatted_columns = []
    for col in df.columns:
        formatted_col = col.replace('_', ' ').title()
        if col == 'registration_url':
            formatted_col = 'Event Link'
        formatted_columns.append(formatted_col)
    
    # Write headers to first row
    for col_idx, col_name in enumerate(formatted_columns, 1):
        ws.cell(row=1, column=col_idx, value=col_name)
    
    # NZ timezone - automatically handles daylight saving
    nz_tz = pytz.timezone('Pacific/Auckland')
    
    # Write data rows (starting from row 2)
    for row_idx, row in df.iterrows():
        for col_idx, original_col in enumerate(df.columns, 1):
            cell = ws.cell(row=row_idx + 2, column=col_idx)
            value = row[original_col]
            
            # Handle registration_url column - make it a clickable hyperlink
            if original_col == 'registration_url':
                cell.value = "Register Here"
                cell.hyperlink = value
                cell.font = Font(color="0563C1", underline="single")
            
            # Handle time column - convert to 24-hour NZ time with timezone label
            elif original_col == 'time':
                try:
                    time_str = str(value)
                    
                    if 'GMT' in time_str:
                        # Extract the GMT offset (e.g., +13)
                        gmt_match = re.search(r'GMT([+-]\d+)', time_str)
                        if gmt_match:
                            offset_str = gmt_match.group(1)
                            offset_hours = int(offset_str)
                            
                            # Create timezone with this offset
                            event_tz = timezone(timedelta(hours=offset_hours))
                            
                            # Get time part before GMT
                            time_part = time_str.split('GMT')[0].strip()
                            
                            # Get event date from the 'date' column
                            date_str = row.get('date', '')
                            event_date = datetime.date.today()
                            
                            if date_str:
                                # Try different date formats
                                for fmt in ['%A %d%b %B %Y', '%A %dth %B %Y', '%A %dst %B %Y', '%A %dnd %B %Y', '%A %drd %B %Y']:
                                    try:
                                        parsed_date = datetime.datetime.strptime(date_str, fmt)
                                        event_date = parsed_date.date()
                                        break
                                    except:
                                        continue
                            
                            # Parse start and end times
                            if ' - ' in time_part:
                                start_time_str, end_time_str = time_part.split(' - ')
                                start_time_str = start_time_str.strip()
                                end_time_str = end_time_str.strip()
                                
                                # Convert start time to NZ timezone
                                start_time_obj = datetime.datetime.strptime(start_time_str, '%H:%M').time()
                                start_dt = datetime.datetime.combine(event_date, start_time_obj, tzinfo=event_tz)
                                start_nz = start_dt.astimezone(nz_tz)
                                
                                # Convert end time to NZ timezone
                                end_time_obj = datetime.datetime.strptime(end_time_str, '%H:%M').time()
                                end_dt = datetime.datetime.combine(event_date, end_time_obj, tzinfo=event_tz)
                                end_nz = end_dt.astimezone(nz_tz)
                                
                                # Determine if NZDT (daylight saving) or NZST (standard time)
                                # NZDT is UTC+13, NZST is UTC+12
                                tz_name = start_nz.strftime('%Z')  # Gets 'NZDT' or 'NZST'
                                
                                # Format as 24-hour time with timezone label
                                cell.value = f"{start_nz.strftime('%H:%M')} - {end_nz.strftime('%H:%M')} {tz_name}"
                            else:
                                cell.value = value
                        else:
                            cell.value = value
                    else:
                        cell.value = value
                except Exception as e:
                    print(f"Error converting time '{value}': {e}")
                    cell.value = value
            
            else:
                cell.value = value
    
    # Auto-adjust column widths for readability
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    # Save workbook to BytesIO (in-memory file)
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    
    return excel_buffer
