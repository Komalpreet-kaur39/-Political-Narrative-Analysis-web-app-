import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os
import plotly.express as px
from chatbot import chatbot_query
# Function to load the YouTube data from the provided file path
def load_video_data_from_file(file_path):
    try:
        # Read the data from the CSV file
        df = pd.read_csv(file_path)

        # Ensure the data is loaded
        if df.empty:
            st.write("No video data found in the file.")
        return df
    except Exception as e:
        st.error(f"Error loading data from file: {e}")
        return pd.DataFrame()


# Streamlit UI
st.title('YouTube Video Analysis')

# List of available channels and their corresponding file paths
channel_files = {
    'NDTV India': 'data/insights/title_desc_cap/hi_ndtv_india_insights_tdc.csv',
    'Republic World': 'data/insights/title_desc_cap/en_Republic_World_insights_tdc.csv',
    'Times Now': 'data/insights/title_desc_cap/en_Times_Now_insights_tdc.csv',  
    'NDTV(eng)': 'data/insights/title_desc_cap/en_NDTV_insights_tdc.csv',   
}
# Dropdown to select a channel
selected_channel = st.selectbox('Select a Channel', options=list(channel_files.keys()))

# Load the data based on the selected channel
file_path = channel_files[selected_channel]
df = load_video_data_from_file(file_path)

# Define the file paths to the saved graphs for each channel
graph_files = {
    'NDTV India': 'images/ndtv_images',
    'Republic World': 'images/RW_images',
    'Times Now': 'images/TN_images',
    'NDTV(eng)': 'images/en_ndtv_images',
}

# Define available graph names
graph_names = [
    "Counts of Each Party",
    "Sentiment Counts of Each Party",
    "Orientation Counts of Each Party",
    "Counts of Each Alliance",
    "Sentiment Counts of Each Alliance",
    "Orientation Counts of Each Alliance",
    "Total Views Per Target Party",
    "Timeline of Sentiments",
    "Hidden Bias Towards BJP"
]

