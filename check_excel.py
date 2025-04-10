import pandas as pd
import json

# קריאת הקובץ
df = pd.read_excel('amj.xlsx', sheet_name='game stats')

# לקחת 5 שורות ראשונות
sample = df.head(5)

# המרה למילון
sample_dict = sample.to_dict('records')

# הדפסת המילון
print(json.dumps(sample_dict, ensure_ascii=False, indent=2))

# הדפסת שמות העמודות
print('\nשמות העמודות:')
for idx, col in enumerate(df.columns):
    print(f'עמודה {idx}: {col}')
