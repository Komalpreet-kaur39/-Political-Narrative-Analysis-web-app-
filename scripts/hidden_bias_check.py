import pandas as pd

td_path = 'data/insights/title_desc/hi_ndtv_india_insights_td.csv'
tdc_path = 'data/insights/title_desc_cap/hi_ndtv_india_insights_tdc.csv'

df_td = pd.read_csv(td_path)
df_tdc = pd.read_csv(tdc_path)

# Merge df_td and df_tdc on the 'url' column
merged_df = pd.merge(df_td, df_tdc, on='url', suffixes=('_td', '_tdc'))

# Function to determine 'Hidden Bias'
def determine_hidden_bias(row):
    # Check the conditions for Hidden Bias
    if row['Sentiment_td'] in ['Neutral', 'Positive'] and \
       row['Orientation_tdc'] == 'Opposes' and \
       row['Target Party_tdc'] == 'BJP':
        return 'Yes'
    if not (row['Orientation_td'] == 'Opposes' and row['Target Party_td'] == 'BJP') and \
       row['Orientation_tdc'] == 'Opposes' and \
       row['Target Party_tdc'] == 'BJP':
        return 'Yes'
    return 'No'

# Apply the function to the merged DataFrame
merged_df['Hidden Bias'] = merged_df.apply(determine_hidden_bias, axis=1)

# Extract the 'Hidden Bias' column and join back to the original DataFrames
df_td['Hidden Bias'] = merged_df['Hidden Bias']
df_tdc['Hidden Bias'] = merged_df['Hidden Bias']

df_td.to_csv(td_path, quoting=1, index=False)
df_tdc.to_csv(tdc_path, quoting=1, index=False)