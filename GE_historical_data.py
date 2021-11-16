import bs4
import requests
import pandas as pd

url_1w = 'https://secure.runescape.com/m=itemdb_rs/a=13/top100'
url_3m = 'https://secure.runescape.com/m=itemdb_rs/a=13/top100?list=0&scale=2'
def top100_table(url):
  x=requests.get(url)
  soup = bs4.BeautifulSoup(x.content)
  t=pd.read_html(x.content)[0]
  t2 = soup.find('table')
  trs=t2.find_all('tr')
  data = []
  for row in trs[2:]:
    tds = row.find_all('td')
    link = tds[0].find('a')
    name = link.text.strip()
    url = link.get('href')
    id = int(url.split('obj=')[1])
    members = bool(tds[1].contents)
    data.append((name,id,members))
  col_names = ['name', 'id', 'members']
  df=pd.DataFrame(data,columns=col_names)
  return df

t1=top100_table(url_1w)
t2=top100_table(url_3m)

pd.DataFrame.join(method='outer')






{'item': {'icon': 'https://secure.runescape.com/m=itemdb_rs/1636369430615_obj_sprite.gif?id=1515',
  'icon_large': 'https://secure.runescape.com/m=itemdb_rs/1636369430615_obj_big.gif?id=1515',
  'id': 1515,
  'type': 'Woodcutting product',
  'typeIcon': 'https://www.runescape.com/img/categories/Woodcutting product',
  'name': 'Yew logs',
  'description': 'Logs cut from a yew tree.',
  'current': {'trend': 'neutral', 'price': 261},
  'today': {'trend': 'negative', 'price': '- 5'},
  'members': 'false',
  'day30': {'trend': 'negative', 'change': '-16.0%'},
  'day90': {'trend': 'positive', 'change': '+7.0%'},
  'day180': {'trend': 'positive', 'change': '+14.0%'}}}