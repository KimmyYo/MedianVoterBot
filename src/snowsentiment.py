from snownlp import SnowNLP, normal
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import jieba

class SentimentAnalyzer():
    def __init__(self, news_data) -> None:

        self.keywords = {
            "綠": ['賴清德', '蕭美琴', '蔡英文', '綠', '民進黨', '賴蕭'],
            "藍": ['侯友宜', '趙少康', '朱立倫', '藍', '國民黨', '侯趙'],
            "白": ['柯文哲', '吳欣盈', '黃國昌', '白', '民眾黨', '柯吳'],
            "黃": ['時代力量', '時力']
        }
        # not in keywords -> set to 灰 
        self.news_data = news_data

    def sentiment_analysis(self, headline, article):
        head_s = SnowNLP(headline)
        if isinstance(article, float):
            article = str(article)

        article_s = SnowNLP(article)
        sum_of_article = 0
        for sentence in article_s.sentences:
            sum_of_article += SnowNLP(sentence).sentiments

        mean_sentiment = sum_of_article / len(article_s.sentences)

        return round(head_s.sentiments, 10), round(mean_sentiment, 5), article_s.summary()

    def sentiment_score(self, data):
        article_s = SnowNLP(data)
        sum_of_article = 0
        for sentence in article_s.sentences:
            sum_of_article += SnowNLP(sentence).sentiments

        mean_sentiment = sum_of_article / len(article_s.sentences)

        return round(mean_sentiment, 5)
    
    def sentiment_score_labeling(self, score):
        if score >= 0.6: return "Positive"
        elif score <= 0.4: return "Negative"
        else: return "Neutral"  

    def article_analysis(self):
        # TODO 1. Loop through each article for Sentiment Analysis
        # TODO 2. Separate articles based on Candidates -> Add to columns
        summary_list = []
        for news_idx, news_row_values in self.news_data.iterrows():
            news_related_color = self.define_keyword(news_row_values)
            self.news_data.loc[news_idx, 'Color'] = news_related_color

            # TODO 3. Sentiment Score, Summary -> Add to news_data df
            score, article_score, summary = self.sentiment_analysis(news_row_values['Headline'], news_row_values['Content'])
            
            # sentiment score analysis 
            score_label = self.sentiment_score_labeling(score)
            self.news_data.loc[news_idx, 'Headline Sentiment'] = round(score, 4)
            self.news_data.loc[news_idx, 'Article Sentiment'] = round(article_score, 4)
            self.news_data.loc[news_idx, 'Sentiment Label'] = score_label # from content counts
           
 
            # summary processing
            summary_list.append(summary)
            
         
        self.news_data['Summary'] = summary_list
        # TODO 4. Create line graph for each color sentiment score 
        # TODO 5. Create Word Cloud for each color for today 

        return self.news_data
    
    def define_keyword(self, news):
        # [0] as status [1] as num of keywors appear 
        color_status_and_counts = {
            '綠': [0, 0],
            '藍': [0, 0], 
            '白': [0, 0],
            '黃': [0, 0]
        }
        if isinstance(news, pd.Series):
            news_content = news['Content']
        else:
            news_content = news
        print(type(news_content))
        # check keyword exist in article or not s
        for color, keywords in self.keywords.items():
            if any(keyword in news_content for keyword in keywords):
                color_status_and_counts[color][0] = 1
        
        color_status = sum(item[0] for item in color_status_and_counts.values())
        # if both or three colors appear in the same article 
        
        if  color_status > 1: 
            # check the amount of time a keyword is found in the article 
            for color, status_and_counts in color_status_and_counts.items():
                keywords = self.keywords[color]
                color_status_and_counts[color][1] = sum(news_content.count(keyword) for keyword in keywords)
            # decide the most common color as the color related of the article 
            news_related_color = max(color_status_and_counts, key=lambda k: color_status_and_counts[k][1])

            print(color_status_and_counts, news_related_color)
        # if not, directly assign the color 
        elif color_status == 1:
            news_related_color = [key for key, value in color_status_and_counts.items() if value[0] == 1][0]
        elif color_status == 0:
            news_related_color = "其他"

        # set the keyword correponsed color 
        return news_related_color

   



        
       

        

    