from datetime import datetime,timezone,timedelta

def get_cutoff_date(time_frame:str) ->str:
    "Returns the cutoff for filtering"
    day_maps={
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 6 Months": 180,
        "Last 1 Year": 365,
        "All Time": None
    }
    days=day_maps[time_frame]
    if days is None: return ''
    cutoff=datetime.now(timezone.utc)-timedelta(days=days)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")