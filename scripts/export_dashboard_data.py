import json, os
from datetime import datetime, timezone
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID=os.getenv("GOOGLE_SHEETS_ID","1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI")
SHEET_NAME=os.getenv("AI_ANALYSIS_SHEET","AI Analysis")
CREDENTIALS_FILE=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE","credentials/service_account.json")
OUTPUT_FILE=Path(os.getenv("DASHBOARD_DATA_FILE","dashboard/data/dashboard-data.json"))

def clean(v): return "" if v is None else str(v).strip()

def normalize_date(v):
    raw=clean(v)
    if not raw:return ""
    if len(raw)>=10 and raw[4]=="-" and raw[7]=="-": return raw[:10]
    for fmt in ("%d %B %Y","%d %b %Y","%d/%m/%Y","%d-%m-%Y","%Y/%m/%d","%B %d, %Y","%b %d, %Y"):
        try:return datetime.strptime(raw,fmt).strftime("%Y-%m-%d")
        except ValueError:pass
    return raw

def main():
    creds=Credentials.from_service_account_file(CREDENTIALS_FILE,scopes=[
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ])
    client=gspread.authorize(creds)
    sheet=client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    vals=sheet.get_all_values()
    if not vals: raise RuntimeError(f'Google Sheet "{SHEET_NAME}" is empty.')
    headers=vals[0];rows=[]
    for raw in vals[1:]:
        r=list(raw)+[""]*(len(headers)-len(raw))
        rec={headers[i]:r[i] for i in range(len(headers))}
        if not clean(rec.get("Author")): continue
        rec["Post Date"]=normalize_date(rec.get("Timestamp") or rec.get("Post Date"))
        for secret_key in ("API Key","GEMINI_API_KEY","Service Account","service_account","Credentials"):
            rec.pop(secret_key,None)
        rows.append(rec)
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"sheet":SHEET_NAME,"count":len(rows),"rows":rows}
    OUTPUT_FILE.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(f"Dashboard data generated: {OUTPUT_FILE}")
    print(f"Valid posts published: {len(rows)}")

if __name__=="__main__": main()
