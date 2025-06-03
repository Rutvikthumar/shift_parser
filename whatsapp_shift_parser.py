import re
from dateutil.parser import parse as dateparse

def parse_whatsapp_shifts(chat_text):
    """
    Parses WhatsApp chat text for pharmacist shift details.
    Returns a list of dicts (date, location, time, system, extra info, poster).
    """
    shifts = []
    current_poster = None
    current_lines = []

    timestamp_pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2}(?:-\d{2})?,\s*\d{1,2}:\d{2}:\d{2}.*?] ~\s*([^:]+): (.*)$')
    time_pattern = re.compile(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*[-to]+\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', re.I)
    system_pattern = re.compile(r'(Kroll|Fillware|Healthwatch|Filware|Nexxsys|SDM\d+)', re.I)
    explicit_date_pattern = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December|\bJun|\bJul|\bAug|\bSep|\bOct|\bNov|\bDec)[a-z]*\.?\s*\d{1,2}(?:st|nd|rd|th)?', re.I)

    def flush_block():
        if not current_lines:
            return
        block = "\n".join(current_lines)
        poster = current_poster
        system = None
        for match in system_pattern.finditer(block):
            system = match.group(0)
            break
        location = None
        lines = block.splitlines()
        for l in lines:
            if "location:" in l.lower():
                location = l.split(":", 1)[-1].strip()
                break
        # Try to find simple location if not found above
        if not location:
            for l in lines:
                if l.strip() and not system_pattern.search(l) and len(l.strip().split()) <= 3 and not any(s in l.lower() for s in ["pharmacist", "coverage", "needed", "shift", "available", "rate", "assistant", "slow", "message", "thanks", "please", "dm", "store"]):
                    location = l.strip()
                    break

        date_time_lines = []
        for line in block.splitlines():
            if any(month in line.lower() for month in ["may", "june", "july", "aug", "sept", "oct", "nov", "dec"]) and re.search(r'\d', line):
                date_time_lines.append(line.strip())
            elif time_pattern.search(line):
                date_time_lines.append(line.strip())
        if not date_time_lines:
            date_time_lines = [l for l in block.splitlines() if time_pattern.search(l) or explicit_date_pattern.search(l)]

        for line in date_time_lines:
            date_matches = list(explicit_date_pattern.finditer(line))
            if date_matches:
                for m in date_matches:
                    date_str = m.group(0)
                    try:
                        d = dateparse(date_str, fuzzy=True)
                        time_matches = time_pattern.findall(line[m.end():])
                        if time_matches:
                            for t in time_matches:
                                shifts.append({
                                    "poster": poster,
                                    "date": d.strftime("%Y-%m-%d"),
                                    "start_time": t[0],
                                    "end_time": t[1],
                                    "location": location,
                                    "system": system,
                                    "raw": line
                                })
                        else:
                            shifts.append({
                                "poster": poster,
                                "date": d.strftime("%Y-%m-%d"),
                                "start_time": "",
                                "end_time": "",
                                "location": location,
                                "system": system,
                                "raw": line
                            })
                    except Exception:
                        continue
            else:
                m = re.match(r'(June|July|May|August|September|October|November|December|Jan|Feb|Mar|Apr)[a-z]*\.?\s*(\d{1,2})[a-z]*[.,\s\-]*(.*)', line, re.I)
                if m:
                    month = m.group(1)
                    day = m.group(2)
                    rest = m.group(3)
                    try:
                        d = dateparse(f"{month} {day}", fuzzy=True)
                        time_matches = time_pattern.findall(rest)
                        if time_matches:
                            for t in time_matches:
                                shifts.append({
                                    "poster": poster,
                                    "date": d.strftime("%Y-%m-%d"),
                                    "start_time": t[0],
                                    "end_time": t[1],
                                    "location": location,
                                    "system": system,
                                    "raw": line
                                })
                        else:
                            shifts.append({
                                "poster": poster,
                                "date": d.strftime("%Y-%m-%d"),
                                "start_time": "",
                                "end_time": "",
                                "location": location,
                                "system": system,
                                "raw": line
                            })
                    except Exception:
                        continue
                else:
                    time_matches = time_pattern.findall(line)
                    if time_matches:
                        for t in time_matches:
                            date_str = None
                            for prev_line in reversed(block.splitlines()):
                                m2 = re.match(r'(June|July|May|August|September|October|November|December|Jan|Feb|Mar|Apr)[a-z]*\.?\s*(\d{1,2})[a-z]*', prev_line, re.I)
                                if m2:
                                    month = m2.group(1)
                                    day = m2.group(2)
                                    try:
                                        d = dateparse(f"{month} {day}", fuzzy=True)
                                        date_str = d.strftime("%Y-%m-%d")
                                        break
                                    except Exception:
                                        continue
                            shifts.append({
                                "poster": poster,
                                "date": date_str or "",
                                "start_time": t[0],
                                "end_time": t[1],
                                "location": location,
                                "system": system,
                                "raw": line
                            })

    for line in chat_text.splitlines():
        m = timestamp_pattern.match(line)
        if m:
            flush_block()
            current_poster = m.group(1).strip()
            current_lines = [m.group(2).strip()]
        else:
            if current_lines is not None:
                current_lines.append(line.strip())
    flush_block()
    return shifts