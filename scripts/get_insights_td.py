import pandas as pd
import os
import time
import csv
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from unidecode import unidecode

def check_bias(title, description):
    temp = f"""You are an expert at analyzing YouTube video using video title and description of news channels. 
    Your task is to determine whether the given video talks against or in support of a political party.

    List of political parties for reference : ['BJP(Bharatiya Janta Party)','INC(Indian National Congress)','AAP(Aam Aadmi Party)']

    Person-Political party association for reference : 
    {{ 'BJP' : ['Modi','Narendra Modi','Amit Shah','Shah','Nirmala Sitharaman','Kangana Ranaut','Yogi Adityanath','J. P. Nadda','B. S. Yediyurappa'],
    'Congress' : ['Mamata Banerjee','Akhilesh Yadav','Mahua Moitra','Uddhav Thackeray','Sharad Pawar','Rahul Gandhi','Sonia Gandhi','Priyanka Gandhi','M. K. Stalin','Mallikarjun Kharge','Supriya Sule','Supriya Shrinate'],
    'AAP' : ['Arvind Kejriwal','Atishi Marlena','Sanjay Singh','Manish Sisodia']}}

    OUTPUT FORMAT:
    {{
    "Orientation": "Supports or Opposes or N/A if not biased",
    "Explanation": "explain why the video supports/ oppose a particular party",
    "Target Party": "target political party who is supported or opposed",
    "Target Person": "political person who is targeted if any",
    "Sentiment": "Positive, Negative, Neutral or N/A if not biased",
    }}

    
    Title: {title}
    Description: {description}
    
    """

    # Initialize OpenAI API
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1024,
        api_key="xxxxxxxxxxxxxxxxxx"  # Add your OpenAI API key here
    )

    # Define prompt template
    prompt = PromptTemplate(
        input_variables=["temp"],
        template="{temp}"
    )

    # Use RunnableSequence instead of LLMChain
    chain = RunnableSequence(prompt | llm)

    # Generate JSON representation using the chain
    result = chain.invoke({"temp": temp})  # Pass input as a dictionary

    return json.loads(result.content)  # Use json.loads instead of eval

top3_file = 'data/cluster/top3/hi_ndtv_india_top3.csv'
df_top = pd.read_csv(top3_file)

output_file = 'data/insights/title_desc/hi_ndtv_india_insights_td.csv'

file_exists = os.path.exists(output_file)

if file_exists:
    df_existing = pd.read_csv(output_file)
    existing_urls = set(df_existing['url'].tolist())
else:
    existing_urls = set()

with open(output_file, 'a', newline='') as f:
    writer = csv.writer(f)

    if not file_exists:
        header = df_top.columns.tolist() + ['Orientation', 'Explanation', 'Target Party', 'Target Person', 'Sentiment']
        writer.writerow(header)

    for index, row in df_top.iterrows():
        url = row['url']

        # Skip processing if the URL is already in the existing data
        if url in existing_urls:
            print("URL already exists. SKIPPING . . .")
            continue

        # Get title and description
        title = row['title']
        description = row['cleaned_description']

        # # Replacing non-standard characters and quotes to prevent syntax errors
        # title = title.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")
        # description = description.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")

        # Replace non-standard characters in title
        title = title.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")

        # Ensure description is a string, then replace non-standard characters
        if isinstance(description, str):
            description = description.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('"', "'")
        else:
            description = ""  # Set a default empty string if description is NaN

        retries = 5  # Number of retries for handling rate limits
        for attempt in range(retries):
            try:
                result_dict = check_bias(title, description)
                
                print(f'Processing Row Number: {index}')

                original_data = [row[col] for col in df_top.columns.tolist()]
                insights = [
                    result_dict['Orientation'],
                    result_dict['Explanation'],
                    result_dict['Target Party'],
                    result_dict['Target Person'],
                    result_dict['Sentiment']
                ]
                data = original_data + insights

                writer.writerow([unidecode(str(i)) for i in data])
                print("---> Data written to file successfully !!")
                break  # Exit retry loop on success

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error encountered: {e}, RETRYING . . .")
                time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break  # Exit on unexpected errors

        time.sleep(2)  # Delay between API calls to avoid rate limits
