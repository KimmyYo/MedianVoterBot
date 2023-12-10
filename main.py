from flask import Flask, request, Response
from telegram import Bot, Update
from telegram.ext import MessageHandler, CallbackContext, Updater, CommandHandler, Dispatcher, Filters
import requests
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from newsscrape import NewsScraper 
from snowsentiment import SentimentAnalyzer
from wordcloud import WordCloud
import base64
from io import BytesIO
import os

TOKEN = os.environ['TOKEN']
FORWARD = "medianvoterbot-production.up.railway.app"
BASE_URL =  f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_URL = f"{BASE_URL}/setwebhook?url={FORWARD}"
MESSAGE_URL = f"{BASE_URL}/sendMessage"

CHAT_ID = 5827677676

app = Flask(__name__)
bot = Bot(token=TOKEN)
news_scraper = NewsScraper()
scheduler = BackgroundScheduler()



# News to send
def separate_parties_news(news_data): 
    # group the message by party 
    green_news = news_data[news_data['Color'] == "綠"]
    blue_news = news_data[news_data['Color'] == "藍"]
    white_news = news_data[news_data['Color'] == "白"]

    return [green_news, blue_news, white_news]

def create_send_message(news_data_list_by_parties):
    # Headline - Media - Datetime 
    # Link
    message_by_parties = {
        '綠': [],
        '藍': [],
        '白': []
    }

    for party_news in news_data_list_by_parties:
        # party_news is a dataframe dictionary
        if len(party_news.index) == 0:
            continue
        
        party_message = message_by_parties[party_news['Color'].iloc[0]]

        for idx, news in party_news.iterrows():
            message = f"「{news['Headline']}」- {news['Media']} - {news['Datetime']}小時前 \n" 
            message += news['URL'] + "\n"
            message += '，'.join(news['Summary'])
            message += "。\n"

            party_message.append(message)

    return message_by_parties


def dataCollect(): 
    news_scraper.scrape("Ettoday")
    s_analyze = SentimentAnalyzer(news_scraper.news_data)
    updated_news_data = s_analyze.article_analysis()
    updated_news_data.to_csv('NewsData.csv', index=False)
    news_data_by_parties = separate_parties_news(updated_news_data)
    message_to_send_by_parties = create_send_message(news_data_by_parties)
    return message_to_send_by_parties


def send_daily_news():
    message_to_send_by_parties = dataCollect()
    # Send the scraped data as a message to Telegram
    for key, value in message_to_send_by_parties.items():
        one_party_message = "\n\n".join(value)
        sendMessage(CHAT_ID, f"{key}色的新聞 近六小時")
        sendMessage(CHAT_ID, one_party_message)

# scheduler.add_job(send_daily_news, trigger=CronTrigger(hour=18, minute=22, second=0), id='daily_news_job')
# scheduler.start()


# WordCloud Send (by parties)
# Telegram bot manage part 
def sendMessage(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(MESSAGE_URL, json=payload)
    return r

@app.route('/', methods=['POST', 'GET'])
def index():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return 'Ｗebhook Connected', 200
    
@app.route('/send_daily_news', methods=['GET'])
def send_daily_news_endpoint():
    # Trigger the scheduled task manually
    send_daily_news()
    return "Daily News sent successfully!"

def get_user_info(update):
    user_id = update.message.from_user.id
    user_username = update.message.from_user.username
    return user_id, user_username

def start(update: Update, context: CallbackContext):
    user_id, username = get_user_info(update)
    update.message.reply_text(f"您好，中間選民 {username}，我是你的選舉新聞推播機器人。\n- 每日18點都會推一日各政黨新聞給你\n- 輸入新聞文章內容進行情感分析 /sentiment \n- 整理您輸入關鍵字的相關新聞 /keyword")


def sentiment(update: Update, context: CallbackContext):
    update.message.reply_text("請輸入Ettoday新聞連結")
    context.user_data['command'] = 'sentiment'

def user_keyword(update: Update, context: CallbackContext):
    update.message.reply_text("請輸入關鍵字，我將會爬24個小時內的新聞，並提供關鍵字數量給你，以及其相關文章的情感分析總結。這需要一點時間，請去喝茶。")
    context.user_data['command'] = 'keyword'

def handle_user_input_command(update: Update, context: CallbackContext):
    text = update.message.text

    # Check the command in the custom state
    command = context.user_data.get('command')
    if command == "sentiment":
        news_related_keyword, sentiment_label, sentiment_score = analyze_sentiment(input_text=text)
        update.message.reply_text(f"這是一篇關於{news_related_keyword}的文章，情感分析結果為：{sentiment_label}，{sentiment_score}。")

    elif command == "keyword":
        user_keyword, keyword_label, average_keyword_sentiment, img_buffer = get_keyword_information(input_text=text)
        if keyword_label == None and average_keyword_sentiment == None and img_buffer == None:
            update.message.reply_text(f"今天沒有{user_keyword}的相關消息喔QQ")

        update.message.reply_text(f"Average Sentiment of {user_keyword} is {keyword_label}, {average_keyword_sentiment}")
        update.message.reply_photo(photo=img_buffer)
    else:
        update.message.reply_text("Hey，找一個命令來執行唄～")
    context.user_data.pop('command', None)


def analyze_sentiment(input_text):
        news_url = input_text
        news_scraper.selenuim_setup()
        news_data = news_scraper.read_ettoday_article(news_link=news_url)
        sentiment_analyzer = SentimentAnalyzer(news_data)
        sentiment_score = sentiment_analyzer.sentiment_score(news_data)
        sentiment_label = sentiment_analyzer.sentiment_score_labeling(sentiment_score)
        news_related_keyword = sentiment_analyzer.define_keyword(news_data)
        return news_related_keyword, sentiment_label, sentiment_score
        



def get_keyword_information(input_text):
        user_keyword = input_text
        news_scraper.scrape('Ettoday', keyword=user_keyword)
        news_data = news_scraper.news_data # after article is read
        news_scraper.browser.quit()
        if news_data.all() is not None:
            sentiment_analyzer = SentimentAnalyzer(news_data)
            print(news_data) 
            # put every news content to sentiment score and sentiment label 
            analyze_data = sentiment_analyzer.article_analysis()

            average_keyword_sentiment = round(sum(analyze_data['Article Sentiment']) / len(analyze_data['Article Sentiment'].index), 4)
            keyword_label = sentiment_analyzer.sentiment_score_labeling(average_keyword_sentiment)

            all_article_text = " ".join(analyze_data['Content'])

            font_path = "font.ttf"
            wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(all_article_text)
            img_buffer = BytesIO()
            wordcloud.to_image().save(img_buffer, format='PNG')
            img_buffer.seek(0)
        else: 
            keyword_label = None
            average_keyword_sentiment = None
            img_buffer = None

        return user_keyword, keyword_label, average_keyword_sentiment, img_buffer
        


# Handler Setup
dp = Dispatcher(bot, None)
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("sentiment", sentiment))
dp.add_handler(CommandHandler('keyword', user_keyword))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input_command))


if __name__ == '__main__':
   port = int(os.environ.get("PORT", 5000))
   app.run(host="0.0.0.0", port=port)
