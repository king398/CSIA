import pandas as pd
from datetime import datetime

# Get the current date and time
df = pd.DataFrame({'Job_ID': [1, 2, 3],
                   'Pages': [1, 6, 100],
                   "Time_Sent":["2024-04-03 11:10:00", "2024-04-03 11:05:00", "2024-04-03 11:10:00"]})
def get_priority(df):
    if df['Pages'] >= 3:
        df['Priority'] = 1
    elif df['Pages'] >= 10:
        df['Priority'] = 2
    elif df['Pages'] >= 20:
        df['Priority'] = 3
    elif df['Pages'] > 50:
        df['Priority'] = 4
    return df
df  = df.apply(get_priority, axis=1)
df['Time_Sent'] = pd.to_datetime(df['Time_Sent'])
# sort the dataframe by the TIme  with the oldest job first
next_job_id = None

for i in df.iterrows():
    minutes_waited = (datetime.now() - i[1]['Time_Sent']).total_seconds() / 60
    if minutes_waited > 10:
        next_job_id = i[1]['Job_ID']
        break
df = df.sort_values(by='Priority')


