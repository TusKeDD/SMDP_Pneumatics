import pandas as pd

# Define the file name
ENQUIRIES_FILE = "enquiries.csv"

# Define your columns
columns = ["Company", "User", "Contact", "Products", "Timestamp", "Mobile", "Email"]

# Create an empty DataFrame with just headers
df = pd.DataFrame(columns=columns)

# Save it as CSV
df.to_csv(ENQUIRIES_FILE, index=False, encoding="utf-8")

print(f"✅ New CSV created: {ENQUIRIES_FILE}")
