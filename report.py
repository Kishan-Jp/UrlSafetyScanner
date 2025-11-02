import pandas as pd
import re

# Define the data
data = [
    ["L0085180", 59, "F", "02/06", "No", "Never done 04/06 Tropt 21", None],
    ["61207150", 75, "F", "07/06", "No", "Never done 07/06 Tropt 102", None],
    ["D9078556", 50, "F", "09/06", "No", "Never done 09/06 Tropt 5.9", None],
    ["LX020178", 58, "M", "12/06", "No", "Never done 12/06 Tropt 45", None],
    ["60579157", 81, "M", "20/06", "No", "22/06 20/06 Tropt 107", 2],
]

# Create the DataFrame
df = pd.DataFrame(data, columns=[
    "Patient ID", "Age", "Gender", "Admit Date", "Lipid ≤24h", "Lipid profile later", "Days Delay"
])

# Assuming the year is 2025 for all dates
YEAR = 2025

# Convert 'Admit Date' to datetime objects
df['Admit Date'] = df['Admit Date'].apply(lambda x: pd.to_datetime(f"{x}/{YEAR}", format='%d/%m/%Y', errors='coerce'))

# Define a function to extract the first valid date from the 'Lipid profile later' string
def extract_date(text):
    if pd.isna(text):
        return None
    # Regex to find dates like "dd/mm" or "dd/mm/yyyy"
    match = re.search(r'\b(\d{1,2}/\d{1,2}(?:/\d{4})?)\b', str(text))
    if match:
        date_str = match.group(1)
        # Add the year if it's not already present
        if len(date_str.split('/')) == 2:
            return pd.to_datetime(f"{date_str}/{YEAR}", format='%d/%m/%Y', errors='coerce')
        else:
            return pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
    return None

# Apply the function to the 'Lipid profile later' column
df['Lipid profile date'] = df['Lipid profile later'].apply(extract_date)

# Calculate the difference in days
df['Days Difference'] = (df['Lipid profile date'] - df['Admit Date']).dt.days

# Drop the columns that are no longer needed for the final output
df = df.drop(columns=['Lipid profile later', 'Lipid profile date', 'Days Delay'])

# Save the final DataFrame to an Excel file
df.to_excel("Cleaned_ACS_Audit.xlsx", index=False)
print("✅ File saved as Cleaned_ACS_Audit.xlsx")