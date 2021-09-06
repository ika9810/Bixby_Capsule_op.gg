from bs4 import BeautifulSoup as bs
import requests
import database as db
import position as pst
from flask import Flask, request
import json

class Champion:
    default    = "body > div.l-wrap.l-wrap--champion > div.l-container > div"
    statistics = "div.l-champion-statistics-header > div"
    matchup    = {
        "strong": "div.champion-stats-header-matchup>div>table.champion-stats-header-matchup__table.champion-stats-header-matchup__table--strong.tabItem>tbody>tr",
        "weak"  : "div.champion-stats-header-matchup>div>table.champion-stats-header-matchup__table.champion-stats-header-matchup__table--weak.tabItem>tbody>tr"
    }
    rune = "div.tabWrap>div.l-champion-statistics-content>div.Content.championLayout-overview>div>div.l-champion-statistics-content__main>div>table>tbody.ChampionKeystoneRune-1>tr:nth-child(1)>td.champion-overview__data>div.perk-page-wrap>div.perk-page"
    fragment_rune = "div.tabWrap>div.l-champion-statistics-content.tabItems>div.Content.championLayout-overview>div>div.l-champion-statistics-content__main>div>table>tbody.ChampionKeystoneRune-1>tr:nth-child(1)>td.champion-overview__data>div>div.fragment-page>div.fragment__detail>div.fragment__row"
    spell="div.tabWrap>div.l-champion-statistics-content>div.Content.championLayout-overview>div>div.l-champion-statistics-content__main>table.champion-overview__table.champion-overview__table--summonerspell>tbody:nth-child(3)>tr:nth-child({})>td.champion-overview__data>ul>li.champion-stats__list__item"
    item ="div.tabWrap > div.l-champion-statistics-content.tabItems > div.tabItem.Content.championLayout-overview > div > div.l-champion-statistics-content__main > table:nth-child(2) > tbody > tr.champion-overview__row--first"
    skill = "div>div.l-champion-statistics-content.tabItems>div.Content.championLayout-overview>div>div.l-champion-statistics-content__main>table.champion-overview__table.champion-overview__table--summonerspell>tbody:nth-child(5)>tr>td.champion-overview__data>ul>li.champion-stats__list__item"
    firstskill = "div.tabWrap > div.l-champion-statistics-content.tabItems > div.tabItem.Content.championLayout-overview > div > div.l-champion-statistics-content__main > table.champion-overview__table.champion-overview__table--summonerspell > tbody:nth-child(5) > tr > td.champion-overview__data > table > tbody > tr:nth-child(2) > td:nth-child(1)"
    def __init__(self, name, position):
        self.url = f"https://www.op.gg/champion/{name}/statistics/{position}"
        headers  = {
            "Accept-Language": "ko_KR" 
        }

        self.html = bs(requests.get(self.url, headers=headers).text, 'html.parser')

    def tester(self,data):
        option = f"body > div.l-wrap > div.l-container > div > div > p"
        judge  = self.html.select(option)[0].text.strip()
        data['judge'] = judge
        return data
    def GetMainPosition(self, data, champion):
        print(champion)
        data['possibleposition'] = pst.getposition(champion)
        return data

    def GetPosition(self, data, position):
        option = f"{self.default}>{self.statistics}> ul > li > a > span.champion-stats-header__position__role"
        if position == "mid":
            Positionname = "미드"
        elif position == "jungle":
            Positionname = "정글"
        elif position == "top":
            Positionname = "탑"
        elif position == "adc":
            Positionname = "원딜"
        elif position == "support":
            Positionname = "서폿"           #발화를 통해 받는 경우 빅스비에서 보내줄 때 정형화 해서 보내줄 거니 5가지로 fix
        else:
            Positionname = self.html.select(option)[0].text.strip()
        data['position'] = Positionname
        return data
    def GetChampionImg(self, data):
        imgurl = db.makeImg(db.koToen(data['name']))
        data['champImg'] = imgurl
        return data    

    def GetChampionName(self, data):
        option = f"{self.default}>{self.statistics}>div.champion-stats-header-info > h1"
        name   = self.html.select(option)[0].text.strip()
        data['name'] = name
        return data

    def GetVersion(self, data):
        option  = f"{self.default}>{self.statistics}>div.champion-stats-header-version"
        version = self.html.select(option)[0].text.split(":")[-1].strip()
        data['patchVersion'] = version
        return data

    def GetTier(self, data):
        option = f"{self.default}>{self.statistics}>div.champion-stats-header-info>div.champion-stats-header-info__tier>b"
        try:
            tier = self.html.select(option)[0].text.strip()
        except:
            tier = 'Empty'
        data['tier'] = tier
        return data

    def GetMatchup(self, options):
        option = f"{self.default}>{self.statistics}>{self.matchup[f'{options}']}"
        html   = self.html.select(option)
        matchresult = []
        for champion in html:
            name = champion.select("td:nth-child(1)")[0].text.strip()
            rate = champion.select("td:nth-child(2) > b")[0].text.strip()
            img  = champion.select("td:nth-child(1) > img")[0].get("src")
            img = "http:" + img.split("?")[0]
            Limg = db.makeImg(db.koToen(name))
            result = [name, rate, img, Limg]
            return result
            
    def GetCounter(self, data):
        data['counterChamp'] = self.GetMatchup('strong')
        data['weakChamp'] = self.GetMatchup('weak')
        return data

    def GetMainRune(self, data):
        mainlist = []
        option = f"{self.default}>{self.rune}"
        html = self.html.select(option)[0]
        for i in range(1,6):
            option = f"div.perk-page__row:nth-child({i})>div.perk-page__item"
            _ = html.select(option)
            for j in _:
                url = "http:" + j.select("img")[0].get('src').split('?')[0]
                mainlist.append(url)
        return mainlist

    def GetAssistantRune(self, data):
        assistantlist = []
        option = f"{self.default}>{self.rune}"
        html = self.html.select(option)[1]
        for i in range(1,5):
            option = f"div.perk-page__row:nth-child({i})>div.perk-page__item"
            _ = html.select(option)
            for j in _:
                url = "http:"+ j.select("img")[0].get('src').split('?')[0]
                assistantlist.append(url)
        return assistantlist

    def GetFragmentRune(self, data):
        fragmentlist = []
        option = f"{self.default}>{self.fragment_rune}"
        html = self.html.select(option)
        for i in html:
            _ = i.select("div.fragment > div.perk-page__image")
            for j in _:
                url = "http:" + j.select("img")[0].get('src').split('?')[0]
                fragmentlist.append(url)
        return fragmentlist

    def GetRune(self, data):
        data['recMainRune'] = self.GetMainRune(data)
        data['recAssistantRune'] = self.GetAssistantRune(data)
        data['recFragmentRune'] = self.GetFragmentRune(data)
        return data

    def GetSpell(self, data):
        datalist = []
        for k in range(1,3):
            option = f"{self.default}>{self.spell.format(k)}"
            html = self.html.select(option)
            for i in html:
                url = "http:" + i.select('img')[0].get('src').split('?')[0]
                datalist.append(url)
        data['recSpell'] = datalist
        return data

    def GetItem(self, data):
        option = f"{self.default}>{self.item}"
        html = self.html.select(option)
        firstlist = []
        mainlist = []
        bootlist = []
        order = [firstlist, mainlist, bootlist]
        num = 0
        for i in html:
            option = "td.champion-overview__data>ul>li.champion-stats__list__item"
            _ = i.select(option)
            for j in _:
                link = "http:" + j.select("li>img")[0].get("src").split('?')[0]
                order[num].append(link)
            num+=1
        data['recStartItem'] = firstlist
        data['recMainItem'] = mainlist
        data['recBoots'] = bootlist
        return data

    def GetSkill(self, data):
        option = f"{self.default}>{self.skill}"
        options = f"{self.default}>{self.firstskill}"
        html = self.html.select(option)
        imglist = []
        orderlist = []
        for i in html:
            img = "http:" + i.select("img")[0].get('src').split('?')[0]
            key = i.select("span")[0].text
            imglist.append(img)
            orderlist.append(key)
        orderlist.append(', '.join(orderlist))
        data['recSkill'] = imglist
        data['recSkillorder'] = orderlist
        data['firstskill'] = self.html.select(options)[0].text.strip()
        return data

    def run(self, position, champion):
        _test = {}
        try:    
            _test = self.GetChampionName(_test)
            _test = self.GetChampionImg(_test)
            _test = self.GetPosition(_test, position)
            _test = self.GetMainPosition(_test, champion)
            _test = self.GetVersion(_test)
            _test = self.GetTier(_test)
            _test = self.GetCounter(_test)
            _test = self.GetSpell(_test)
            _test = self.GetSkill(_test)
            _test = self.GetItem(_test)
            _test = self.GetRune(_test)
            return _test
        except:
            _test = self.tester(_test)
            return _test
    # def run(self, position, champion):                        #test용
    #     _test = {}
    #     _test = self.GetChampionName(_test)
    #     _test = self.GetChampionImg(_test)
    #     _test = self.GetPosition(_test, position)
    #     _test = self.GetMainPosition(_test, champion)
    #     _test = self.GetVersion(_test)
    #     _test = self.GetTier(_test)
    #     _test = self.GetCounter(_test)
    #     _test = self.GetSpell(_test)
    #     _test = self.GetSkill(_test)
    #     _test = self.GetItem(_test)
    #     _test = self.GetRune(_test)
    #     return _test
champion = ""
position = ""

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def API():
    #query = request.query_string.decode('utf-8')
    position = request.args.get('position')
    champion = request.args.get('champion')
    print(position)
    print(champion)
    c = Champion(champion, position)
    result = c.run(position,champion)
    print(result)
    return json.dumps(result, ensure_ascii=False)

@app.route("/data", methods=["GET", "POST"])
def DATA():
    result = db.champData()
    return json.dumps(result, ensure_ascii=False)
    
app.run('0.0.0.0',port=8000)