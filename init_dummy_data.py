import sqlite3
import pandas as pd
import os

def init_sample_db():
    db_path = "sample_data.db"
    conn = sqlite3.connect(db_path)
    
    # Create sample sales table
    data = {
        "date": ["2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", 
                 "2023-07", "2023-08", "2023-09", "2023-10", "2022-10"],
        "sales_amount": [1000, 1200, 1100, 1300, 1500, 1400, 1600, 1700, 1800, 2000, 1800],
        "region": ["East", "East", "West", "West", "East", "East", "West", "West", "East", "East", "East"]
    }
    df = pd.DataFrame(data)
    df.to_sql("sales_data", conn, if_exists="replace", index=False)
    
    conn.close()
    print(f"Sample database created at {os.path.abspath(db_path)}")

if __name__ == "__main__":
    init_sample_db()
