import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from fuzzywuzzy import fuzz
import yfinance as yf
from ticker_map import ticker_map

def fuzzy_map_sponsor(sponsor, ticker_map):
    if not sponsor:
        return None
    for key, ticker in ticker_map.items():
        if fuzz.ratio(sponsor.lower(), key.lower()) > 90:  # Tighter threshold
            try:
                yf.Ticker(ticker).info  # Validate ticker
                return ticker
            except:
                continue
    return None

def get_market_cap(ticker):
    try:
        info = yf.Ticker(ticker).info
        mcap = info.get('marketCap', 0)
        return mcap if 0 < mcap < 500000000 else None  # Small/micro only
    except:
        return None

def estimate_completion_date(start_date, phase):
    try:
        start = pd.to_datetime(start_date)
        months = 18 if 'PHASE2' in phase else 24  # Phase 2: 18m, Phase 3: 24m
        return start + timedelta(days=months * 30)
    except:
        return None

def fetch_clinical_trials():
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    fields = (
        "protocolSection.identificationModule.nctId,"
        "protocolSection.identificationModule.briefTitle,"
        "protocolSection.sponsorCollaboratorsModule.leadSponsor.name,"
        "protocolSection.statusModule.overallStatus,"
        "protocolSection.statusModule.primaryCompletionDateStruct.date,"
        "protocolSection.statusModule.startDateStruct.date,"
        "protocolSection.designModule.phases,"
        "protocolSection.designModule.enrollmentInfo.count,"
        "protocolSection.designModule.enrollmentInfo.type,"
        "protocolSection.conditionsModule.conditions,"
        "protocolSection.armsInterventionsModule.interventions.name"
    )
    
    end_date = datetime.now() + timedelta(days=30)
    date_filter = end_date.strftime('%Y-%m-%d')
    
    query = (
        f'AREA[StudyType]"Interventional" AND '
        f'(AREA[Phase]"Phase 2" OR AREA[Phase]"Phase 3") AND '
        f'AREA[PrimaryCompletionDate]RANGE[{datetime.now().strftime("%Y-%m-%d")},{date_filter}]'
    )
    
    params = {
        'query.term': query,
        'fields': fields,
        'pageSize': 1000,
        'format': 'json'
    }
    
    print("Fetching trials...")
    all_studies = []
    page_token = None
    retries = 3
    
    while True:
        if page_token:
            params['pageToken'] = page_token
        
        for attempt in range(retries):
            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                studies = data.get('studies', [])
                all_studies.extend(studies)
                
                page_token = data.get('nextPageToken')
                if not page_token:
                    break
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    print("Max retries reached.")
                    return pd.DataFrame()
        else:
            continue
        break
    
    if not all_studies:
        print("No studies.")
        return pd.DataFrame()
    
    print(f"Retrieved {len(all_studies)} studies.")
    
    data = []
    for study in all_studies:
        protocol = study.get('protocolSection', {})
        id_module = protocol.get('identificationModule', {})
        sponsor_module = protocol.get('sponsorCollaboratorsModule', {})
        status_module = protocol.get('statusModule', {})
        design_module = protocol.get('designModule', {})
        conditions_module = protocol.get('conditionsModule', {})
        interventions_module = protocol.get('armsInterventionsModule', {})
        
        row = {
            'NCT_ID': id_module.get('nctId'),
            'Title': id_module.get('briefTitle'),
            'Sponsor': sponsor_module.get('leadSponsor', {}).get('name'),
            'Status': status_module.get('overallStatus'),
            'Phase': ', '.join(design_module.get('phases', [])),
            'Primary_Completion_Date': status_module.get('primaryCompletionDateStruct', {}).get('date'),
            'Estimated_Enrollment': design_module.get('enrollmentInfo', {}).get('count'),
            'Enrollment_Type': design_module.get('enrollmentInfo', {}).get('type'),
            'Conditions': ', '.join(conditions_module.get('conditions', [])),
            'Interventions': ', '.join([i.get('name', '') for i in interventions_module.get('interventions', [])]),
            'Start_Date': status_module.get('startDateStruct', {}).get('date')
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    df['Primary_Completion_Date'] = pd.to_datetime(df['Primary_Completion_Date'], errors='coerce')
    df['Estimated_Completion'] = df.apply(
        lambda row: estimate_completion_date(row['Start_Date'], row['Phase']) 
        if pd.isna(row['Primary_Completion_Date']) else row['Primary_Completion_Date'], axis=1
    )
    df['Upcoming_Readout'] = df['Estimated_Completion'].apply(
        lambda d: pd.notna(d) and datetime.now() <= d <= end_date
    )
    df['Delay_Flag'] = df['Status'].isin(['SUSPENDED', 'TERMINATED', 'WITHDRAWN'])
    
    df['Ticker'] = df['Sponsor'].apply(lambda s: fuzzy_map_sponsor(s, ticker_map))
    df['Market_Cap'] = df['Ticker'].apply(get_market_cap)
    df = df[df['Market_Cap'].notna()]  # Small/micro only
    
    df['Signal'] = 'Hold'
    df.loc[
        (df['Phase'].str.contains('PHASE2|PHASE3')) & (df['Upcoming_Readout'] == True),
        'Signal'
    ] = 'Buy'
    df.loc[df['Delay_Flag'] == True, 'Signal'] = 'Short'
    
    df = df.sort_values('Market_Cap')
    
    print(f"Found {len(df)} small/micro-cap trials.")
    
    output_file = f"upcoming_fda_proxy_trials_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")
    
    with open('trial_log.txt', 'a') as f:
        f.write(f"{datetime.now()}: Retrieved {len(all_studies)} trials, {len(df)} small/micro-cap.\n")
    
    return df

if __name__ == "__main__":
    df = fetch_clinical_trials()
    print(df.head(10))