import datetime
import requests
from typing import Union
from bs4 import BeautifulSoup as soap
from GoogleAds.regions import Regions

HEADERS = {
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

def show_regions_list():
    """Displays Supported Regions Name along with their Region Codes"""
    print("Regions List")
    for region_code in Regions.keys():
        print(f"Region Name: {Regions[region_code]['Region']}\tRegion Code: {region_code}")

class GoogleAds:
    def __init__(self, region="anywhere", proxy=None):
        self.reqs = requests.Session()
        self.headers = HEADERS
        #proxy config
        self.proxy = proxy
        if proxy:
            self.reqs.proxies.update(proxy)

        self.r_check = True
        if region == "anywhere":
            self.r_check = False
        print((not Regions.get(region)) and self.r_check)
        if (not Regions.get(region)) and self.r_check:
            raise Exception("Invalid Region Code")
        self.region = region
        self.region_num = Regions[region]["1"] if self.r_check else 0
        self.get_cookies()

    def get_cookies(self):
        """Get Cookies from the main url https://adstransparency.google.com/ and store them in requests Session"""
        params = {
            'region': self.region,
        }
        self.reqs.get('https://adstransparency.google.com/', params=params, headers=self.headers)#.text.replace("\/","")
        #response = str(response[response.find("tfaaReportAppInfo"):]).encode('utf8').decode('unicode_escape')
        #print(json.loads(response[response.find("["):response.find(']')+1]))

    def refresh_session(self, proxy=None):
        """Refresh Session cookies"""
        self.reqs = requests.Session()
        self.get_cookies()
        if proxy:
            self.proxy = proxy
        self.reqs.proxies.update(self.proxy)

    def get_all_search_suggestions(self, keyword: str) -> list:
        """
            Gets All suggestions from the Google Ads Transparency for given keyword.
            Returns list of Suggestions along with their details
            Returns Empty list [] if no suggestion found"""
        data = {
                'f.req': '{"1":"' + keyword + '","2":10,"3":10}',
                }            
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchSuggestions',
            params={'authuser': '0'},
            data=data,
        )
        return suggestions if (suggestions := response.json().get("1")) else []

    def get_first_search_suggestion(self, keyword: str) -> Union[dict,None]:
        """
           Gets First Suggestions from the Google Ads Transparency for given keyword.
           Returns dict of Suggestion details
           Returns None if no suggestion found"""
        
        if suggestions := self.get_all_search_suggestions(keyword):
            return suggestions[0]
        return None

    def get_advistisor_by_domain(self, domain: str) -> Union[dict,None]:
        """
            Makes search of domain/url and returns the Company Name and It's Advertisor Id 
        """
        data = {
            "f.req": '{"2":40,"3":{"12":{"1":"' + domain + '"}}}'
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives',
            params={'authuser': ''},
            data=data,
        )
        if response := response.json().get("1"):
            ad = response[0]
            return {"Advertisor Id": ad["1"], "Name":ad["12"]}
        #if ads := response.json().get("1"):
        #    with open("new.json", "w") as f:
        #        json.dump(ads, f)
        #    return [{"Advertisor Id": ad[1],"Creative Id":ad["2"]} for ad in ads]
        #return []

    def creative_search_by_advertiser_id(self, advertiser_id: str) -> list:    #TODO do region search
        """Get Creatives or ads by quering given Advertisor Id
        If no Ad found return []"""
        data = {
            'f.req': '{"2":40,"3":{"12":{"1":"","2":true},"13":{"1":["' + advertiser_id + '"]}}, "7":{"1":1}}',
        }
        if self.r_check:
            data = {
            'f.req': '{"2":40,"3":{"8":[' + str(self.region_num) + '],"12":{"1":"","2":true},"13":{"1":["' + advertiser_id + '"]}}, "7":{"1":1}}',
        }
        response = self.reqs.post(
            'https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives',
            params={'authuser': ''},
            data=data,
        )
        return [ad["2"] for ad in ads] if (ads := response.json().get("1")) else []

    def get_creative_Ids(self, keyword: str) -> dict:
        """Makes search for given keyword and gets the first Suggestion. Then gets the Creatives for that.
        Returns Advertisor Name, Id, Ad count and List of Creatives"""
        if not (search := self.get_first_search_suggestion(keyword)):
            return {"Advertisor": "", "Advertisor Id":"", "Ad Count": 0, "Creatives": []}
        print(search)

        if search.get("2"): 
            if not (advertisor := self.get_advistisor_by_domain(domain=search["2"]["1"])):
                return {"Advertisor": "", "Advertisor Id":"", "Ad Count": 0, "Creatives": []}
            suggestions = self.get_all_search_suggestions(advertisor["Name"])
            search = next((suggestion for suggestion in suggestions if suggestion["1"]["1"] == advertisor["Name"] and suggestion["1"]["2"] == advertisor["Advertisor Id"]), None)
        advertisor = search["1"]["1"]
        Ad_count = search['1']['4']['2']['2'] if search["1"].get("4") else 0
        if Ad_count:
            return {"Advertisor": advertisor, "Advertisor Id": search["1"]["2"], "Ad Count": Ad_count, "Creative_Ids": self.creative_search_by_advertiser_id(advertiser_id=search["1"]["2"])}
        return {"Advertisor": advertisor, "Advertisor Id":search["1"]["2"], "Ad Count": Ad_count, "Creative_Ids": []}

    def get_link_to_video(self, link: str) -> str:
        """Get the JS response from the link given and parse the Video/Image Link. Returns input Link if any error occurs"""
        response = requests.post(link)
        try:
            txt = next((x for x in response.text.split("CDATA[") if "googlevideo.com" in x))
            x = str(txt.split("]")[0]).encode("utf-8").decode("unicode_escape")
            return x.encode("utf-8").decode("unicode_escape")
        except Exception:
            return link

    def get_breif_ads(self, advertisor_id: str, creative_id: str) -> dict:    # TODO do region search
        """Takes the Advertisor Id and Creative ID and returns the breif details of that particular Ad"""
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
        format_ = "Text" if format_int == 1 else "Image" if format_int == 2 else "Video"
        try:
            if format_ == "Video":
                link = response["5"][0]["2"]["4"]
            else:
                link = response["5"][0]["3"]["2"].split("'")[1]
        except Exception:
            link = response["5"][0]["1"]["4"]
        if "displayads" in link:
            link = self.get_link_to_video(link)
        date = datetime.datetime.fromtimestamp(int(response["4"]["1"])).strftime('%Y-%m-%d')
        return {"Adverisor Id" : advertisor_id,  # TODO Add Country
                "Creative Id" : creative_id,
                "Ad Format": format_,
                "Last Shown" : date,
                "Ad Link" : link}
    
    def parse_ad_link(self, html: str) -> dict:
        """Parse the Ad Body and Ad title from the html"""
        page = soap(html, 'lxml')
        try:
            ad_body = page.find("div", {"data-highlight-id-inside":"36"}).text
        except Exception:
            ad_body = ""
        try:
            ad_title = page.find("div", {"aria-level":"3"}).text
        except Exception:
            ad_title = ""
        return {"Ad Body":ad_body, "Ad Title": ad_title}

    def get_detailed_ad(self, advertisor_id: str, creative_id: str) -> dict:
        """Takes the Advertisor Id and Creative ID and returns the details of that particular Ad"""
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
    a = GoogleAds()
    keyword = "ibbedesign"
    keyword = "Google"
    print(a.get_advistisor_by_domain(keyword), end="\n\n")
    creatives = a.get_creative_Ids(keyword)
    if creatives["Ad Count"]:
        advertisor_id = creatives["Advertisor Id"]
        for creative_id in creatives["Creative_Ids"]:
            #print(a.get_breif_ads(advertisor_id, creative_id))
            print(a.get_detailed_ad(advertisor_id,creative_id))
    else:
        print("Got nothing")