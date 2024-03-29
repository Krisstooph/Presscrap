from datetime import datetime
from urllib.request import urlopen, Request

import requests
from bs4 import BeautifulSoup

# TODO!


PRESSCRAP_VERSION = 'v.12'

urls = {
    'PCH24': 'https://www.pch24.pl',
    'WYKOP': 'https://www.wykop.pl',
    'WYKOP_HITS': 'https://www.wykop.pl/hity/tygodnia/',
    'MAGNA-POLONIA': 'https://www.magnapolonia.org',
    'MYSL-POLSKA': 'https://myslpolska.info',
    'INFO-DZIEN': 'https://pl.meteotrend.com/sunrise-sunset/pl/lodz/',
    'PIUS-X': 'https://www.piusx.org.pl/liturgia/kalendarz#dzis',
    'EWANGELIA': 'https://archibial.pl/czytania/',
    'YR': 'https://www.yr.no/en/forecast/hourly-table/2-3093133/Poland/%C5%81%C3%B3d%C5%BA%20Voivodeship/powiat%20%C5%81%C3%B3dzki%20Wschodni/Lodz?i=0',
    'PASAZER': 'https://www.pasazer.com',
    'AVHERALD': 'https://avherald.com/',
}

urls_to_open = {
    urls['PCH24']: 'https://pch24.pl/dzial/wiadomosci/',
    urls['WYKOP']: 'https://www.wykop.pl/hity/dnia',
    urls['WYKOP_HITS']: 'https://www.wykop.pl/hity/tygodnia/',
    urls['MAGNA-POLONIA']: 'https://www.magnapolonia.org/kategoria/wiadomosci',
    urls['MYSL-POLSKA']: 'https://myslpolska.info',
    urls['EWANGELIA']: 'https://archibial.pl/czytania/',
    urls[
        'YR']: 'https://www.yr.no/en/forecast/hourly-table/2-3102106/Poland/%C5%81%C3%B3d%C5%BA%20Voivodeship/Powiat%20%C5%82%C3%B3dzki%20wschodni/Bukowiec?i=0',
    urls['PASAZER']: 'https://www.pasazer.com/news',
    urls['AVHERALD']: 'https://avherald.com/',
    'DZIENNIK': 'https://wiadomosci.dziennik.pl/',
    'WYBORCZA': 'https://wiadomosci.gazeta.pl/wiadomosci/0,0.html',
    'ONET': 'https://wiadomosci.onet.pl/',
    'TVP_INFO': 'https://www.tvp.info',
    'WPOLITYCE': 'https://wpolityce.pl',
    'NIEZALEZNA': 'https://niezalezna.pl',
}

football_teams_urls = {
    'Polska': 'https://www.meczyki.pl/druzyna,polska,1677',
    'Real Madryt': 'https://www.meczyki.pl/druzyna,real-madryt,2016',
    'Widzew': 'https://www.meczyki.pl/druzyna,widzew-lodz,1658',
}

output_div_blocks = []
output_file = 'press.html'


