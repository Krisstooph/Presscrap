from datetime import datetime
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

urls = {
    'PCH24': 'https://www.pch24.pl',
    'WYKOP': 'https://www.wykop.pl',
    'MAGNA-POLONIA': 'https://www.magnapolonia.org',
    'MYSL-POLSKA': 'http://mysl-polska.pl',
    'INFO-DZIEN': 'https://pl.meteotrend.com/sunrise-sunset/pl/lodz/',
    'PIUS-X': 'https://www.piusx.org.pl/liturgia/kalendarz#dzis',
}

urls_to_open = {
    urls['PCH24']: 'https://www.pch24.pl/wiadomosci,835,1,i.html',
    urls['WYKOP']: 'https://www.wykop.pl/hity/dnia',
    urls['MAGNA-POLONIA']: 'https://www.magnapolonia.org/kategoria/wiadomosci',
    urls['MYSL-POLSKA']: 'http://mysl-polska.pl',
}

football_teams_urls = {
    'Polska': 'https://sportowefakty.wp.pl/pilka-nozna/polska/terminarz',
    'Real Madryt': 'https://sportowefakty.wp.pl/pilka-nozna/real-madryt/terminarz',
    'Widzew': 'https://sportowefakty.wp.pl/pilka-nozna/widzew-lodz/terminarz',
}

output_div_blocks = []
output_file = 'press.html'


def get_soup_from_page(page_url):
    req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req)

    return BeautifulSoup(page, 'html.parser')


def prepare_article_div(article_title, article_header, article_url, article_color):
    return f'<div class="column" style="border-radius: 25px; border: 2px solid #999999; padding: 10px; margin: 0 5px 5px 0; float: left; width: 47%; background-color: #{article_color};"><a href="{article_url}" style="text-decoration: none;"><h2 style="text-align: center; font-family: Helvetica, sans-serif; color: black;">{article_title}</h2><p style="font-size: 20px; font-family: Arial, Helvetica, sans-serif; font-weight: bold; color: #555555;">{article_header}</p></a></div>'


def create_output_file():
    html_header = '<html><header><title>Prasówka</title></header><body>'
    html_end = '</body></html>'
    day_info_block = prepare_day_info_block()
    saint_of_a_day_block = prepare_saint_block()
    next_matches_block = prepare_next_matches_block()
    file = open(output_file, 'w+', encoding='utf-8')
    file.write(html_header)
    file.write(day_info_block)
    file.write(saint_of_a_day_block)
    file.write(next_matches_block)

    for index, out_div in enumerate(output_div_blocks):
        if index % 2 == 0:
            file.write('<div class="row">')
            file.write(out_div)
        else:
            file.write(out_div)
            file.write('</div>')

    file.write(html_end)
    file.close()