if not df.empty:
    # Define the tabs
    tabs = st.tabs(["Data Overview", "Visualizations", "Interactive Features","caption summary"])

    with tabs[0]:
        # Data Overview Tab
        st.subheader(f'{selected_channel} - Video Data')
        st.write("### Summary Insights")
        st.metric(label="Total Videos", value=len(df))
        st.metric(label="Average Views", value=f"{df['views'].mean():,.2f}")
        st.metric(label="Average Likes", value=f"{df['likes'].mean():,.2f}")

        st.write("### Data Preview")
        st.write(df.head(10))

        # Display column names for better insight
        # st.write("### Available Columns:")
        # st.write(df.columns)

    with tabs[1]:
        # Visualizations Tab
        st.subheader(f'{selected_channel} - Video Data Visualizations')

         # Allow the user to select the type of chart
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart"])

        # Define columns allowed for each chart type
        bar_chart_columns = ['Sentiment', 'views', 'likes', 'title', 'comments']
        line_chart_columns = ['views', 'comments', 'likes', 'Sentiment', 'publish_date']
        
        df['short_title'] = df['title'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)
        
        df_plot = df.copy()
        
        # Filter available columns for Bar Chart
        bar_chart_columns_available = [col for col in bar_chart_columns if col in df.columns]
        
        # Filter available columns for Line Chart
        line_chart_columns_available = [col for col in line_chart_columns if col in df.columns]
        
       # Allow the user to select columns for x and y axes or single column for Pie chart
        if chart_type != "Pie Chart":
            if chart_type == "Bar Chart":
                # Filter columns for bar chart dynamically
                x_column = st.selectbox("Select X-Axis Column", bar_chart_columns_available)
                y_column = st.selectbox("Select Y-Axis Column", bar_chart_columns_available)
            elif chart_type == "Line Chart":
                # Filter columns for line chart dynamically
                x_column = st.selectbox("Select X-Axis Column", line_chart_columns_available)
                y_column = st.selectbox("Select Y-Axis Column", line_chart_columns_available)
        
            # If 'title' is selected for either axis, use the shortened title
            if x_column == 'title':
                df_plot['title'] = df_plot['short_title']  # Use the shortened title for X-axis
                x_column = 'title'  # Set the x_column to 'short_title' for the plot
            if y_column == 'title':
                df_plot['title'] = df_plot['short_title']  # Use the shortened title for Y-axis
                y_column = 'title'  # Set the y_column to 'short_title' for the plot
        
            # Generate the chart based on the selected chart type
            if chart_type == "Bar Chart":
                fig = px.bar(df_plot, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
            elif chart_type == "Line Chart":
                fig = px.line(df_plot, x=x_column, y=y_column, title=f"{y_column} over {x_column}")
            
        else:
            pie_column = st.selectbox("Select Column for Pie Chart", df.columns.tolist())
            fig = px.pie(df, names=pie_column, title=f"Distribution of {pie_column}")

        # Display the dynamically generated graph
        st.plotly_chart(fig)

        # Visual enhancements with Plotly
        st.write("### Sentiment Distribution")
        if 'Sentiment' in df.columns:
            fig_sentiment = px.bar(df, x='Sentiment', title="Sentiment Distribution", color='Sentiment')
            st.plotly_chart(fig_sentiment)

        # st.write("### Top 10 Videos by Views")
        # if 'views' in df.columns and 'title' in df.columns:
        #     fig_views = px.bar(df.sort_values(by="views", ascending=False).head(10),
        #                        x='title', y='views', title="Top 10 Videos by Views",
        #                        labels={"title": "Video Title", "views": "View Count"})
        #     st.plotly_chart(fig_views)
            
        st.write("### Sentiment Comparison")
        metric = st.selectbox('Select Metric', ['views', 'likes', 'comments'])
        sentiment_chart = px.bar(
            df.groupby('Sentiment')[metric].sum().reset_index(),
            x='Sentiment', y=metric, color='Sentiment',
            title=f"{metric.capitalize()} by Sentiment"
        )
        st.plotly_chart(sentiment_chart)
      
        # date_range = st.date_input('Select Date Range', [])
        # sentiment_filter = st.selectbox("Select Sentiment", ['Positive', 'Negative', 'Neutral'])
        # df_filtered = df[(df['publish_date'] >= date_range[0]) & (df['publish_date'] <= date_range[1])]
        # df_filtered = df_filtered[df_filtered['Sentiment'] == sentiment_filter]

        # Graph display for selected graph
        st.write("### Graphs")
        selected_graph = st.selectbox("Select a Graph to Display", options=graph_names)

        # Construct the path to the selected graph
        graph_directory = graph_files[selected_channel]
        graph_file_mapping = {
            "Counts of Each Party": "counts of each party.png",
            "Sentiment Counts of Each Party": "sentiment counts of each party.png",
            "Orientation Counts of Each Party": "orientation counts of each party.png",
            "Counts of Each Alliance": "counts of each alliance.png",
            "Sentiment Counts of Each Alliance": "sentiment counts of each alliance.png",
            "Orientation Counts of Each Alliance": "orientation counts of each alliance.png",
            "Total Views Per Target Party": "total view.png",
            "Timeline of Sentiments": "timeline sentiment.png",
            "Hidden Bias Towards BJP": "hidden bias.png",
        }

        selected_graph_path = os.path.join(graph_directory, graph_file_mapping[selected_graph])

        # Display the selected graph
        if os.path.exists(selected_graph_path):
            st.image(Image.open(selected_graph_path), caption=selected_graph)
        else:
            st.error(f"Graph '{selected_graph}' not found for {selected_channel}. Please check the file path.")

    with tabs[2]:
        # Interactive Features Tab
        st.subheader(f'{selected_channel} - Interactive Features')

        # Allow users to filter based on sentiment
        sentiment_filter = st.selectbox('Filter by Sentiment', options=['All', 'Positive', 'Negative', 'Neutral'])
        if sentiment_filter != 'All':
            df = df[df['Sentiment'] == sentiment_filter]
        st.write(f"Showing {len(df)} {sentiment_filter} videos:",df)

        # # Search bar for filtering by video title
        # search_query = st.text_input("Search by Video Title")
        # if search_query:
        #     df = df[df['title'].str.contains(search_query, case=False, na=False)]
        #     st.write(f"Filtered {len(df)} videos matching '{search_query}'",df)
        # Search bar for filtering by video title
        search_query = st.text_input("Search by Video Title")
        if search_query:
            # Filter videos based on the search query
            filtered_df = df[df['title'].str.contains(search_query, case=False, na=False)]
            
            if not filtered_df.empty:
                # Display the filtered videos if any matches are found
                st.write(f"Filtered {len(filtered_df)} videos matching '{search_query}'", filtered_df)
            else:
                # Display a message if no matches are found
                st.warning(f"No videos found matching '{search_query}'.")

        # Sorting dropdown
        sort_option = st.selectbox("Sort By", options=["views", "likes", "comments"])
        sort_order = st.radio("Order", ["Descending", "Ascending"])
        is_ascending = sort_order == "Ascending"
        df = df.sort_values(by=sort_option, ascending=is_ascending)
        st.write("### Sorted Data", df)

        df['engagement_rate'] = (df['likes'] + df['comments']) / df['views']
        df['comment_to_like_ratio'] = df['comments'] / df['likes']
        st.write("### Engagement Metrics")
        st.write(df[['title', 'engagement_rate', 'comment_to_like_ratio']].sort_values(by='engagement_rate', ascending=False).head(10))

        # # Add interactivity with filters and sliders
        # top_n = st.slider("Select Top N Videos by Views", min_value=1, max_value=20, value=5)
        # st.write(df[['title', 'views']].sort_values(by='views', ascending=False).head(top_n))

    with tabs[3]:
        # Caption Summary Tab
        st.subheader(f'{selected_channel} - Caption Summary')
    
       # Input search bar
        search_query = st.text_input(
            "Search for Video Title",
            placeholder="Type a title to search...",
            # help="Start typing to get suggestions for video titles."
        )
    
        # Filter titles based on the input
        if search_query:
            # Filter titles containing the search query (case-insensitive)
            matching_titles = df[df['title'].str.contains(search_query, case=False, na=False)]['title'].tolist()
            
            if matching_titles:
                # Suggest matching titles for user to select
                selected_title = st.selectbox("Select a Title", options=matching_titles)
                
                # Display caption summary for the selected title
                if selected_title:
                    selected_video = df[df['title'] == selected_title]
                    caption_summary = selected_video.iloc[0]['Caption Summary']  
                    st.write(f"**Caption Summary for '{selected_title}':**")
                    st.write(caption_summary)
            else:
                st.warning("No matching titles found. Try refining your search.")
        else:
            st.info("Type a title to start searching.")
    # with tabs[4]:
    #     # Chatbot Tab
    #     st.subheader(f"Chatbot for {selected_channel}")
        
    #     st.write("Ask any question related to the data, and the chatbot will analyze and respond.")

    #     # User Input for Chatbot Query
    #     user_query = st.text_input("Enter your question:", placeholder="e.g., What are the top 5 videos with the most views?")
        
    #     if user_query:
    #         st.write(f"**You:** {user_query}")
    #         with st.spinner("The bot is thinking... please wait!"):
    #          # response = chatbot_query(user_query, df)
    #             try:
    #             # Fetch the response from the chatbot
    #                 response = chatbot_query(user_query, df)
    #                 # Display the chatbot's response
    #                 st.write("### Chatbot Response:")
    #                 st.write(response)
    #             except Exception as e:
    #         # In case of any unexpected errors in the chatbot processing
    #                 st.error(f"An unexpected error occurred: {str(e)}")
        
    #     #  add a button for clearing the input field
    #     # if st.button("Clear Input"):
    #     #     user_query = ""
else:
    st.write("Please upload a valid CSV file.")