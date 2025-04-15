import requests
import pandas as pd

# Configuration
# API_KEY = "d3f52c573ad14e20a6545cfc2b16cc38"  # Replace with your actual WTO API key
API_KEY = "f7d7128d487c42578e655f7545e7c7c7"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
BASE_URL = "https://api.wto.org/timeseries/v1/data"

# Function to fetch data for a specific indicator
def fetch_indicator_data(indicator_code, reporter="840", year="2019", partner=None):
    """Fetch data from WTO Timeseries API for a given indicator"""
    
    # Base parameters for all requests
    params = {
        "i": indicator_code,  # Indicator code
        "r": reporter,        # Reporter country code (840=USA)
        "yr": year,           # Year
        "fmt": "json"         # Request JSON format
    }
    
    # Add partner only for bilateral trade data
    if partner and indicator_code == "HS_M_0010":
        params["p"] = partner
    
    print(f"Fetching data for indicator {indicator_code}...")
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "Dataset" in data and data["Dataset"]:
            df = pd.DataFrame(data["Dataset"])
            print(f"Retrieved {len(df)} records")
            return df
        else:
            print(f"No data found for indicator {indicator_code}")
            return pd.DataFrame()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return pd.DataFrame()

# Main execution
def main():
    # United States (840) as reporter, China (156) as partner
    reporter_code = "840"
    partner_code = "156"
    year = "2019"
    
    # 1. Fetch MFN Tariff Data (HS_A_0020)
    print("\nFetching MFN tariff rates...")
    tariff_df = fetch_indicator_data(
        "HS_A_0020",          # HS MFN - Simple average ad valorem duty (Percent)
        reporter=reporter_code,
        year=year
    )
    
    # 2. Fetch Bilateral Import Data (HS_M_0010)
    print("\nFetching bilateral import data...")
    import_df = fetch_indicator_data(
        "HS_M_0010",          # Bilateral imports by detailed HS codes
        reporter=reporter_code,
        year=year,
        partner=partner_code
    )
    
    # Save results to CSV files
    if not tariff_df.empty:
        tariff_df.to_csv("us_mfn_tariffs_china_2019.csv", index=False)
        print("MFN tariff data saved to us_mfn_tariffs_china_2019.csv")
        print("\nSample tariff data:")
        print(tariff_df.head())
    
    if not import_df.empty:
        import_df.to_csv("us_imports_from_china_2019.csv", index=False)
        print("Import data saved to us_imports_from_china_2019.csv")
        print("\nSample import data:")
        print(import_df.head())
    
    # Create a combined dataset
    if not tariff_df.empty and not import_df.empty:
        # Extract key columns and rename for clarity
        if "ProductSector" in tariff_df.columns and "ProductSector" in import_df.columns:
            tariff_subset = tariff_df[["ProductSector", "Value"]].rename(
                columns={"Value": "MFN_Tariff_Rate"}
            )
            
            import_subset = import_df[["ProductSector", "Value"]].rename(
                columns={"Value": "Import_Value_USD"}
            )
            
            # Merge on HS code
            combined_df = pd.merge(
                tariff_subset, import_subset, 
                on="ProductSector", how="outer"
            )
            
            combined_df.to_csv("us_tariffs_and_imports_china_2019.csv", index=False)
            print("\nCombined data saved to us_tariffs_and_imports_china_2019.csv")
            print("\nSample combined data:")
            print(combined_df.head())

if __name__ == "__main__":
    main()