import datetime
import requests
from bs4 import BeautifulSoup as soap

headers = {
    'authority': 'adstransparency.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version-list': '"Not.A/Brand";v="8.0.0.0", "Chromium";v="114.0.5735.134", "Google Chrome";v="114.0.5735.134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"15.0.0"',
    'sec-ch-ua-wow64': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

class GoogleAds:
    def __init__(self,  headers):
        self.reqs = requests.Session()
        self.headers = headers
        self.get_cookies()

    def get_cookies(self):
        params = {
            'region': 'anywhere',
        }
        self.reqs.get('https://adstransparency.google.com/', params=params, headers=headers)#.text.replace("\/","")
        #response = str(response[response.find("tfaaReportAppInfo"):]).encode('utf8').decode('unicode_escape')
        #print(json.loads(response[response.find("["):response.find(']')+1]))

    def refresh_session(self):
        self.reqs = requests.Session()
        self.get_cookies()

    def get_all_search_suggestions(self, keyword):
        data = {
            'f.req': '{"1":"' + keyword + '","2":10,"3":10}',
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchSuggestions',
            params={'authuser': '0'},
            data=data,
        )
        suggestions = response.json()["1"]
        if suggestions:    
            return suggestions
        return []

    def get_first_search_suggestion(self, keyword):
        if suggestions := self.get_all_search_suggestions(keyword):
            return suggestions[0]
        return []

    def get_advistisor_by_domain(self, domain):
        data = {
            "f.req": '{"2":40,"3":{"12":{"1":"' + domain + '"}}}'
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives',
            params={'authuser': ''},
            data=data,
        )
        response = response.json().get("1")
        if response:
            ad = response[0]
            return {"Advertisor Id": ad["1"], "Name":ad["12"]}
        return {}
        """if ads := response.json().get("1"):
            with open("new.json", "w") as f:
                json.dump(ads, f)
            return [{"Advertisor Id": ad[1],"Creative Id":ad["2"]} for ad in ads]
        return []"""

    def creative_search_by_advertiser_id(self, advertiser_id):
        data = {
            'f.req': '{"2":40,"3":{"12":{"1":"","2":true},"13":{"1":["' + advertiser_id + '"]}}, "7":{"1":1}}',
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives',
            params={'authuser': ''},
            data=data,
        )
        if ads := response.json().get("1"):
            return [ad["2"] for ad in ads]
        return []

    def get_creative_Ids(self, keyword):
        if search := self.get_first_search_suggestion(keyword):
            print(search)

            if search.get("2"): # TODO add domain  "Advertisor": advertisor, "Ad Count": Ad_count, 
                if advertisor := self.get_advistisor_by_domain(domain=search["2"]["1"]):
                    suggestions = self.get_all_search_suggestions(advertisor["Name"])
                    search = next((suggestion for suggestion in suggestions if suggestion["1"]["1"] == advertisor["Name"] and suggestion["1"]["2"] == advertisor["Advertisor Id"]), None)
                else:
                    return {"Advertisor": "", "Advertisor Id":"", "Ad Count": 0, "Creatives": []}
            advertisor = search["1"]["1"]
            Ad_count = search['1']['4']['2']['2'] if search["1"].get("4") else 0
            if Ad_count:
                return {"Advertisor": advertisor, "Advertisor Id": search["1"]["2"], "Ad Count": Ad_count, "Creative_Ids": self.creative_search_by_advertiser_id(advertiser_id=search["1"]["2"])}
            return {"Advertisor": advertisor, "Advertisor Id":search["1"]["2"], "Ad Count": Ad_count, "Creative_Ids": []}
        return {"Advertisor": "", "Advertisor Id":"", "Ad Count": 0, "Creatives": []}

    def get_link_to_video(self, link):
        response = requests.post(link)
        try:
            txt = next((x for x in response.text.split("CDATA[") if "googlevideo.com" in x))
            x = str(txt.split("]")[0]).encode("utf-8").decode("unicode_escape")
            return x.encode("utf-8").decode("unicode_escape")
        except:
            return link

    def get_breif_ads(self, advertisor_id, creative_id):
        data = {
            'f.req': '{"1":"' + advertisor_id + '","2":"' + creative_id + '","5":{"1":1}}',
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/LookupService/GetCreativeById',
            params={'authuser': '0'},
            data=data,
        )
        response = response.json()["1"]
        format_int = response["8"]
        format = "Text" if format_int == 1 else "Image" if format_int == 2 else "Video"
        if format == "Video":
            try:
                link = response["5"][0]["2"]["4"]  
            except:
                link = response["5"][0]["1"]["4"]
            if "displayads" in link:
                link = self.get_link_to_video(link)
        else:
            try:
                link = response["5"][0]["3"]["2"].split("'")[1]  
            except:
                link = response["5"][0]["1"]["4"]
            if "displayads" in link:
                link = self.get_link_to_video(link)

        date = datetime.datetime.fromtimestamp(int(response["4"]["1"])).strftime('%Y-%m-%d')
        return {"Adverisor Id" : advertisor_id,  # TODO Add Country
                "Creative Id" : creative_id,
                "Ad Format": format,
                "Last Shown" : date,
                "Ad Link" : link}
    
    def parse_ad_link(self, html):
        page = soap(html, 'lxml')
        try:
            ad_body = page.find("div", {"data-highlight-id-inside":"36"}).text
        except:
            ad_body = ""
            #ad_body = page.find_all("div", recursive=False)[0].text
        try: 
            ad_title = page.find("div", {"aria-level":"3"}).text
        except:
            ad_title = ""
        return {"Ad Body":ad_body, "Ad Title": ad_title}

    def get_detailed_ad(self, advertisor_id, creative_id):
        ad_detail = self.get_breif_ads(advertisor_id, creative_id)
        response = self.reqs.get(
            ad_detail["Ad Link"],
        )
        ad_detail.update({"Ad Body":"", "Ad Title": "", "Image URL": "", "Video URL": ""})
        if ad_detail["Ad Format"] == "Text":
            ad_detail.update(self.parse_ad_link(response.text))
        elif ad_detail["Ad Format"] == "Image":
            ad_detail["Image URL"] = ad_detail["Ad Link"]
        else:
            ad_detail["Video URL"] = ad_detail["Ad Link"]
        return ad_detail

if __name__ == '__main__':
    a = GoogleAds(headers)
    keyword = "ibbedesign"
    keyword = "facebook"
    creatives = a.get_creative_Ids(keyword)
    if creatives["Ad Count"]:
        advertisor_id = creatives["Advertisor Id"]
        for creative_id in creatives["Creative_Ids"]:
            #print(a.get_breif_ads(advertisor_id, creative_id))
            print(a.get_detailed_ad(advertisor_id,creative_id))
    else:
        print("Got nothing")