def get_soup_from_page(page_url):
    req = Request(page_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'})
    page = urlopen(req)

    return BeautifulSoup(page, 'html.parser')


def prepare_article_div(article_title, article_header, article_url, article_color):
    return f'<div class="column" style="border-radius: 25px; border: 2px solid #999999; padding: 10px; margin: 0 5px 5px 0; float: left; width: 47%; background-color: #{article_color};"><a href="{article_url}" style="text-decoration: none;"><h2 style="text-align: center; font-family: Helvetica, sans-serif; color: black;">{article_title}</h2><p style="font-size: 20px; font-family: Arial, Helvetica, sans-serif; font-weight: bold; color: #555555;">{article_header}</p></a></div>'


def create_output_file():
    html_header = '<html><header><title>Prasówka</title></header><body>'
    html_end = '</body></html>'
    day_info_block = prepare_day_info_block()
    weather_block = prepare_weather()
    evangel_of_a_day_block = prepare_Evangel()
    saint_of_a_day_block = prepare_saint_block()
    next_matches_block = prepare_next_matches_block()
    left_news_block = prepare_left_news_block()
    semi_left_news_block = prepare_semi_left_news_block()
    aviation_news_block = prepare_aviation_news()
    file = open(output_file, 'w+', encoding='utf-8')
    file.write(html_header)
    file.write(day_info_block)
    file.write(weather_block)
    file.write(evangel_of_a_day_block)
    file.write(saint_of_a_day_block)
    file.write(next_matches_block)

    for index, out_div in enumerate(output_div_blocks):
        if index % 2 == 0:
            file.write('<div class="row">')
            file.write(out_div)
        else:
            file.write(out_div)
            file.write('</div>')

    file.write(semi_left_news_block)
    file.write(left_news_block)
    file.write(aviation_news_block)
    file.write(html_end)
    file.close()


def prepare_articles_pch24():
    articles_number = 6
    soup = get_soup_from_page(urls_to_open[urls['PCH24']])
    articles_divs = soup.find_all('div', attrs={'class': 'col-12'})[2:2 + articles_number]

    for article_div in articles_divs:
        list_a = article_div.find_all('a')[1]
        article_title = list_a.text.strip()
        article_url = list_a['href']
        article_header = get_article_header_for_pch24(article_url)
        article_color = "e0726e"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def write_articles_for_wykop(soup, articles_number, color):
    articles_divs = soup.find_all('section', attrs={'class': 'link-block'})[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('h2').find('a').text.strip() if article_div.find('h2') is not None else '---'

        if article_title == '---':
            continue

        article_header = article_div.find('div', attrs={'class': 'content'}).find('section', attrs={'class': 'info'}).find('a').text
        article_url = f'{urls["WYKOP"]}{article_div.find("h2").find("a")["href"]}'
        article_color = color
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_articles_wykop():
    articles_number = 4
    soup = get_soup_from_page(urls_to_open[urls['WYKOP']])
    write_articles_for_wykop(soup, articles_number, "99dae8")


def prepare_articles_wykop_hits():
    articles_number = 8
    soup = get_soup_from_page(urls_to_open[urls['WYKOP_HITS']])
    write_articles_for_wykop(soup, articles_number, "ccaaaa")


def prepare_articles_magna():
    articles_number = 4
    soup = get_soup_from_page(urls_to_open[urls['MAGNA-POLONIA']])
    articles_divs = soup.find_all('div', attrs={'class': 'archive-desc-wrapper clearfix'})[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('h2', attrs={'class': 'entry-title'}).text
        article_header = article_div.find('div', attrs={'class': 'entry-content'}).text
        article_url = article_div.find('h2', attrs={'class': 'entry-title'}).find('a')['href']
        article_color = "ede795"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_articles_mysl():
    articles_number = 2
    soup = get_soup_from_page(urls_to_open[urls['MYSL-POLSKA']])
    articles_divs = soup.find_all('div', attrs={'class': 'btSingleItemRow'})[0].find_all('header')[:articles_number]

    for article_div in articles_divs:
        article_title = article_div.find('a').text  # TODO! strip()?
        article_header = ''
        article_url = f"{article_div.find('a')['href']}"
        article_color = "ab7e96"
        output_article = prepare_article_div(article_title, article_header, article_url, article_color)
        output_div_blocks.append(output_article)


def prepare_day_info_block():
    soup = get_soup_from_page(urls['INFO-DZIEN'])
    info_block = \
        soup.find_all('div', attrs={'class': 'section detailed extable'})[0].find_all('a', attrs={'name': 'weather_1'})[
            0]
    text_date = info_block.find_all('h5', attrs={'class': 'b0'})[0].text
    text_sun_rise = info_block.find_all('b')[0].text
    text_sun_set = info_block.find_all('b')[2].text
    text_day_duration = info_block.find_all('b')[3].text
    text_time = datetime.now().strftime("%H:%M:%S")

    return f'<p style="font-size: 10px; margin-bottom: -20px;">{PRESSCRAP_VERSION}</p><div style="font-family: Tahoma;"><h1>Dziś jest {text_date}</h1><h2>{text_time}</h2><p>Wschód słońca: <b>{text_sun_rise}</b></p><p>Zachód słońca: <b>{text_sun_set}</b></p><p>Dzień trwa: <b>{text_day_duration}</b> godzin</p></div>'


def prepare_saint_block():
    soup = get_soup_from_page(urls['PIUS-X'])
    saint_day = soup.find_all('li', attrs={'id': 'dzis'})[0]
    saint_name = str(saint_day.contents[1])
    saint_name_ascii = get_saint_name(saint_name)
    saint_class = saint_day.find_all('span')[1].text
    soup = get_soup_from_page(f'https://pl.wikipedia.org/w/index.php?sort=relevance&search={saint_name_ascii}')
    saint_short_info = soup.find_all('li')[4].text
    saint_page = soup.find_all('li')[4].find_all('a')[0]['href'] if len(
        soup.find_all('li')[4].find_all('a')) > 0 else ''
    saint_url = f"https://pl.wikipedia.org/{saint_page}"

    return f'<hr><div><h3>Święto: {saint_name}<p>Klasa: {saint_class}</p></h3><a href={saint_url}>{saint_short_info}</a></div><hr></br>'


def get_rid_of_non_ascii_chars(saint_name):
    return saint_name.lower().replace('ą', 'a').replace('ę', 'e').replace('ł', 'l').replace('ó', 'o').replace('ś',
                                                                                                              's').replace(
        'ż', 'z').replace('ź', 'z').replace('ć', 'c').replace('ń', 'n').replace(' ', '%20')


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
        next_match_text = soup.find_all('tr', attrs={'class': 'stacked'})[5].text.strip()
        next_next_match_text = soup.find_all('tr', attrs={'class': 'stacked'})[6].text.strip()
        next_match_data = next_match_text.split('\n')
        next_next_match_data = next_next_match_text.split('\n')
        first_next_date = next_match_data[0] if len(next_match_data) > 0 else 'Brak informacji'
        first_match_info = next_match_data[1].strip() if len(next_match_data) > 1 else ''
        second_next_date = next_next_match_data[0] if len(next_next_match_data) > 0 else 'Brak informacji'
        second_match_info = next_next_match_data[1].strip() if len(next_next_match_data) > 1 else ''
        html += f'<p>{first_next_date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{first_match_info}</p><p>{second_next_date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{second_match_info}</p>'

    html += f'<h3><a href="https://www.flashscore.pl/pilka-nozna/hiszpania/laliga/tabela/"><b>La Liga</b></a>&nbsp;&nbsp;&nbsp;<a href="https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa/tabela/"><b>1 Liga Polska</b></a></h3>'

    return html


def prepare_left_news_block():
    html = ''
    articles_number = 3

    soup = get_soup_from_page(urls_to_open['DZIENNIK'])
    article_list = soup.find_all('ul', attrs={'class': 'topicList'})[3].find_all('li')[:articles_number]
    html += '<h7 style="font-size: 11px;"><b>dziennik</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = article.find('a')['href']

        html += f'<li><a href="{url}">{title}</a></li>'

    soup = get_soup_from_page(urls_to_open['ONET'])
    article_list = soup.find_all('ul', attrs={'class': 'topicList'})[0].find_all('a')[:articles_number]
    html += '<h7 style="font-size: 11px;"><b>onet</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = article['href']

        html += f'<li><a href="{url}">{title}</a></li>'

    soup = get_soup_from_page(urls_to_open['WYBORCZA'])
    article_list = soup.find_all('li', attrs={'class': 'newsBox__item'})[:articles_number]
    html += '<h7 style="font-size: 11px;"><b>wyborcza</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = article.find('a')['href']

        html += f'<li><a href="{url}">{title}</a></li>'

    html += '</ul>'

    return html


def prepare_semi_left_news_block():
    html = '<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><hr><hr><br><br><ul style="font-family: Tahoma; font-size: 18px;">'
    articles_number = 3

    soup = get_soup_from_page(urls_to_open['TVP_INFO'])
    article_list = soup.find_all('div', attrs={'class': 'news__container'})[1].find_all('div', attrs={'class': 'news__item'})[:articles_number]
    html += '<h7 style="font-size: 11px;"><b>tvp info</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = f'{urls_to_open["TVP_INFO"]}{article.find("a")["href"]}'

        html += f'<li><a href="{url}">{title}</a></li>'

    soup = get_soup_from_page(urls_to_open['WPOLITYCE'])
    all_articles_on_page = soup.find_all('article', attrs={'class': 'tile'})
    articles_and_comments = {}

    for single_article in all_articles_on_page:
        if len(single_article.find_all('span')) == 4:
            articles_and_comments[single_article] = int(single_article.find_all('span')[1].text)

    article_list = list(dict(sorted(articles_and_comments.items(), key=lambda item: item[1], reverse=True)).keys())[:articles_number]

    html += '<h7 style="font-size: 11px;"><b>wPolityce</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = f'{urls_to_open["WPOLITYCE"]}{article.find("a")["href"]}'

        html += f'<li><a href="{url}">{title}</a></li>'

    soup = get_soup_from_page(urls_to_open['NIEZALEZNA'])
    article_list = soup.find_all('div', attrs={'class': 'col'})[1].find_all('div', attrs={'class': 'item-news'})[:articles_number]
    html += '<h7 style="font-size: 11px;"><b>niezależna</b></h7>'

    for article in article_list:
        title = article.text.strip()
        url = f'{urls_to_open["NIEZALEZNA"]}{article.find("a")["href"]}'

        html += f'<li><a href="{url}">{title}</a></li>'

    return html


def prepare_Evangel():
    html = '<hr><h3>Ewangelia:</h3>'

    try:
        soup = get_soup_from_page(urls['EWANGELIA'])
        evangel = \
            soup.find_all('div', attrs={'class': 'czytania'})[0].text.split('EWANGELIA')[1].split(
                'Medytacja nad Słowem')[
                0].strip()
        evangel = evangel.replace('\r', ' ')
        text_temp_first = evangel.split('\n\n')

        if len(text_temp_first) <= 3:
            text_temp_first = evangel.split('\n')

        text_temp = []

        for txt in text_temp_first:
            if txt:
                text_temp.append(txt)

        siglum_and_title = text_temp[0].strip() + ' ' + text_temp[1].strip()
        header = text_temp[2].strip()
        text = ''

        for txt in text_temp[3:-1]:
            text += txt

        html += f'<div>' \
                f'<h4>{siglum_and_title}</h4>' \
                f'<b>{header}</b>' \
                f'<p style="font-family: Tahoma;">{text}</p>' \
                f'<p style="font-family: Tahoma;"><i>{text_temp[-1].strip()}</i></p>' \
                f'</div>'
    except:
        print('Problem with getting Evangel of a day...')

    return html


def prepare_weather():
    style_table_th_td = 'style="border: 1px solid black; text-align: center;"'
    html = f'<h3>Pogoda</h3><table {style_table_th_td}"><thead><tr>' \
           f'<th {style_table_th_td}>Godzina</th>' \
           f'<th {style_table_th_td}>Pogoda</th>' \
           f'<th {style_table_th_td}>Temperatura</th>' \
           f'<th {style_table_th_td}>Opady [mm]</th>' \
           f'<th {style_table_th_td}>Wiatr [m/s]</th>' \
           f'</tr></thead><tbody>'
    soup = get_soup_from_page(urls['YR'])
    trs = soup.find_all('div', attrs={'class': 'fluid-table'})[0].find('tbody').find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')

        html += f'<tr>' \
                f'<td {style_table_th_td}>{tds[0].text}</td>' \
                f'<td {style_table_th_td}>{tds[1].text}</td>' \
                f'<td {style_table_th_td}>{tds[2].text.replace("Temperature", "")}</td>' \
                f'<td {style_table_th_td}>{tds[3].text}</td>' \
                f'<td {style_table_th_td}>{tds[4].text[:-2]}</td>' \
                f'</tr>'

    html += '</tbody></table>'

    return html


def get_aviation_crash_info():
    html = ''
    headers = {'accept': '*/*',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,la;q=0.6',
               'cache-control': 'no-cache',
               'dnt': '1',
               'pragma': 'no-cache',
               'referer': 'https',
               'sec-fetch-mode': 'no-cors',
               'sec-fetch-site': 'cross-site',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
               }

    URL = "https://avherald.com/"

    response = requests.get(url=URL, headers=headers, verify=False)
    crashes = response.text.split('crash.gif')

    if len(crashes) > 2:
        html += '<div><br><h3 style="font-family: Tahoma;">KATASTROFY</h3><ul style="font-family: Tahoma;">'

        for crash in crashes[2:]:
            header = crash.split('span')[:2][1].split('>')[1][:-2]
            link = crash.split('span')[:2][0].split('href=\"')[1].split('"')[0]
            html += f'<li>' \
                    f'<a href={urls["AVHERALD"]}{link}><b>{header}</b></a>' \
                    f'</li>'

        html += '</ul></div>'

    return html


def prepare_aviation_news():
    html = get_aviation_crash_info()
    html += '<div><br><h3 style="font-family: Tahoma;">Lotnictwo</h3><ul style="font-family: Tahoma; font-size: 18px;">'
    soup = get_soup_from_page(urls_to_open[urls['PASAZER']])
    sections = soup.find('div', attrs={'class': 'content_def'}).find_all_next('section')[:-13]

    for section in sections:
        header = section.find('strong').text.strip()
        text = section.find('a').text.strip().split('\n')[-1].strip()
        link = f'{urls["PASAZER"]}{section.find("a")["href"]}'

        html += '<li>' \
                f'<a href={link}><b>{header}</b></a>' \
                f'<p>{text}</p>' \
                '</li>'

    html += '</ul></div>'

    return html


def get_article_header_for_pch24(article_url):
    soup = get_soup_from_page(article_url)
    article_paragraphs = soup.find('article', attrs={'class': 'pch-article'}).find_all_next('p')

    if len(article_paragraphs[0].text.split('\n')) == 1:
        return f'{article_paragraphs[1].text}</br></br>{article_paragraphs[2].text}'
    else:
        header = article_paragraphs[0].text.split('\n')[:3]

        return f'{header[0]}</br></br>{header[2]}'


functions_to_call = {
    urls['PCH24']: prepare_articles_pch24,
    urls['MAGNA-POLONIA']: prepare_articles_magna,
    urls['WYKOP_HITS']: prepare_articles_wykop_hits,
    urls['WYKOP']: prepare_articles_wykop,
    urls['MYSL-POLSKA']: prepare_articles_mysl,
}

for function in functions_to_call:
    try:
        functions_to_call[function]()
    except:
        print(f'Failed to load: {function}')

create_output_file()
