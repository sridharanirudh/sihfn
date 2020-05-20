import json
from bs4 import BeautifulSoup
import re
import xml.etree.cElementTree as ET
import lxml.etree as etree
import glob
import pdb
import gzip

files = glob.glob('data/articles/CNNPolitics/*')
orientation = "mainstream"


tweetFile = gzip.open('data/tweets/CNNPolitics.json.gz')
tweets = json.loads(tweetFile.read())

portal = "cdn"
veracity = "mixture of true and false"

tweet_hash = {}
for tweet in tweets:
    tweet_hash[f'data/articles/CNNPolitics/{tweet["id_str"]}'] = tweet

findex = 0

for fname in files[-25:]:
    tweet_id = fname.split('-')[0]
    f = open(fname, 'rb')
    data = f.read()
    f.close()

    soup = BeautifulSoup(data, 'html.parser')

    article_e = ET.Element("article")
    author_e = ET.SubElement(article_e, "author")
    pma = soup.find(class_="metadata__byline__author")
    atext = ""
    if pma:
        a = pma.find('a')
        if a:
            atext = a.text
    author_e.text = atext
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

    mainText = ""
    p = soup.find_all(class_='zn-body__paragraph')
    pindex = 0
    for p_ in p:
        text = p_.text.strip()
        p_element = ET.SubElement(article_e, "paragraph")
        ET.SubElement(p_element, "start").text = str(pindex)
        pindex += len(text)
        ET.SubElement(p_element, "end").text = str(pindex)
        pindex += 1
        mainText += text
    q = re.findall(r'"(.*?)"', mainText)
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
        tree.write(f"/home/anirudh/ub/cse702/sihfn/data/parsed/CNNPolitics/{findex}.xml")

        x = etree.parse(f"/home/anirudh/ub/cse702/sihfn/data/parsed/CNNPolitics/{findex}.xml")
        f = open(f"/home/anirudh/ub/cse702/sihfn/data/parsed/CNNPolitics/{findex}.xml", "wb+")
        f.write(etree.tostring(x, pretty_print=True))
        f.close()
        findex += 1
