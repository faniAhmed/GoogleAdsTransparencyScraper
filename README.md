# GoogleTransparencyScraper

It is a scraper that gets the Creatives/Ads data from Google Ads Transparency. The public API of Google Transparency have been reverse enginnered to get the desired data.  It has support for search based on specific region and also supports proxies. Any one can contribute to this project by making a pull request or identifying any feature that I should add to it.
<br><br>
For Donations:<br>
You can send remmitance on the following account.<br>
Name: Farhan Ahmed<br>
Bank: Sadapay<br>
Country: Pakistan<br>
IBAN: PK29SADA0000003406021417<br>

## Installation:

You can install it using pip.

```
pip install Google-Ads-Transparency-Scraper
```

The PyPi link to the module is
[https://pypi.org/project/Google-Ads-Transparency-Scraper/](Google Ads Transparency Scraper)

## Usage:

After Installation you can import the module as

```
from GoogleAds.main import GoogleAds, show_regions_list
```

###### Example Code:

```
    a = GoogleAds()
    keyword = "Google LLC"
    creatives = a.get_creative_Ids(keyword, 200) # Get 200 creatives if available
    if creatives["Ad Count"]:
        advertisor_id = creatives["Advertisor Id"]
        for creative_id in creatives["Creative_Ids"]:
            #print(a.get_breif_ads(advertisor_id, creative_id))
            print(a.get_detailed_ad(advertisor_id,creative_id))
    else:
        print("Got nothing")
```

### show_regions_list():

Displays Supported Regions Name along with their Region Codes

This function is called without any parameters. Simply call the function as follow.

```
show_regions_list()
```

### GoogleAds():

The class GoogleAds has Region and proxy as Optional parameters. Proxy will remain same for a single object instance though you can update proxy and cookies using the refresh_session() function (Details are available in the section below). 

```
def__init__(self, region="anywhere", proxy=None)
```

The Obj instance can be created as follow

```
proxy = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }
Obj1 = GoogleAds()
Obj2 = GoogleAds(region="pk")
Obj3 = GoogleAds(proxy=proxy)
Obj4 = GoogleAds(region="pk", proxy=proxy)
```

The followinga are the functions provided in this module

##### Refresh Session:

It changes cookies and proxies[Optional] making a new session with Google. Benificient to call periodically so Google does not block you.
The previous region will be continued and proxies will be updated as per given parameters.
```
Obj1.refresh_session()
Obj1.refresh_session(proxy=proxy)
```

##### Get All Search Suggestion:

It gets all the Search Suggestions for a particular *keyword*  argument given to the function `get_all_search_suggestions(self, keyword: str)`

```
Obj1.get_all_search_suggestions("Google") # Google is the search keyword
```

Returns list of Suggestions along with their details

Returns Empty list [] if no suggestion found

```
[
     {
         "1": {
                 "1": "Google",  # Advertisor Name
                 "2": "AR05099026886533578753", # Advertisor Id
                 "3": "US", # Advertisor Region
                 "4": {
                     "2": {
                         "1": "22",
                         "2": "22"
                     }
                 }
             }
     },
     {
    "2": {
        "1": "google.com" # Domain that matches the searched keyword
     }
   }
]
```

Suggestions are in dict and have two formats. One is Avertisor Format and the Other is domain format.
The Main things that are usefull are Name, Advertisor Id, Region and the Domain

##### Get First Search Suggestion:

Gets First Suggestions from the Google Ads Transparency for given keyword.
Returns dict of Suggestion details
Returns None if no suggestion found

```
Obj1.get_first_search_suggestion("Keyword")
```

##### Get Adverstisor By Domain:

Makes search of domain/url and returns the Company Name and It's Advertisor Id. The

> {'Advertisor Id': 'AR14188379519798214657', 'Name': 'Google LLC'}

##### Get Creative Ids:
Takes a keyword and a count argument. The count argument tells the number of creatives that need to be extracted
Makes search for given keyword and gets the first Suggestion. Then gets the Creatives for that.

Returns Advertisor Name, Id, Ad count and List of Creatives

The following is the return format

> {"Advertisor": "", "Advertisor Id":"", "Ad Count": 0, "Creatives": []}

You call this method as follow

```
Obj1.get_creative_Ids("Keyword", 200) # count is 40 by default
```

##### Get Creatives by Advertisor Id:

Get list of Creative Ids for given Advertisor Id

```
Obj1.creative_search_by_advertiser_id("Advertisor Id", 200) # count is 40 by default
```

##### Get Brief Ad Info:

Takes the Advertisor Id and Creative ID and returns the breif info of that particular Ad

```
Obj1.get_breif_ads("Advertisor Id", "Creative Id")
```

Returns Data in following format

> {"Adverisor Id" : "", "Creative Id" : "", "Ad Format": "Text/Image/Video", "Last Shown" : "Date", "Ad Link" : ""}

##### Get Detailed Ad Info:

Takes the Advertisor Id and Creative ID and returns the details of that particular Ad

```
Obj1.get_detailed_ad("Advertisor Id", "Creative Id")
```

Returns the Data in the following format

> {"Adverisor Id" : "", "Creative Id" : "", "Ad Format": "Text/Image/Video", "Last Shown" : "Date", "Ad Link" : "", "Ad Body":"", "Ad Title": "", "Image URL": "", "Video URL": ""}
