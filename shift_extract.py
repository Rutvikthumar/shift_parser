import re
from dateutil.parser import parse as dateparse
from datetime import timedelta

def parse_shift_email(email_body):
    """
    Parses TAL shift email body into a list of dicts (location, date, times, system, etc).
    Handles date ranges, lists, times, and various formatting.
    """
    lines = [line.strip() for line in email_body.splitlines() if line.strip() and "area" not in line.lower()]
    shift_data = []
    base_year = dateparse("today").year

    for line in lines:
        m = re.match(r"([A-Za-z\s\(\)\-\']+)\s*–\s*([^()]+)\s*(\([^)]+\))?\s*([A-Za-z0-9 ,]*)$", line)
        if not m:
            continue
        location = m.group(1).strip()
        date_block = m.group(2).strip()
        time_block = m.group(3) or ""
        system_block = m.group(4).strip()

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
                day = int(part)
                date_str = f"{month} {day} {base_year}"
                dates = [dateparse(date_str)]
            elif m2 := re.match(r'([A-Za-z]+)\s*(\d+)-(\d+)', part):
                month = m2.group(1)
                start_day = int(m2.group(2))
                end_day = int(m2.group(3))
                dates = [dateparse(f"{month} {d} {base_year}") for d in range(start_day, end_day+1)]
            elif m3 := re.match(r'([A-Za-z]+)\s*(\d+)\s*–\s*([A-Za-z]+)?\s*(\d+)', part):
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
            times = re.findall(r'(\d{1,2}(?::\d{2})?)[\-\–](\d{1,2}(?::\d{2})?)', time_block)
            if not times:
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