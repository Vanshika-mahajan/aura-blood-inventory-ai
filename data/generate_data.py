import pandas as pd
import numpy as np
import datetime

# --- Configuration ---
NUM_DONORS = 5000
START_DATE = '2023-01-01'
END_DATE = '2024-12-31'
DATA_DIR = '../data/'
OUTPUT_DIR = '../data/'

# Blood Type Distribution in India (Approximate)
BLOOD_TYPE_DISTRIBUTION = {
    'O+': 0.37, 'B+': 0.32, 'A+': 0.17, 'AB+': 0.07,
    'O-': 0.02, 'B-': 0.02, 'A-': 0.02, 'AB-': 0.01
}

def load_source_data():
    """Loads the source CSV files into pandas DataFrames."""
    print("Loading source data...")
    # Load UCI data and assign column names
    uci_cols = ['Recency', 'Frequency', 'Monetary', 'Time', 'Donated_March_2007']
    transfusion_df = pd.read_csv(f'{DATA_DIR}transfusion.csv', names=uci_cols)
    
    # Load pincodes
    pincodes_df = pd.read_csv('AllIndiaPincodeDirectory.csv')
    # Use only unique, non-null pincodes
    valid_pincodes = pincodes_df['pincode'].dropna().unique()

    # Load holidays
    holidays_df = pd.read_csv(f'{DATA_DIR}holidays.csv')
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    
    print("Source data loaded successfully.")
    return transfusion_df, valid_pincodes, holidays_df

def generate_donors(num_donors, valid_pincodes):
    """Generates a more realistic DataFrame of synthetic donors."""
    print(f"Generating {num_donors} synthetic donors...")
    donor_ids = [f'D{1001 + i}' for i in range(num_donors)]
    
    blood_types = np.random.choice(
        list(BLOOD_TYPE_DISTRIBUTION.keys()),
        size=num_donors, p=list(BLOOD_TYPE_DISTRIBUTION.values())
    )
    
    pincodes = np.random.choice(valid_pincodes, size=num_donors)
    
    donors_df = pd.DataFrame({
        'Donor_ID': donor_ids,
        'Blood_Type': blood_types,
        'Pincode': pincodes
    })
    print("Donor data generation complete.")
    return donors_df

def generate_time_series_logs(donors_df, holidays_df):
    """Generates donation and issuance logs over a date range."""
    print("Generating time-series logs...")
    dates = pd.to_datetime(pd.date_range(start=START_DATE, end=END_DATE))
    holiday_dates = holidays_df['Date'].dt.date
    
    donations_log = []
    issuance_log = []

    for date in dates:
        # --- Simulate Donations ---
        is_holiday = date.date() in holiday_dates
        # Fewer donations on holidays, more on weekends
        if is_holiday:
            daily_donations = np.random.randint(10, 30)
        elif date.weekday() >= 5: # Saturday or Sunday
            daily_donations = np.random.randint(80, 150)
        else: # Weekday
            daily_donations = np.random.randint(50, 100)

        # Select random donors for the day
        donating_donors = donors_df.sample(n=daily_donations)
        for _, donor in donating_donors.iterrows():
            donations_log.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Donor_ID': donor['Donor_ID'],
                'Blood_Type': donor['Blood_Type'],
                'Units_Collected': 1
            })

        # --- Simulate Issuances (Demand) ---
        # Slightly higher demand after holidays
        if is_holiday:
             daily_issuances = np.random.randint(60, 120)
        else:
             daily_issuances = np.random.randint(70, 130)
        
        for _ in range(daily_issuances):
            blood_type_issued = np.random.choice(
                list(BLOOD_TYPE_DISTRIBUTION.keys()),
                p=list(BLOOD_TYPE_DISTRIBUTION.values())
            )
            issuance_log.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Blood_Type': blood_type_issued,
                'Units_Issued': 1
            })

    print("Time-series log generation complete.")
    return pd.DataFrame(donations_log), pd.DataFrame(issuance_log)

if __name__ == "__main__":
    transfusion_df, valid_pincodes, holidays_df = load_source_data()
    
    donors_df = generate_donors(NUM_DONORS, valid_pincodes)
    donations_df, issuance_df = generate_time_series_logs(donors_df, holidays_df)

    # Save the final datasets
    donors_df.to_csv(f'{OUTPUT_DIR}donors.csv', index=False)
    donations_df.to_csv(f'{OUTPUT_DIR}donations_log.csv', index=False)
    issuance_df.to_csv(f'{OUTPUT_DIR}issuance_log.csv', index=False)

    print("\n--- Synthetic Data Generation Complete! ---")
    print(f"Saved donors.csv with {len(donors_df)} records.")
    print(f"Saved donations_log.csv with {len(donations_df)} records.")
    print(f"Saved issuance_log.csv with {len(issuance_df)} records.")
    print(f"\nSample of donations_log.csv:")
    print(donations_df.head())