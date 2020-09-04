from playsound import playsound
from selenium import webdriver

DOMAIN_PCH24 = 'pch24.pl'


class AutoPress:
    urls = {
        'https://www.wykop.pl/hity/dnia': 4,
        'https://www.pch24.pl/wiadomosci,835,1,i.html': 6,
    }

    def __init__(self):
        self.driver = webdriver.Chrome(r'C:/webdriver/chromedriver.exe')

    def initialize(self):
        self.driver.maximize_window()

    def open_news_in_tabs(self):
        for url in self.urls:
            self.driver.get(url)
            news_number = self.urls[url]
            news_urls = self.find_news(url, news_number)

            for news_url in news_urls:
                self.open_link_in_tab(news_url)

        self.driver.close()
        self.ding()

    def open_link_in_tab(self, link_url):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(link_url)
        self.driver.switch_to.window(self.driver.window_handles[0])

    def find_news(self, url, news_number):
        if DOMAIN_PCH24 in url:
            news = self.explore_news_from_pch24(news_number)
        else:
            news = self.explore_news_from_wykop(news_number)

        return news

    def explore_news_from_pch24(self, news_number):
        best_news = {}
        self.close_pop_up_pch24()
        news_elements = self.driver.find_elements_by_class_name('TplWarto')

        for news_element in news_elements:
            link = f"{news_element.find_element_by_css_selector('div.TagTitle.mt10').find_element_by_tag_name('a').get_attribute('href')}"
            comments = 0
            likes = 0
            social_text = news_element.find_element_by_class_name('mt8').find_element_by_css_selector(
                'div.flLeft.SocialInfo.mt5').text

            if '' in social_text and '' in social_text:
                social_array = social_text.strip().split('\n')[1].split('\n')
                comments = int(social_array[0])
                likes = int(social_array[1].strip())

            best_news[link] = likes + comments * 2

        best_news = {k: v for k, v in sorted(best_news.items(), key=lambda item: item[1])}  # Sort in reverse order
        best_news = {k: best_news[k] for k in list(best_news)[-news_number:]}  # Slice only for desired news number

        return best_news

    def close_pop_up_pch24(self):
        self.driver.switch_to.frame(self.driver.find_element_by_class_name('fancybox-iframe'))
        self.driver.find_element_by_class_name('popup-newsletter__close').click()  # Closing pop-up
        self.driver.switch_to.default_content()

    def explore_news_from_wykop(self, news_number):
        best_news = {}
        news_elements = [e for e in self.driver.find_element_by_id('itemsStream').find_elements_by_tag_name('li') if 'link' in e.get_attribute('class')][:news_number]
        importance = 0

        for news_element in news_elements:
            wrapper_link = news_element.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute(
                'href')
            link = news_element.find_element_by_class_name('fix-tagline').find_elements_by_tag_name('span')[
                0].find_element_by_tag_name('a').get_attribute('href')
            print(f'Wykop link: {wrapper_link}')
            best_news[link] = importance
            importance += 1

        best_news = {k: v for k, v in
                     sorted(best_news.items(), key=lambda item: item[1], reverse=True)}  # Sort in reverse order

        return best_news

    def ding(self):
        playsound('ding.wav')


press = AutoPress()
press.initialize()
press.open_news_in_tabs()
