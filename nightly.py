import urllib.request, json, datetime, os

TURSO_URL   = os.environ["TURSO_URL"]
TURSO_TOKEN = os.environ["TURSO_TOKEN"]

def query(sql, args=[]):
    payload = {"requests":[
        {"type":"execute","stmt":{"sql":sql,"args":[
            {"type":"null"} if v is None else {"type":"text","value":str(v)} for v in args
        ]}},{"type":"close"}
    ]}
    req = urllib.request.Request(
        f"{TURSO_URL}/v2/pipeline", data=json.dumps(payload).encode(),
        headers={"Authorization":f"Bearer {TURSO_TOKEN}","Content-Type":"application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    if data["results"][0].get("type")=="error":
        raise Exception(data["results"][0]["error"]["message"])
    return data["results"][0].get("response",{}).get("result")

def add(org, category, title, notes, due_date, assigned_to):
    r = query("SELECT COUNT(*) FROM command_center_items WHERE org=? AND title=?", [org, title])
    cnt = int(r["rows"][0][0]["value"])
    if cnt == 0:
        query("INSERT INTO command_center_items (org,category,title,notes,due_date,assigned_to,completed) VALUES (?,?,?,?,?,?,0)",
              [org, category, title, notes, due_date, assigned_to])
        print(f"  ADDED: {title}")
    else:
        print(f"  exists: {title}")

def patch_done(key):
    r = query(f"SELECT value FROM cc_meta WHERE key='{key}'")
    return bool(r and r.get("rows"))

def mark_patch(key):
    query(f"INSERT OR REPLACE INTO cc_meta (key,value) VALUES ('{key}','done')")

today = datetime.date.today()
month = today.month
day   = today.day
year  = today.year

print(f"Running nightly check: {today}")

# Trimester closeout reminders — 21 days before
closeouts = [(8,25,"2026-08-25",1), (12,25,"2026-12-25",2), (5,1,"2027-05-01",3)]
for cm, cd, due, tri in closeouts:
    closeout = datetime.date(int(due[:4]), cm, cd)
    remind_date = closeout - datetime.timedelta(days=21)
    if today == remind_date:
        add("bpwt","President",f"Submit SUCCESS Tri {tri} report — due {due}",
            "Collect all LPM trimester reports, compile SUCCESS report, and submit to state by closeout date.",
            due,"Jen")
        add("bpwt","Programming VP",f"Submit Programming Trimester Report Tri {tri} — due {due}",
            "Collect activity info from all LPMs. Submit to State EVP.\nEmailMe: https://www.emailmeform.com/builder/form/Ixbdc9860vE70",
            due,"Brandy")

# Friendship Day reminder July 1
if month == 7 and day == 1:
    aug1 = datetime.date(year, 8, 1)
    days_until_sun = (6 - aug1.weekday()) % 7
    friendship_day = aug1 + datetime.timedelta(days=days_until_sun)
    add("bpwt","Member/Self",f"Friendship Day event — {friendship_day.strftime('%b %d')}",
        f"Hold or attend a chapter social event for USWT Friendship Day ({friendship_day}).\nElectronic form: https://www.emailmeform.com/builder/form/eV878zf0S3Lkf41aFM",
        str(friendship_day),"Jen")

# Tri 2 kickoff Sep 1
if month == 9 and day == 1:
    key = "nightly_tri2_kickoff"
    if not patch_done(key):
        add("bpwt","Membership VP","Submit New Member Adds by Oct 1 — Tri 2","Monthly NMA deadline.","2026-10-01","Maude")
        add("bpwt","Membership VP","Submit New Member Adds by Nov 1 — Tri 2","Monthly NMA deadline.","2026-11-01","Maude")
        add("bpwt","Membership VP","Submit New Member Adds by Dec 1 — Tri 2","Monthly NMA deadline.","2026-12-01","Maude")
        add("bpwt","Membership VP","Contact Tri 2 members up for renewal","Send Tri 2 renewals. Personal ask is a must.","2026-10-15","Maude")
        add("bpwt","Treasurer","Submit Tri 2 early bird renewal dues — postmarked Oct 15","Trimester Billing Form + check to Chapter Service Center.","2026-10-15","Lorissa")
        add("bpwt","President","Make donation to MNWT Foundation — Tri 2","Required for SUCCESS (F6).","2026-12-25","Jen")
        add("bpwt","State Delegate","Submit trimester report — Tri 2 due Dec 25","Coordinate with Jen on timing.","2026-12-25","")
        mark_patch(key)

# Tri 3 kickoff Jan 1
if month == 1 and day == 1:
    key = "nightly_tri3_kickoff"
    if not patch_done(key):
        add("bpwt","Membership VP","Submit New Member Adds by Feb 1 — Tri 3","Monthly NMA deadline.","2027-02-01","Maude")
        add("bpwt","Membership VP","Submit New Member Adds by Mar 1 — Tri 3","Monthly NMA deadline.","2027-03-01","Maude")
        add("bpwt","Membership VP","Submit New Member Adds by Apr 1 — Tri 3","Monthly NMA deadline.","2027-04-01","Maude")
        add("bpwt","Membership VP","Submit New Member Adds by May 1 — Tri 3","Monthly NMA deadline.","2027-05-01","Maude")
        add("bpwt","Membership VP","Contact Tri 3 members up for renewal","Send Tri 3 renewals. Personal ask is a must.","2027-01-15","Maude")
        add("bpwt","Treasurer","Submit Tri 3 early bird renewal dues — postmarked Jan 15","Trimester Billing Form + check to Chapter Service Center.","2027-01-15","Lorissa")
        add("bpwt","President","Make donation to MNWT Foundation — Tri 3","Required for SUCCESS (F6).","2027-05-01","Jen")
        add("bpwt","State Delegate","Submit trimester report — Tri 3 due May 1","Coordinate with Jen on timing.","2027-05-01","")
        mark_patch(key)

# WoT Week reminder Sep 7
if month == 9 and day == 7:
    add("bpwt","Member/Self","Women of Today Week — Shout Out With Pride activity",
        "WoT Week is the last full week of September.\nForm: https://mnwt.org/members/forms_categories.php?bofID=16",
        f"{year}-09-28","Jen")

# Convention planning reminder Nov 1
if month == 11 and day == 1:
    key = "nightly_convention_planning_2026"
    if not patch_done(key):
        add("bpwt","Convention","Begin Convention 2027 venue and catering contracts",
            "Work with Tevyan to finalize hotel contract, catering quote, and budget for May 2027.",
            "2026-12-31","Jen")
        add("bpwt","Convention","Build Convention 2027 committee and assign roles",
            "Co-chairs: Jen + Tevyan. Build out: decorations, registration, programming, silent auction, hospitality.",
            None,"Jen")
        mark_patch(key)

print("Nightly check complete.")
