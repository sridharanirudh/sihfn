import json
from bs4 import BeautifulSoup
import re
import xml.etree.cElementTree as ET
import lxml.etree as etree
import glob
import pdb
import gzip

files = glob.glob('data/articles/ABCPolitics/*')
orientation = "mainstream"


tweetFile = gzip.open('data/tweets/ABCPolitics.json.gz')
tweets = json.loads(tweetFile.read())

portal = "abc"
veracity = "mostly true"

tweet_hash = {}
for tweet in tweets:
    tweet_hash[f'data/articles/ABCPolitics/{tweet["id_str"]}'] = tweet

findex = 0

for fname in files[-25:]:
    tweet_id = fname.split('-')[0]
    f = open(fname, 'rb')
    data = f.read()
    f.close()

    soup = BeautifulSoup(data, 'html.parser')

    article_e = ET.Element("article")
    author_e = ET.SubElement(article_e, "author")
    a = soup.find(class_="Byline__Author")
    if a:
        author_e.text = a.text
    else:
        author_e.text = ""
    orientation_e = ET.SubElement(article_e, "orientation")
    orientation_e.text = orientation

    portal_e = ET.SubElement(article_e, "portal")
    portal_e.text = portal

    v_e = ET.SubElement(article_e, "veracity")
    v_e.text = veracity

    url_e = ET.SubElement(article_e, "uri")
    url_e.text = tweet_hash[tweet_id]['entities']['urls'][0]['expanded_url']

    title = soup.title
    title_e = ET.SubElement(article_e, "title")
    if title:
        title_e.text = title.text
    else:
        title_e.text = ""

    articles = soup.find_all('article')
    if articles and len(articles) > 0:
        article = articles[0]
        mainText = ""
        p = article.find_all('p')
        pindex = 0
        for p_ in p:
            text = p_.text.strip()
            p_element = ET.SubElement(article_e, "paragraph")
            ET.SubElement(p_element, "start").text = str(pindex)
            pindex += len(text)
            ET.SubElement(p_element, "end").text = str(pindex)
            pindex += 1
            mainText += text
        q = re.findall(r'“(.*?)”', mainText)
        if mainText:
            for q_ in q:
                i = mainText.index(q_)
                q_element = ET.SubElement(article_e, "quote")
                ET.SubElement(q_element, "start").text = str(i)
                ET.SubElement(q_element, "start").text = str(i + len(q_))
                print(i, i + len(q_))
            mainText_e = ET.SubElement(article_e, "mainText")
            mainText_e.text = mainText

            tree = ET.ElementTree(article_e)
            tree.write(f"/home/anirudh/ub/cse702/sihfn/data/parsed/ABCNews/{findex}.xml")

            x = etree.parse(f"/home/anirudh/ub/cse702/sihfn/data/parsed/ABCNews/{findex}.xml")
            f = open(f"/home/anirudh/ub/cse702/sihfn/data/parsed/ABCNews/{findex}.xml", "wb+")
            f.write(etree.tostring(x, pretty_print=True))
            f.close()
            findex += 1
