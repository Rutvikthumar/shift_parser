import re
from dateutil.parser import parse as dateparse
from datetime import timedelta

def expand_dates(base_month, base_year, date_str):
    """
    Expands strings like 'May 31, Jun 2, 9, Jul 14, 21, Aug 1, 2, 3'
    into a list of (month, day) tuples.
    """
    results = []
    current_month = base_month
    current_year = base_year
    parts = re.split(r',\s*', date_str)
    for part in parts:
        m = re.match(r'([A-Za-z]+)\s*(\d+)', part)
        if m:
            current_month = m.group(1)
            current_day = int(m.group(2))
            results.append((current_month, current_day, current_year))
        elif re.match(r'\d+', part):
            # No new month, use current
            results.append((current_month, int(part), current_year))
        elif m := re.match(r'([A-Za-z]+)\s*(\d+)-(\d+)', part):
            # Range: e.g., Jul 14-18
            current_month = m.group(1)
            start_day = int(m.group(2))
            end_day = int(m.group(3))
            for d in range(start_day, end_day + 1):
                results.append((current_month, d, current_year))
    return results

def expand_range(start_str, end_str, base_year):
    """
    For ranges like "May 29–30"
    """
    start_dt = dateparse(f"{start_str} {base_year}")
    end_dt = dateparse(f"{end_str} {base_year}")
    days = (end_dt - start_dt).days + 1
    return [(start_dt.strftime("%b"), start_dt.day + i, base_year) for i in range(days)]

def parse_time_block(time_block):
    # Handles (9-5), (10:30-6), (9-5:30), etc.
    # Returns (start, end), both as strings
    times = re.findall(r'(\d{1,2}(?::\d{2})?)\s*-\s*(\d{1,2}(?::\d{2})?)', time_block)
    return times if times else []

def parse_shift_email(email_body):
    # Pattern: Location – Dates (Times) System
    lines = [line.strip() for line in email_body.splitlines() if line.strip() and "area" not in line.lower()]
    shift_data = []
    base_year = dateparse("today").year  # Default to current year

    for line in lines:
        # Split: "Location – Date(s) (time) System"
        m = re.match(r"([A-Za-z\s\(\)]+)\s*–\s*([^()]+)\s*(\([^)]+\))?\s*([A-Za-z0-9 ,]*)$", line)
        if not m:
            continue  # skip lines not matching

        location = m.group(1).strip()
        date_block = m.group(2).strip()
        time_block = m.group(3) or ""
        system_block = m.group(4).strip()

        # Handle date ranges, lists, and single dates
        # e.g., "May 29, 30", "Jul 14, 21, Aug 1, 2, 3", "May 31 , Jun 14, 15, 28, 29"
        date_parts = re.split(r'[,;]', date_block)
        month = None
        for part in date_parts:
            part = part.strip()
            # Month and date: e.g., 'May 29'
            m1 = re.match(r'([A-Za-z]+)\s*(\d+)', part)
            if m1:
                month = m1.group(1)
                day = int(m1.group(2))
                date_str = f"{month} {day} {base_year}"
                dates = [dateparse(date_str)]
            elif re.match(r'\d+', part) and month:
                # Date only, use previous month
                day = int(part)
                date_str = f"{month} {day} {base_year}"
                dates = [dateparse(date_str)]
            elif m2 := re.match(r'([A-Za-z]+)\s*(\d+)-(\d+)', part):
                # Range, e.g., Jul 14-18
                month = m2.group(1)
                start_day = int(m2.group(2))
                end_day = int(m2.group(3))
                dates = [dateparse(f"{month} {d} {base_year}") for d in range(start_day, end_day+1)]
            elif m3 := re.match(r'([A-Za-z]+)\s*(\d+)\s*–\s*([A-Za-z]+)?\s*(\d+)', part):
                # Cross-month range: May 29–Jun 3
                start_month = m3.group(1)
                start_day = int(m3.group(2))
                end_month = m3.group(3) or start_month
                end_day = int(m3.group(4))
                start_dt = dateparse(f"{start_month} {start_day} {base_year}")
                end_dt = dateparse(f"{end_month} {end_day} {base_year}")
                days = (end_dt - start_dt).days + 1
                dates = [start_dt + timedelta(days=i) for i in range(days)]
            else:
                continue

            # Handle multiple time slots per day
            times = parse_time_block(time_block)
            if not times:
                # Try to find times in system block (e.g., Sat (10-3) Sun (10-2))
                alt_times = re.findall(r'(Sat|Sun)?\s*\(([\d:-]+)\)', system_block)
                if alt_times:
                    for weekday, t in alt_times:
                        for d in dates:
                            shift_data.append({
                                "location": location,
                                "date": d.strftime("%Y-%m-%d"),
                                "weekday": weekday if weekday else d.strftime("%a"),
                                "start_time": t.split('-')[0],
                                "end_time": t.split('-')[1] if '-' in t else "",
                                "system": re.sub(r'\(.+\)', '', system_block).strip()
                            })
                    continue

            if times:
                for t in times:
                    for d in dates:
                        shift_data.append({
                            "location": location,
                            "date": d.strftime("%Y-%m-%d"),
                            "weekday": d.strftime("%a"),
                            "start_time": t[0],
                            "end_time": t[1],
                            "system": re.sub(r'\(.+\)', '', system_block).strip()
                        })
            else:
                for d in dates:
                    shift_data.append({
                        "location": location,
                        "date": d.strftime("%Y-%m-%d"),
                        "weekday": d.strftime("%a"),
                        "start_time": "",
                        "end_time": "",
                        "system": system_block,
                    })

    return shift_data

