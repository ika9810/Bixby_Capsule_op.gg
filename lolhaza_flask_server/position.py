from bs4 import BeautifulSoup as bs
import requests

url = "https://www.op.gg/champion/statistics"

req = requests.get(url)
html = bs(req.text,"html.parser")
#a 챔피언별포지션 전체
#b 각 챔피언의 이름 전체
a = html.select("body > div.l-wrap.l-wrap--champion > div.l-container > div.l-champion-index > div.l-champion-index-content > div.l-champion-index-content--main > div.champion-index__champion-list > div > a > div.champion-index__champion-item__positions")
b = html.select("body > div.l-wrap.l-wrap--champion > div.l-container > div.l-champion-index > div.l-champion-index-content > div.l-champion-index-content--main > div.champion-index__champion-list > div > a > div.champion-index__champion-item__name")

result = {}
positionlist = []
champnamelist = []
def getposition(champion):
    print(champion)
    for j in a:       #챔피언 포지션에 챔프별로 j 하나당 하나의 챔피언
        poslist = []
        for k in j.select("div.champion-index__champion-item__position"):       #각 챔피언 안의 포지션들을 추출
            k = k.select("span")[0].text
            poslist.append(k)
        positionlist.append(poslist)
    for i in b: #챔피언 이름별로 저장
        champnamelist.append(i.text.lower())
    for l in range(len(champnamelist)):     #두 개 매칭
        result[champnamelist[l]] = positionlist[l]
    return result[champion]
# Converstion-Driver
# Server => db.py ->