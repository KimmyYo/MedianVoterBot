import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
# import random
from datetime import datetime, timedelta



class NewsScraper():
    def __init__(self) -> None:
        self.selenuim_waiting_time = 20 # 10 sec to load all data from the page
        self.browser = None

        # scrape last 24 hour news 
        self.current_time = datetime.now()
        self.scrape_time = 5

        self.media_info = pd.DataFrame({
            'Media': ['Ettoday', 'Yahoo', 'Public Television', 'UDN', 'ITN'],
            'URL': 
                ['https://www.ettoday.net/events/election2024/newslist-president.php7',
                 'https://tw.news.yahoo.com/topic/2024election/',
                 'https://news.pts.org.tw/hotTopic/108',
                 'https://udn.com/vote2024/rank/newest',
                 'https://news.ltn.com.tw/list/breakingnews/politics'
                ]
        })

        news_data_cols = ['Media', 'Headline', 'Datetime', 'URL', 'Content']
        self.news_data = pd.DataFrame(columns=news_data_cols)
    

    
    def selenuim_setup(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "prefs", {
                # block image loading
                "profile.managed_default_content_settings.images": 2,
            }
        )
        self.browser = webdriver.Chrome(
            options=options
        )
        self.browser.implicitly_wait(self.selenuim_waiting_time)

    def scrape(self, media_name, keyword=None):
        media_url = self.media_info.loc[self.media_info['Media'] == media_name, 'URL'].iloc[0]
        if media_name == 'Ettoday':
            self.scrape_ettoday(media_url, keyword=keyword)
        elif media_name == 'Yahoo':
            self.scrape_yahoo(media_url)
        elif media_name == 'UDN':
            self.scrape_udn(media_url)
    


    def datetime_parser(self, published_datetime, stoptime):
        # stop when datetime have a space in it 
        formatted_hour = ""
        print(f"stoptime: {stoptime}")
        # 11/30 15:30
        if stoptime in published_datetime:
            # detect 24 hours
            return "STOP"
        # 分鐘前
        elif published_datetime[-3:] == "分鐘前": 
            # only get the data befor -3 
            formatted_hour = round(float(published_datetime[:-3]) / 60, 1)
        # 小時前
        elif published_datetime[-3:] == "小時前":
            formatted_hour = float(published_datetime[:-3])
        
        return formatted_hour
    
    def push_ettoday_6_hours(self):
        stop_scraping = False
        while not stop_scraping:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            # part_pictxt_2 -> <a piece> -> pic, txt (h3, date)
            news_section = soup.find('div', class_='part_pictxt_2')
            news_a_tag_lists = news_section.find_all('a') # <a> tags list 
            for headline in news_a_tag_lists:
                if headline:  # <a><txt>(<h3><p>)
                    news_link = headline.get('href')
                    a_tag_inner = headline.find('div', class_='txt')
                    news_title = a_tag_inner.find('h3').text
                    news_datetime = a_tag_inner.find('p').text

                    news_datetime = self.datetime_parser(news_datetime, stoptime="6小時前")
                    
                    # detect left hours
                    if news_datetime == "STOP":
                        stop_scraping = True  # stop getting news 
                        break

                    # store data to df 
                    self.news_data.loc[len(self.news_data.index)] = \
                        {
                        'Media': 'Ettoday', 
                        'Headline': news_title, 
                        'URL': news_link,
                        'Datetime': news_datetime
                        }
                    
            if stop_scraping:
                break
            else: # next page 
                next_page_button = self.browser.find_element(By.CSS_SELECTOR, 'a.btn.next')
                next_page_button.click()

    def keyword_24_hours(self, keyword):
        stop_scraping = False
        while not stop_scraping:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            news_section = soup.find('div', class_='part_pictxt_2')
            news_a_tag_lists = news_section.find_all('a') # <a> tags list 
            for headline in news_a_tag_lists:
                if headline:  # <a><txt>(<h3><p>)
                    news_link = headline.get('href')
                    a_tag_inner = headline.find('div', class_='txt')
                    if keyword in a_tag_inner.find('h3').text:
                        news_title = a_tag_inner.find('h3').text
                        news_datetime = a_tag_inner.find('p').text

                        news_datetime = self.datetime_parser(news_datetime, stoptime=" ") # 2023/11/25 11:22 的 space
                        
                        # detect left hours
                        if news_datetime == "STOP":
                            stop_scraping = True  # stop getting news 
                            break
                        self.news_data.loc[len(self.news_data.index)] = \
                            {
                            'Media': 'Ettoday', 
                            'Headline': news_title, 
                            'URL': news_link,
                            'Datetime': news_datetime
                            }
                    else: 
                        continue
            if stop_scraping:
                break
            else: # next page 
                try: 
                    next_page_button = self.browser.find_element(By.CSS_SELECTOR, 'a.btn.next')
                    next_page_button.click()
                except selenium.common.exceptions.NoSuchElementException:
                    break


    def scrape_ettoday(self, media_url=None, keyword=None):

        self.selenuim_setup()
        self.browser.get(media_url)

        if keyword == None:
            self.push_ettoday_6_hours()
        else:
            self.keyword_24_hours(keyword)

        self.read_ettoday_article()
        self.browser.quit()
    
    def read_ettoday_article(self, news_link=None):
        if news_link == None:
            # read the article link in every row data
            for index, news_row in self.news_data.iterrows():
                self.browser.get(news_row.URL)
                soup = BeautifulSoup(self.browser.page_source, 'html.parser')
                # find article section 
                news_content_section = soup.find('div', class_='story')
                if news_content_section == None:
                    return
                news_content = news_content_section.find_all('p')
                news_content_data = ""
                for paragraph in news_content:
                    if "記者" in paragraph.text or "▲" in paragraph.text:
                        continue 
                    news_content_data += paragraph.text 

                self.news_data.at[index, 'Content'] = news_content_data

        else: # from user input
            self.browser.get(news_link)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            # find article section 
            news_content_section = soup.find('div', class_='story')
            news_content = news_content_section.find_all('p')
            news_content_data = ""
            for paragraph in news_content:
                if "記者" in paragraph.text or "▲" in paragraph.text:
                    continue 
                news_content_data += paragraph.text 
            
            return news_content_data

            

    def scrape_udn(self, media_url):
        self.selenuim_setup()
        self.browser.get(media_url)

        stop_scraping = False
        
        while not stop_scraping:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            news_section = soup.find_all('a', class_="story-list__news")
            for news in news_section:
                if not news:
                    stop_scraping = True
                    break
                news_link = news.get('href')
                news_title = news.find('h2').text
                print(news_title)
                try: 
                    news_datetime = news.find('time', class_="story-list__datetime").get('datetime')
                except:
                    print(self.news_data['URL'])
                    stop_scraping = True
                    break
                

                self.news_data.loc[len(self.news_data.index)] = \
                    {
                    'Media': 'udn', 
                    'Headline': news_title, 
                    'URL': news_link,
                    'Datetime': news_datetime
                    }
                
                if datetime.strptime(news_datetime, "%Y-%m-%d %H:%M") - datetime.now() >  timedelta(24):
                    stop_scraping = True
                    break

            if stop_scraping:
                break
            # else: # next page 
            #     next_page_button = self.browser.find_element(By.CSS_SELECTOR, 'button.btn.btn--more')
            #     next_page_button.click()

        
        self.read_udn_article()
    
    def read_udn_article(self):
        for index, news_row in self.news_data.iterrows():
            self.browser.get(news_row.URL)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            # find article section 
            news_content_section = soup.find('section', class_='article-content__editor')
            news_content = news_content_section.find_all('p')
            news_content_data = ""
            for paragraph in news_content:
                news_content_data += paragraph.text 

            self.news_data.at[index, 'Content'] = news_content_data


    def scrape_yahoo(self, media_url):
        self.selenuim_setup()
        self.browser.get(media_url)
        yahoo_news_count = 0
        stop_scraping = False
        
        while not stop_scraping:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            news_section = soup.find('div', class_='topic-story-list-new')
            news_section = news_section.find('ul', id="stream-container-scroll-template")
            if not news_section:
                self.browser.get(media_url)
                continue
            else:
                news_list = news_section.find_all('li')

            for news in news_list:
                news_a_tag = news.find('a')
                news_link = news_a_tag.get('href')
                news_title = news_a_tag.find('h3').text
                news_datetime = news_a_tag.find('div', class_='Fz(12px)').text
                self.news_data.loc[len(self.news_data.index)] = \
                    {
                    'Media': 'Yahoo', 
                    'Headline': news_title, 
                    'URL': news_link,
                    'Datetime': news_datetime
                    }
                yahoo_news_count += 1
                if yahoo_news_count > 25:
                    stop_scraping = True
                    break
            if stop_scraping == True:
                break
        self.read_yahoo_article()

    def read_yahoo_article(self):
        for index, news_row in self.news_data.iterrows():
            print("https://tw.news.yahoo.com/" + news_row.URL)
            self.browser.get("https://tw.news.yahoo.com/" + news_row.URL)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            if soup:
                # find article section 
                news_content_section = soup.find('div', class_='caas-body')
                news_content = news_content_section.find_all('p')
                news_content_data = ""
                for paragraph in news_content:
                    news_content_data += paragraph.text 

                news_row['Content'] = news_content_data
            else: 
                print("no soup")
                break




                
                

                    
           












                





        

