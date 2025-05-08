from utils.database import Database
import streamlit as st
import pandas as pd
from utils.gpt_helper import GPTHelper
from utils.threat_analyzer import ThreatAnalyzer, NewsScraper
from templates.prompts import PROMPT_TEMPLATES, SAMPLE_QUERIES
from components.ui import render_response

# Initialize session state
if 'threat_analyzer' not in st.session_state:
    st.session_state.threat_analyzer = ThreatAnalyzer()
if 'gpt_helper' not in st.session_state:
    st.session_state.gpt_helper = GPTHelper()
if 'news_scraper' not in st.session_state:
    st.session_state.news_scraper = NewsScraper()


def main():
    st.title("Cyber Threat Intelligence Platform")
    st.markdown("Get insights from AI analysis or live news sources.")

    # Mode selection
    mode = st.radio(
        "Select Mode:", ["Single Source Analysis", "Source Comparison"],
        help="Choose between single source analysis or compare multiple sources"
    )

    # Initialize data_source with a default value
    data_source = "GPT Analysis"

    # Original data source selection for single source mode
    if mode == "Single Source Analysis":
        data_source = st.radio(
            "Choose your data source:", ["GPT Analysis", "Live News"],
            help="Select whether to use AI analysis or fetch live news")

        if data_source == "GPT Analysis":
            st.header("AI-Powered Threat Analysis")

            # Query input section
            st.subheader("Query Input")
            use_template = st.checkbox("Use Template")

            if use_template:
                template_key = st.selectbox("Select Template",
                                            list(PROMPT_TEMPLATES.keys()))
                template = PROMPT_TEMPLATES[template_key]["template"]
                query = template
            else:
                query = st.text_area("Enter your threat analysis query:")

            if st.button("Analyze"):
                with st.spinner("Analyzing threat data..."):
                    # Get GPT analysis
                    response = st.session_state.gpt_helper.analyze_threat(
                        query)

                    # Tag the response
                    tags = st.session_state.gpt_helper.tag_threat_data(
                        str(response))

                    # Store the analysis
                    analysis = st.session_state.threat_analyzer.store_response(
                        query, response, tags)

                    # Store in SQLite database
                    db = Database()
                    db.store_analysis(query, response, tags)

                    # Indicate successful storage
                    if 'error' not in analysis:
                        st.success("✅ Analysis stored successfully")

                    # Display response
                    render_response(response, tags)

            # Sample queries section
            with st.expander("Sample Queries"):
                for sample_query in SAMPLE_QUERIES:
                    if st.button(sample_query, key=f"gpt_{sample_query}"):
                        st.session_state['query'] = sample_query
                        st.rerun()

        else:  # Live News
            st.header("Live Security News")

            # Predefined queries for news
            news_queries = [
                "Australian superannuation cyberattack",
                "SQL injection attack", "DaVita ransomware attack April 2025",
                "data breach 2025", "AI in cybersecurity",
                "cloud security breaches", "Phishing attack trends 2025",
                "Recent Cyberattack in Australia", "latest trends in hacking",
                "cybersecurity job market"
            ]

            selected_query = st.selectbox("Select a news topic:", news_queries)

            articles_count = st.slider("Number of articles to fetch", 1, 10, 3)

            if st.button("Fetch News"):
                with st.spinner("Fetching latest news..."):
                    articles = st.session_state.news_scraper.fetch_articles(
                        selected_query, page_size=articles_count)

                    if articles:
                        from dateutil import parser

                        db = Database()
                        for article in articles:
                            db.store_web_scraping_analysis(
                                query=selected_query,
                                title=article.get('title', 'No title'),
                                author=article.get('author', 'Unknown'),
                                description=article.get('description', ''),
                                content=article.get('content', ''),
                                url=article.get('url', ''),
                                published_at=parser.parse(
                                    article['publishedAt'])
                                if article.get('publishedAt') else None,
                                response=article)

                        for article in articles:
                            with st.container():
                                st.markdown("---")
                                st.markdown(
                                    f"### {article.get('title', 'No title')}")
                                st.markdown(
                                    f"*By {article.get('author', 'Unknown')} | {article.get('publishedAt', 'No date')}*"
                                )
                                st.markdown(
                                    f"{article.get('description', 'No description')}"
                                )
                                st.markdown(
                                    f"[Read full article]({article.get('url', '#')})"
                                )
                    else:
                        st.error(
                            "No articles found. Please try a different topic or try again later."
                        )

    # Database Viewer section
    st.header("Database Viewer", anchor="database-viewer")
    if st.button("View Both Databases"):
        db = Database()
        gpt_df = db.to_dataframe()
        web_df = db.to_dataframe_web_scraping()

        if not gpt_df.empty:
            st.subheader("GPT Analysis Data")
            st.dataframe(gpt_df[['timestamp', 'query', 'tags']],
                         use_container_width=True,
                         hide_index=True)

        if not web_df.empty:
            st.subheader("Web Scraping Data")
            st.dataframe(web_df[['timestamp', 'query', 'title', 'author']],
                         use_container_width=True,
                         hide_index=True)

        if gpt_df.empty and web_df.empty:
            st.warning("No data found in either database.")

            # Show full response for selected row
            if len(df) > 0:
                selected_query = st.selectbox(
                    "Select a query to view full response:",
                    df['query'].unique())
                if selected_query:
                    selected_row = df[df['query'] == selected_query].iloc[0]
                    with st.expander("View Full Response"):
                        st.json(selected_row['response'])

    # Export section
    if data_source == "GPT Analysis":
        st.header("Export Analysis")
        export_format = st.selectbox("Export Format", ["csv", "json"])
        if st.button("Export Data"):
            data = st.session_state.threat_analyzer.export_analysis(
                format=export_format)
            if data:
                st.download_button(
                    label=f"Download {export_format.upper()}",
                    data=data,
                    file_name=f"threat_analysis.{export_format}",
                    mime=f"text/{export_format}")

    # Export section for Web Scraping (Live News)
    if data_source == "Live News":
        st.header("Export News Data")
        export_format = st.selectbox("Export Format", ["csv", "json"],
                                     key="news_export_format")
        if st.button("Export News Data"):
            db = Database()

            # Update the method name to the correct one in the class
            if export_format == "csv":
                # Use export_web_scraping_analysis for CSV export
                data = db.export_web_scraping_analysis(format="csv")
                mime_type = "text/csv"
                file_ext = "csv"
            else:
                # Use export_web_scraping_analysis for JSON export
                data = db.export_web_scraping_analysis(format="json")
                mime_type = "application/json"
                file_ext = "json"

            if data:
                st.download_button(
                    label=f"Download News Data ({export_format.upper()})",
                    data=data,
                    file_name=f"web_scraping_data.{file_ext}",
                    mime=mime_type)

    if mode == "Source Comparison":
        st.header("Threat Source Comparison")
        comparison_query = st.text_input("Enter your comparison query:")

        if st.button("Compare Sources"):
            if comparison_query:
                # Use tabs for comparison
                tab1, tab2 = st.tabs(["AI Analysis", "News Analysis"])

                with tab1:
                    with st.spinner("Getting AI analysis..."):
                        try:
                            gpt_response = st.session_state.gpt_helper.analyze_threat(
                                comparison_query)
                            tags = st.session_state.gpt_helper.tag_threat_data(
                                str(gpt_response))
                            render_response(gpt_response, tags)
                        except Exception as e:
                            st.error(f"Error getting AI analysis: {str(e)}")

                with tab2:
                    with st.spinner("Fetching news..."):
                        try:
                            articles = st.session_state.news_scraper.fetch_articles(
                                comparison_query, page_size=5)

                            # Debug logging
                            st.write(f"Found {len(articles)} total articles")

                            if articles and len(articles) > 0:
                                for article in articles:
                                    with st.container():
                                        st.markdown("---")
                                        st.markdown(
                                            f"### {article.get('title', 'No title')}"
                                        )
                                        st.markdown(
                                            f"*By {article.get('author', 'Unknown')} | {article.get('publishedAt', 'No date')}*"
                                        )
                                        st.markdown(
                                            f"{article.get('description', 'No description')}"
                                        )
                                        st.markdown(
                                            f"[Read full article]({article.get('url', '#')})"
                                        )
                            else:
                                st.error(
                                    f"No news articles found for query: {comparison_query}"
                                )
                        except Exception as e:
                            st.error(f"Error fetching news: {str(e)}")
            else:
                st.warning("Please enter a query to compare sources.")

        st.markdown("---")


if __name__ == "__main__":
    st.set_page_config(page_title="Cyber Threat Intelligence Platform",
                       page_icon="🛡️",
                       layout="wide")
    main()
