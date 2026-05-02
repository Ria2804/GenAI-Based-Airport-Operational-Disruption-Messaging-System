def get_severity_label(severity: int) -> str:
    if severity is None:
        return "Unknown"
    s = int(severity)
    if s <= 3:
        return "Low"
    elif s <= 6:
        return "Medium"
    elif s <= 8:
        return "High"
    else:
        return "Critical"