# Example usage:
if __name__ == "__main__":
    email_body = """GTA 

Etobicoke – May 29, 30 (8-8) HW
Toronto – May 29 (9-5) Fillware
Oshawa – May 30 (4-12) HW
Mississauga – May 31 (9-6) Kroll
Courtice – May 31 , Jun 14, 15, 28, 29 (9-3) Kroll
Oshawa – May 31 (9-5) Kroll
Brampton – May 31, Jun 2, 9, Jul 14, 21, Aug 1, 2, 3 (10-5), Sat (10-3), Sun (10-2) Fillware
Scarborough – Jun 1 (10-5) Kroll
Scarborough – Jun 6 (9:30-8) Kroll
Whitby – Jun 7 (9-6), 8 (10-5) Kroll
Oakville – Jun 7, 8 (9-6),11, 12, 13 (1-9), 21, 22, (9-6), 23,27 (1-9), 30 (9-5) Kroll
Oshawa – Jun 7, 14, 21, 28 (9-4) Propel
Oshawa – Jun 7 (9-3, 23Kroll
Toronto – Jun 7, 14,16,17,19,20, 21, 23, 27,28, Jul 3 till 31 close Wednesday , (10:30-6), Sat (1-6) Kroll
Brampton – Jun 21, Jul 12, Aug  23, 30, 31 Sat(10-3) Sun (10-2) Fillware
Toronto- Jun 27  (10-6) Fillware
Caledonia – Jun 27 (8-9) Propel
Scarborough – July 8,10,11,12,(9-6), Sat (10-4) Nexxsys
Pickering – Jul 16,17,18 (9-5), Sat (9-3) Kroll
Brampton – Aug 5, 6, 12, 13 (10-7) Kroll
Vaughan – Aug 29,30 Sep 5 , 11,13 (9-7), Sat (10-6), Sun 11-4)
Toronto – Sep 29,30, Oct 1,2,3 , 6 (10-5) Nexxsys
North York – Oct 29, Nov 5, 12, (10-5) Nexxsys
"""
    shifts = parse_shift_email(email_body)
    for s in shifts:
        print(s)
