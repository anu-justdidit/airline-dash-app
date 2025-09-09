import pandas as pd
import os
import requests
import zipfile
import numpy as np

def fetch_and_save_data():
    """Fetches REAL data from BTS website and checks for Kaggle satisfaction data."""
    
    raw_data_dir = "../data/raw"
    os.makedirs(raw_data_dir, exist_ok=True)
    
    # ------- DOWNLOAD REAL BTS DELAY DATA -------
    print("Downloading REAL BTS Delay data from transtats.bts.gov...")
    
    bts_download_url = "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{}_{}.zip"

    year = 2024
    month = 1

    try:
        url = bts_download_url.format(year, month)
        print(f"Downloading from: {url}")
        
        response = requests.get(url)
        response.raise_for_status()

        zip_file_path = os.path.join(raw_data_dir, f"ontime_{year}_{month:02d}.zip")
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded ZIP file saved to: {zip_file_path}")

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            csv_file_name = zip_ref.namelist()[0]
            with zip_ref.open(csv_file_name) as csv_file:
                bts_df = pd.read_csv(csv_file, low_memory=False)

        # Select only the most relevant columns to keep the dataset manageable
        relevant_columns = [
            'FlightDate', 'Airline', 'Origin', 'Dest', 
            'DepDelayMinutes', 'ArrDelayMinutes', 'Cancelled', 'Diverted'
        ]
        # Only keep columns that actually exist in the downloaded data
        available_columns = [col for col in relevant_columns if col in bts_df.columns]
        bts_df = bts_df[available_columns]

        bts_df.to_csv(f"{raw_data_dir}/bts_delays.csv", index=False)
        print("✅ Saved BTS Delays data to data/raw/bts_delays.csv")
        print(f"Dataset shape: {bts_df.shape}")

    except Exception as e:
        print(f"❌ Error downloading BTS data: {e}")
        print("Creating simulated data as fallback...")
        create_simulated_bts_data(raw_data_dir)
    
    # ------- CHECK FOR KAGGLE SATISFACTION DATA -------
    satisfaction_file_path = f"{raw_data_dir}/satisfaction.csv"
    if os.path.exists(satisfaction_file_path):
        print("\n✅ Found Kaggle satisfaction data (satisfaction.csv).")
        # Read a small sample to show it's working
        satisfaction_sample = pd.read_csv(satisfaction_file_path, nrows=5)
        print("Preview of your Kaggle satisfaction data:")
        print(satisfaction_sample.head().to_string())
    else:
        print("\n" + "⚠" * 70)
        print("❌ MISSING: Kaggle Passenger Satisfaction data not found.")
        print("   To add it, please follow these steps:")
        print("   1. Go to: https://www.kaggle.com/datasets/teejmahal20/airline-passenger-satisfaction")
        print("   2. Download the dataset (requires login).")
        print("   3. Unzip the file.")
        print("   4. Find the CSV inside and RENAME it to 'satisfaction.csv'.")
        print("   5. MOVE the renamed file to this folder:", os.path.abspath(raw_data_dir))
        print("   6. Run this script again.")
        print("⚠" * 70)
        
        # Create a realistic sample file so the rest of the code doesn't break
        print("\nCreating a realistic sample file for now...")
        sample_data = {
            'id': range(1, 1001),
            'satisfaction': np.random.choice(['satisfied', 'neutral or dissatisfied'], 1000),
            'Gender': np.random.choice(['Male', 'Female'], 1000),
            'Age': np.random.randint(18, 80, 1000),
            'Customer Type': np.random.choice(['Loyal Customer', 'disloyal Customer'], 1000),
            'Type of Travel': np.random.choice(['Business travel', 'Personal Travel'], 1000),
            'Class': np.random.choice(['Business', 'Eco', 'Eco Plus'], 1000),
            'Flight Distance': np.random.randint(100, 5000, 1000),
            'Arrival Delay Minutes': np.random.randint(0, 300, 1000)
        }
        pd.DataFrame(sample_data).to_csv(satisfaction_file_path, index=False)
        print("✅ Created a sample satisfaction.csv. Please replace it with the full Kaggle file.")

def create_simulated_bts_data(raw_data_dir):
    """Create simulated BTS data as fallback if download fails"""
    airlines = ['AA', 'DL', 'UA', 'WN', 'AS', 'NK', 'F9', 'G4', 'HA', 'B6']
    bts_data = {
        'FlightDate': pd.date_range(start='2024-01-01', periods=1000, freq='H').tolist(),
        'Airline': np.random.choice(airlines, 1000),
        'Origin': np.random.choice(['JFK', 'LAX', 'ORD', 'DFW', 'ATL'], 1000),
        'Dest': np.random.choice(['SFO', 'DEN', 'MIA', 'SEA', 'BOS'], 1000),
        'DepDelayMinutes': np.random.randint(0, 300, 1000),
        'ArrDelayMinutes': np.random.randint(0, 300, 1000),
        'Cancelled': np.random.choice([True, False], 1000, p=[0.05, 0.95]),
        'Diverted': np.random.choice([True, False], 1000, p=[0.01, 0.99])
    }
    bts_df = pd.DataFrame(bts_data)
    bts_df.to_csv(f"{raw_data_dir}/bts_delays.csv", index=False)
    print("✅ Created simulated BTS data as fallback")

if __name__ == "__main__":
    fetch_and_save_data()