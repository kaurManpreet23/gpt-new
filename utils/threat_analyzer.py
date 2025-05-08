import requests
import time
import pandas as pd
from datetime import datetime


class ThreatAnalyzer:

    def __init__(self):
        self.responses = []

    def store_response(self, query, response, tags):
        analysis = {
            'timestamp': datetime.utcnow(),
            'query': query,
            'response': response,
            'tags': tags
        }
        self.responses.append(analysis)
        return analysis

    def get_historical_analysis(self):
        if not self.responses:
            return pd.DataFrame()
        return pd.DataFrame(self.responses)

    def export_analysis(self, format='csv'):
        df = self.get_historical_analysis()
        if df.empty:
            return None
        if format == 'csv':
            return df.to_csv(index=False)
        elif format == 'json':
            return df.to_json(orient='records')
        return None


class NewsScraper:

    def __init__(self):
        self.base_url = "https://newsapi.org/v2/everything"
        self.api_key = "014ff12200e04a4db0205d9c899e7fa6"  # Replace with your actual API key from NewsAPI
        self.headers = {"Content-Type": "application/json"}
        self.query_keywords = {
            'Australian superannuation cyberattack': [
                'superannuation', 'cyberattack', 'Australia', 'breach',
                'security', 'cyber'
            ],
            'SQL injection attack': [
                'SQL injection', 'database', 'vulnerability', 'security',
                'exploit', 'attack'
            ],
            'DaVita ransomware attack April 2025':
            ['DaVita', 'ransomware', 'attack', '2025', 'cyberattack'],
            'data breach 2025':
            ['data breach', '2025', 'security', 'cyberattack', 'leak', 'hack'],
            'AI in cybersecurity': [
                'AI', 'cybersecurity', 'machine learning', 'AI security',
                'cyber defense'
            ],
            'cloud security breaches': [
                'cloud security', 'breach', 'cloud', 'cyberattack',
                'vulnerability'
            ],
            'Phishing attack trends 2025':
            ['phishing', 'cyberattack', '2025', 'scam', 'fraud', 'security'],
            'Recent Cyberattack in Australia':
            ['Australia', 'cyberattack', 'data breach', 'security', 'hack'],
            'latest trends in hacking': [
                'hacking', 'cybersecurity', 'exploit', 'trend', 'security',
                'attack'
            ],
            'cybersecurity job market': [
                'cybersecurity', 'job market', 'security professionals',
                'cyber career', 'jobs'
            ]
        }

    def fetch_articles(self, query, page_size=5):
        params = {
            'q': query,
            'apiKey': self.api_key,
            'pageSize': page_size,
            'language': 'en',
            'sortBy': 'publishedAt'  # Sort by the most recent
        }
        try:
            response = requests.get(self.base_url,
                                    headers=self.headers,
                                    params=params)
            response.raise_for_status()
            data = response.json()
            print(
                f"Total results found for query '{query}': {data['totalResults']}"
            )  # Debugging line
            if data['status'] == 'ok' and data['totalResults'] > 0:
                return self.filter_relevant_articles(data['articles'], query)
            else:
                print(
                    f"No relevant articles found for the query '{query}'. Please try again later or refine the query."
                )
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def filter_relevant_articles(self, articles, query):
        relevant_articles = []
        keywords = self.query_keywords.get(
            query, [])  # Get predefined keywords for the query
        if not keywords:
            keywords = query.lower().split(
            )  # Use split query if no predefined keywords

        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()

            # Check if any of the keywords exist in the title or description
            if any(keyword in title
                   for keyword in keywords) or any(keyword in description
                                                   for keyword in keywords):
                relevant_articles.append(article)

        return relevant_articles

    def process_news_response(self, query):
        articles = self.fetch_articles(query)
        if articles:
            sorted_articles = sorted(articles,
                                     key=lambda x: x['publishedAt'],
                                     reverse=True)
            print(f"\nTop articles for '{query}':\n")
            for idx, article in enumerate(sorted_articles[:5], 1):
                title = article.get('title', 'No title available')
                author = article.get('author', 'Unknown author')
                description = article.get('description',
                                          'No description available')
                content = article.get('content', 'No content available')
                url = article.get('url', 'N/A')
                published_at = article.get('publishedAt', 'No date available')

                print(f"{idx}. {title}")
                print(f"   Author: {author}")
                print(f"   Published at: {published_at}")
                print(f"   Description: {description}")
                print(f"   Content: {content[:150]}..."
                      )  # Limiting content to first 150 chars for brevity
                print(f"   Read more: {url}\n")
        else:
            print(
                "No relevant articles found, please try again later or change the query.\n"
            )

    def start_scraper(self):
        print("Welcome to the real-time News Scraper!")
        print(
            "You can select a query from the options below by typing the corresponding number."
        )
        print("Type 'exit' to quit the program.\n")
        while True:
            print("1. Australian superannuation cyberattack")
            print("2. SQL injection attack")
            print("3. DaVita ransomware attack April 2025")
            print("4. Data breach 2025")
            print("5. AI in cybersecurity")
            print("6. Cloud security breaches")
            print("7. Phishing attack trends 2025")
            print("8. Recent Cyberattack in Australia")
            print("9. Latest trends in hacking")
            print("10. Cybersecurity job market")

            query_choice = input(
                "Enter a number (1-10) to select a query or type 'exit' to quit: "
            ).strip()

            if query_choice == 'exit':
                print("Exiting the program...")
                break

            query_dict = {
                '1': 'Australian superannuation cyberattack',
                '2': 'SQL injection attack',
                '3': 'DaVita ransomware attack April 2025',
                '4': 'data breach 2025',
                '5': 'AI in cybersecurity',
                '6': 'cloud security breaches',
                '7': 'Phishing attack trends 2025',
                '8': 'Recent Cyberattack in Australia',
                '9': 'latest trends in hacking',
                '10': 'cybersecurity job market'
            }

            if query_choice in query_dict:
                selected_query = query_dict[query_choice]
                self.process_news_response(selected_query)
            elif query_choice == '10':
                custom_query = input("\nEnter your custom query: ").strip()
                if custom_query:
                    self.process_news_response(custom_query)
                else:
                    print("Custom query cannot be empty. Please try again.\n")
            else:
                print("Invalid selection, please try again.\n")


if __name__ == "__main__":
    scraper = NewsScraper()
    scraper.start_scraper()
