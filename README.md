# MedianVoterBot

MedianVoterBot is a Telegram bot designed to deliver timely and relevant political news from Taiwan. Utilizing Python, Flask, and Selenium, this bot scrapes news websites, filters content based on keywords, and performs sentiment analysis on mentions of political candidates.

## Features

- **News Scraping**: Automatically gathers news articles from various sources using Selenium.
- **Keyword-Based Filtering**: Filters news articles to focus specifically on Taiwan's political news.
- **Sentiment Analysis**: Analyzes the sentiment of news content and mentions of political candidates using the SnowNLP and jieba modules.
- **Interactive Telegram Bot**: Delivers filtered and analyzed news directly to users on Telegram.

## Technology Stack

- **Python**: Core programming language.
- **Flask**: Web framework used to create the bot server.
- **Selenium**: Web scraping tool to extract news articles.
- **SnowNLP**: Python library for Chinese natural language processing, used for sentiment analysis.
- **jieba**: Chinese text segmentation module, used for keyword extraction and analysis.
- **Telegram Bot API**: Interface for integrating the bot with Telegram.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/MedianVoterBot.git
    cd MedianVoterBot
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the project root.
    - Add your Telegram bot token and any other necessary configuration variables:
    ```sh
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    ```

5. **Run the Flask server**:
    ```sh
    python app.py
    ```

## Usage

1. **Start the bot**:
    - Open your Telegram app.
    - Search for your bot using the bot username.
    - Start a conversation with the bot to receive news updates.

2. **Commands**:
    - `/start`: Initiate interaction with the bot.
    - `/help`: Get a list of available commands.
    - `/news`: Receive the latest filtered political news.
    - `/sentiment [candidate_name]`: Get sentiment analysis on mentions of a specific candidate.
