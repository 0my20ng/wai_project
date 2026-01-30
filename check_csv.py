import csv
from collections import Counter
import os

def check_csv():
    try:
        # Try both utf-8 and cp949
        for enc in ['utf-8', 'cp949']:
            try:
                with open(os.path.join('data', 'total_welfare_data.csv'), 'r', encoding=enc) as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    print(f"Encoding: {enc}")
                    print(f"Header: {header}")
                    
                    sources = []
                    for row in reader:
                        if len(row) >= 6:
                            sources.append(row[5])
                    
                    print(f"Total rows read: {len(sources)}")
                    print(f"Source counts: {Counter(sources)}")
                break
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_csv()
