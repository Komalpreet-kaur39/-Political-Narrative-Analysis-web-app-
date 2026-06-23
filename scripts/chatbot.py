import openai

def chatbot_query(query, df):
    """
    Responds to the user's query by analyzing the loaded data.
    """
    try:
        # Example prompt to give context to the chatbot
        prompt = f"""
        You are a data analyst with expertise in YouTube analytics. 
        Use the following dataset to answer the user's query:
        {df.head(10).to_string()}
        
        User's Query: {query}
        """
        # Send the query to OpenAI's API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
            api_key=openai.api_key  # Ensure your API key is set in the environment

        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error processing query: {e}"
