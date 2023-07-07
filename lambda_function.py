from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import re
from urllib.parse import urlencode
from urllib.request import urlopen, Request

def lambda_handler(event, context):

    # YOUR TWITTER WIDGET HERE
    URL = "https://hoge/twitter.php"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=880x996")
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.binary_location = "/opt/headless/python/bin/headless-chromium"
    browser = webdriver.Chrome(
        "/opt/headless/python/bin/chromedriver",
        options=options 
    )
    browser.implicitly_wait(10)
    browser.get(URL)

    a = browser.find_elements(By.CSS_SELECTOR,'iframe#twitter-widget-0')[0]
    browser.switch_to.frame(a)
    tweet_list = browser.find_elements(By.XPATH,'//html//section//article')
    tweet_array = []
    
    for each_tweet in tweet_list:
        post_data_set = {}
        content = each_tweet.find_elements(By.XPATH,'div//div//div//div//div[@data-testid="tweetText"]')[0].text
        times = each_tweet.find_elements(By.XPATH,'div//div//div//div//div//div//div//div//div//div//div//time')[0].get_attribute("datetime")
        data_date = datetime.datetime.strptime(times,"%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=9)

        each_tweet.click()
        browser.switch_to.window(browser.window_handles[-1])
        url = browser.current_url.split('?')[0]
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        browser.switch_to.frame(a)

        post_data_set.update({"data_date":data_date,"url":url,"data_content":content,"data_title":content})
        img_list = each_tweet.find_elements(By.XPATH,'div//div//div//div//div//div//div//div//div//div//div//img')

        for i in range(len(img_list)):
            if re.search("/media/",img_list[i].get_attribute("src")):
                image = img_list[i].get_attribute("src")
                post_data_set.update({"image_url":image})
                break

        tweet_array.append(post_data_set)
    browser.close()
    
# DEV: POST ONLY THE LATEST ONE MESSAGE
    line = tweet_array[0]
    
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "accept" :"application/json"
    }
    request = Request(url, headers=headers)
    data = {
        "token": "YOUR_SLACK_API_USER_OAUTH_TOKEN_HERE",
        "channel": "YOUR_SLACK_CHANNEL_NAME_HERE",
        "text": line["data_content"] + " " + line.get("url", "") + " " + line.get("image_url", ""),
    }
    data = urlencode(data).encode("utf-8")
    response = urlopen(request, data)
    
    return line["data_content"]
    