def prepare_articles_pch24():
    articles_number = 6
    soup = get_soup_from_page(urls_to_open[urls['PCH24']])
    articles_divs = soup.find_all('div', attrs={'class': 'TplWarto'})
    best_articles = {}

    for article_div in articles_divs:
        list_a = article_div.findChildren('a', recursive=True)
        article_title = article_div.findChildren('div', attrs={'class': 'TagTitle mt10'})[0].text
        article_header = article_div.find('p').text if article_div.find('p') else ''
        article_url = f"{urls['PCH24']}{list_a[0]['href']}"
        article_color = "bb7777"
        comments = 0
        likes = 0
        social_text = article_div.findChildren('div', attrs={'class': 'flLeft SocialInfo mt5'}, recursive=True)[0].text

        if '' in social_text and '' in social_text:
            social_array = social_text.strip().split('\n')[1].split('\n')
            comments = int(social_array[0])
            likes = int(social_array[1].strip())

        best_articles[article_url] = (likes + comments * 2, article_title, article_header)

    best_articles = {k: v for k, v in sorted(best_articles.items(), key=lambda item: item[1])}
    best_articles = {k: best_articles[k] for k in list(best_articles)[-articles_number:]}

    for article_url in best_articles:
        output_article = prepare_article_div(best_articles[article_url][1], best_articles[article_url][2], article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_articles_wykop():
    articles_number = 4
    soup = get_soup_from_page(urls_to_open[urls['WYKOP']])
    articles_divs = soup.find('ul', attrs={'id': 'itemsStream'}).find_all('li', attrs={'class': 'link'})[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('h2').find('a')['title'] if article_div.find('h2') is not None else '---'

        if article_title == '---':
            continue

        article_header = article_div.find('p', attrs={'class': 'text'}).text
        article_url = article_div.find_all('a', attrs={'class': 'affect'})[1]['href']
        article_color = "7777cc"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_articles_magna():
    articles_number = 2
    soup = get_soup_from_page(urls_to_open[urls['MAGNA-POLONIA']])
    articles_divs = soup.find_all('div', attrs={'class': 'archive-desc-wrapper clearfix'})[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('h2', attrs={'class': 'entry-title'}).text
        article_header = article_div.find('div', attrs={'class': 'entry-content'}).text
        article_url = article_div.find('h2', attrs={'class': 'entry-title'}).find('a')['href']
        article_color = "FFC462"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_articles_mysl():
    articles_number = 2
    soup = get_soup_from_page(urls_to_open[urls['MYSL-POLSKA']])
    articles_divs = soup.find_all('div', attrs={'class': 'content'})[1].find_all('div', attrs={'class': 'node'}, recursive=False)[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('h2').text  # TODO! strip()?
        article_header = article_div.find('strong').text
        article_url = f"{urls['MYSL-POLSKA']}{article_div.find('h2').find('a')['href']}"
        article_color = "B06D9B"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_day_info_block():
    soup = get_soup_from_page(urls['INFO-DZIEN'])
    info_block = soup.find_all('div', attrs={'class': 'section detailed extable'})[0].find_all('a', attrs={'name': 'weather_1'})[0]
    text_date = info_block.find_all('h5', attrs={'class': 'b0'})[0].text
    text_sun_rise = info_block.find_all('b')[0].text
    text_sun_set = info_block.find_all('b')[2].text
    text_day_duration = info_block.find_all('b')[3].text
    text_time = datetime.now().strftime("%H:%M:%S")

    return f'<div><h1>Dziś jest {text_date}</h1><h2>{text_time}</h2><p>Wschód słońca: <b>{text_sun_rise}</b></p><p>Zachód słońca: <b>{text_sun_set}</b></p><p>Dzień trwa: <b>{text_day_duration}</b> godzin</p></div>'


def prepare_saint_block():
    soup = get_soup_from_page(urls['PIUS-X'])
    saint_day = soup.find_all('li', attrs={'id': 'dzis'})[0]
    saint_name = str(saint_day.contents[1])
    saint_name_ascii = get_saint_name(saint_name)
    saint_class = saint_day.find_all('span')[1].text
    soup = get_soup_from_page(f'https://pl.wikipedia.org/w/index.php?sort=relevance&search={saint_name_ascii}')
    saint_short_info = soup.find_all('li')[4].text
    saint_page = soup.find_all('li')[4].find_all('a')[0]['href'] if len(soup.find_all('li')[4].find_all('a')) > 0 else ''
    saint_url = f"https://pl.wikipedia.org/{saint_page}"

    return f'<hr><div><h3>Święto: {saint_name}<p>Klasa: {saint_class}</p></h3><a href={saint_url}>{saint_short_info}</a></div><hr></br>'


def get_rid_of_non_ascii_chars(saint_name):
    return saint_name.lower().replace('ą', 'a').replace('ę', 'e').replace('ł', 'l').replace('ó', 'o').replace('ś', 's').replace('ż', 'z').replace('ź', 'z').replace('ć', 'c').replace('ń', 'n').replace(' ', '%20')


def get_saint_name(saint_info):
    saint_name = ''
    infos = saint_info.split(',')

    if len(infos) > 1:
        saint_name = infos[0].strip()
        saint_name = get_rid_of_non_ascii_chars(saint_name)

    return saint_name


def prepare_next_matches_block():
    html = '<h3>Najbliższe mecze:</h3>'

    for current_team in football_teams_urls:
        html += f'<h4>{current_team}</h4>'
        soup = get_soup_from_page(football_teams_urls[current_team])
        calendar = soup.find_all('div', attrs={'id': 'calendarMatches'})[0]
        divs = calendar.find_all('div', attrs={'class': 'cmatch cmatch--inactive'})
        headers = calendar.find_all('header')[-len(divs):]
        first_next_date = headers[0].text.strip()
        first_match_info = divs[0].text.strip().replace('\n\n', ' ').replace('relacja', '')
        second_next_date = headers[1].text.strip()
        second_match_info = divs[1].text.strip().replace('\n\n', ' ').replace('relacja', '')
        html += f'<p>{first_next_date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{first_match_info}</p><p>{second_next_date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{second_match_info}</p>'

    html += f'<h3><a href="https://www.flashscore.pl/pilka-nozna/hiszpania/laliga/tabela/"><b>La Liga</b></a>&nbsp;&nbsp;&nbsp;<a href="https://www.flashscore.pl/pilka-nozna/polska/fortuna-1-liga/tabela/"><b>1 Liga Polska</b></a></h3>'

    return html

functions_to_call = {
    urls['PCH24']: prepare_articles_pch24,
    urls['WYKOP']: prepare_articles_wykop,
    urls['MAGNA-POLONIA']: prepare_articles_magna,
    urls['MYSL-POLSKA']: prepare_articles_mysl,
}

for function in functions_to_call:
    functions_to_call[function]()

create_output_file()
