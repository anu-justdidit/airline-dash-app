import pandas as pd
import os

def load_and_clean_data():
    """Loads raw CSVs, cleans, merges, and saves processed data."""
    
    processed_data_dir = "../data/processed"
    os.makedirs(processed_data_dir, exist_ok=True)
    
    print("Loading and cleaning data...")
    
    try:
        # Load the raw data
        bts_df = pd.read_csv("../data/raw/bts_delays.csv")
        satisfaction_df = pd.read_csv("../data/raw/satisfaction.csv")
        
        print(f"BTS data shape: {bts_df.shape}")
        print(f"Satisfaction data shape: {satisfaction_df.shape}")
        
        # Clean BTS data
        print("Cleaning BTS data...")
        bts_df['FlightDate'] = pd.to_datetime(bts_df['FlightDate'], errors='coerce')
        bts_df = bts_df.dropna(subset=['FlightDate', 'Airline'])
        
        # Convert airline codes to full names for better merging
        airline_mapping = {
            'AA': 'American Airlines',
            'DL': 'Delta Air Lines', 
            'UA': 'United Airlines',
            'WN': 'Southwest Airlines',
            'AS': 'Alaska Airlines',
            'NK': 'Spirit Air Lines',
            'F9': 'Frontier Airlines',
            'G4': 'Allegiant Air',
            'HA': 'Hawaiian Airlines',
            'B6': 'JetBlue Airways'
        }
        
        bts_df['Airline_Name'] = bts_df['Airline'].map(airline_mapping)
        bts_df = bts_df.dropna(subset=['Airline_Name'])
        
        # Clean Satisfaction data
        print("Cleaning satisfaction data...")
        # Map satisfaction to numeric score
        satisfaction_df['Satisfaction_Score'] = satisfaction_df['satisfaction'].map({
            'satisfied': 1,
            'neutral or dissatisfied': 0
        })
        
        # Aggregate BTS data by airline
        print("Aggregating BTS data by airline...")
        airline_performance = bts_df.groupby('Airline_Name').agg(
            Total_Flights=('Airline', 'count'),
            Average_Departure_Delay=('DepDelayMinutes', 'mean'),
            Average_Arrival_Delay=('ArrDelayMinutes', 'mean'),
            Cancellation_Rate=('Cancelled', 'mean'),
            Diversion_Rate=('Diverted', 'mean')
        ).reset_index()
        
        # Aggregate Satisfaction data by airline type (assuming airline can be inferred from Class/Type of Travel)
        print("Aggregating satisfaction data...")
        satisfaction_agg = satisfaction_df.groupby('Class').agg(
            Avg_Satisfaction_Score=('Satisfaction_Score', 'mean'),
            Total_Surveys=('Satisfaction_Score', 'count')
        ).reset_index()
        
        # Create a mapping between airline class and airline names
        class_to_airline = {
            'Business': ['Delta Air Lines', 'American Airlines', 'United Airlines'],
            'Eco': ['Southwest Airlines', 'JetBlue Airways', 'Alaska Airlines'],
            'Eco Plus': ['Frontier Airlines', 'Spirit Air Lines', 'Allegiant Air']
        }
        
        # Create final merged dataset
        print("Creating final merged dataset...")
        merged_data = []
        for airline_class, airlines in class_to_airline.items():
            class_data = satisfaction_agg[satisfaction_agg['Class'] == airline_class].copy()
            for airline in airlines:
                airline_data = airline_performance[airline_performance['Airline_Name'] == airline].copy()
                if not airline_data.empty:
                    merged_row = {
                        'Airline': airline,
                        'Airline_Class': airline_class,
                        'Avg_Satisfaction_Score': class_data['Avg_Satisfaction_Score'].values[0],
                        'Total_Surveys': class_data['Total_Surveys'].values[0],
                        'Total_Flights': airline_data['Total_Flights'].values[0],
                        'Avg_Departure_Delay': airline_data['Average_Departure_Delay'].values[0],
                        'Avg_Arrival_Delay': airline_data['Average_Arrival_Delay'].values[0],
                        'Cancellation_Rate': airline_data['Cancellation_Rate'].values[0],
                        'Diversion_Rate': airline_data['Diversion_Rate'].values[0]
                    }
                    merged_data.append(merged_row)
        
        final_df = pd.DataFrame(merged_data)
        
        # Save the final processed data
        final_df.to_csv(f"{processed_data_dir}/merged_data.csv", index=False)
        print("✅ Cleaned and merged data saved to data/processed/merged_data.csv")
        print(f"Final dataset shape: {final_df.shape}")
        print("\nFinal data preview:")
        print(final_df.to_string())
        
        return final_df
        
    except Exception as e:
        print(f"❌ Error in data processing: {e}")
        raise

if __name__ == "__main__":
    load_and_clean_data()