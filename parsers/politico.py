import json
from bs4 import BeautifulSoup
import re
import xml.etree.cElementTree as ET
import lxml.etree as etree
import glob
import pdb
import gzip

files = glob.glob('data/articles/politico/*')
orientation = "right"


tweetFile = gzip.open('data/tweets/politico.json.gz')
tweets = json.loads(tweetFile.read())

portal = "politico"
veracity = "mostly false"

tweet_hash = {}
for tweet in tweets:
    tweet_hash[f'data/articles/politico/{tweet["id_str"]}'] = tweet

findex = 0

for fname in files[-25:]:
    tweet_id = fname.split('-')[0]
    f = open(fname, 'rb')
    data = f.read()
    f.close()

    soup = BeautifulSoup(data, 'html.parser')

    article_e = ET.Element("article")
    author_e = ET.SubElement(article_e, "author")
    pa = soup.find(class_="story-meta__authors")
    atext = ""
    if pa:
        a = pa.find("a")
        if a:
            atext = a.text.strip()
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
    p = soup.find_all(class_='story-text__paragraph')
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
        tree.write(f"/home/anirudh/ub/cse702/sihfn/data/parsed/politico/{findex}.xml")

        x = etree.parse(f"/home/anirudh/ub/cse702/sihfn/data/parsed/politico/{findex}.xml")
        f = open(f"/home/anirudh/ub/cse702/sihfn/data/parsed/politico/{findex}.xml", "wb+")
        f.write(etree.tostring(x, pretty_print=True))
        f.close()
        findex += 1
