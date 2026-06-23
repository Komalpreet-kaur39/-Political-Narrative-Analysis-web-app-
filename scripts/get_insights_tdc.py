# '''
#     This script generates insights from data using title, description and captions.
# '''

import pandas as pd
import os
import time
import csv
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai
import warnings
warnings.filterwarnings("ignore")

def summarize_captions(captions):
    # Create the prompt template for summarizing captions
    summary_template = f"""You are an expert at summarizing youtube captions. 
    Instructions :
        - Include any political party or figures (if mentioned) in the summary. 
        - Do not remove any political context from the captions while summarizing.
    Summarize the following captions of a youtube video in a concise manner:
    Captions: {captions}
    Summary:
    """

    # Initialize OpenAI API for summarization
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1024,
        api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )

    prompt = PromptTemplate(
        input_variables=["summary_template"],
        template="{summary_template}"
    )

    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    result = chain.run(summary_template=summary_template)

    return result.strip()

def check_bias(title, description, caption_summary):

    temp = f"""You are an expert at analyzing YouTube video using video title, descriptions and captions of news channels. 
        Your task is to determine whether the given video talks against or in support of a political party.

        List of political parties for reference : ['BJP(Bharatiya Janta Party)','INC(Indian National Congress)','AAP(Aam Aadmi Party)']

        Person-Political party association for reference : 
        {{ 'BJP' : ['Modi','Narendra Modi','Amit Shah','Shah','Nirmala Sitharaman','Kangana Ranaut','Yogi Adityanath','J. P. Nadda','B. S. Yediyurappa'],
        'Congress' : ['Mamata Banerjee','Akhilesh Yadav','Mahua Moitra','Uddhav Thackeray','Sharad Pawar','Rahul Gandhi','Sonia Gandhi','Priyanka Gandhi','M. K. Stalin','Mallikarjun Kharge','Supriya Sule','Supriya Shrinate'],
        'AAP' : ['Arvind Kejriwal','Atishi Marlena','Sanjay Singh','Manish Sisodia']}}

        OUTPUT FORMAT:
        {{
        "Orientation": "Supports or Opposes or N/A if not biased",
        "Explanation": "Explain why the video supports/ oppose a particular party",
        "Target Party": "Target political party who is supported or opposed",
        "Target Person": "Political person who is targeted if any",
        "Sentiment": "Positive, Negative, Neutral or N/A if not biased",
        }}

        ```
        Title: {title}
        Description: {description}
        Caption Summary: {caption_summary}
        ```
        """

    # Initialize OpenAI API for bias checking
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1024,
        api_key="xxxxxxxxxxxxxxxxxx"
    )

    # Define prompt template
    prompt = PromptTemplate(
        input_variables=["temp"],
        template="{temp}"
    )

    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)
    result = chain.run(temp=temp)

    return result

top3_file = 'data/cluster/top3/hi_ndtv_india_top3.csv'
df_top = pd.read_csv(top3_file)

df_top['captions'].fillna('', inplace=True)

base_filename = os.path.splitext(os.path.basename(top3_file))[0]
channel_name = '_'.join(base_filename.split('_')[1:-1])

# Path to output file
base_path = 'data/insights/title_desc_cap'
output_file = os.path.join(base_path, f'hi_{channel_name}_insights_tdc.csv')

# Load existing URLs if output file already exists
if os.path.exists(output_file):
    df_existing = pd.read_csv(output_file)
    existing_urls = set(df_existing['url'].tolist())
else:
    existing_urls = set()

with open(output_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Write header if the file does not exist
    if not os.path.exists(output_file):
        header = df_top.columns.tolist() + ['Caption Summary', 'Orientation', 'Explanation', 'Target Party', 'Target Person', 'Sentiment']
        writer.writerow(header)

    for index, row in df_top.iterrows():
        url = row['url']

        # Skip processing if the URL is already in the existing data
        if url in existing_urls:
            print("URL already exists. SKIPPING . . .")
            continue

        # Get title, description, and captions
        title = str(row['title']).replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")
        description = str(row['cleaned_description']).replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")
        captions = str(row['captions']).replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")

        # Summarize the captions
        print(len(captions))
        caption_summary = summarize_captions(captions[:100000])

        while True:
            try:
                result = check_bias(title, description, caption_summary)
                result_dict = eval(result)

                print(f'Processing Row Number : {index}')

                original_data = [row[col] for col in df_top.columns.tolist()]
                insights = [caption_summary, result_dict['Orientation'], result_dict['Explanation'], result_dict['Target Party'], result_dict['Target Person'], result_dict['Sentiment']]
                data = original_data + insights

                writer.writerow(data)
                print("---> Data written to file successfully !!")
                break

            except (SyntaxError, KeyError) as e:
                print(f"Error encountered: {e}, RETRYING . . .")
                break

        time.sleep(2)

