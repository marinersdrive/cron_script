import os
import pymysql
import decimal
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
import json

##################################################generator###############################################################
cookies = {
    '_csrf': '-QlSRpfa7b8_G_tIr-rAzIWR',
}

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'apollographql-client-name': 'Flipkart-Ads',
    'x-csrf-token': 'w1qiG7Nm--Tbq5z42RXqHDbzCPd4YQ3P2l-E',
    'x-sourceurl': 'https://advertising.flipkart.com/login?tenant=BSS',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'viewport-width': '1536',
    'content-type': 'application/json',
    'accept': '*/*',
    'apollographql-client-version': '1.0.0',
    'dpr': '1.25',
    'downlink': '10',
    'x-tenant': 'BSS',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://advertising.flipkart.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://advertising.flipkart.com/login?tenant=BSS',
    'Accept-Language': 'en-US,en;q=0.9',
}

json_data = {
    'operationName': 'LoginUser',
    'variables': {
        'password': 'Trailytics@123',
        'userLoginId': 'ashutosh.shukla@trailytics.com',
    },
    'query': 'mutation LoginUser($userLoginId: String!, $password: String!) {\n  loginUser(userLoginId: $userLoginId, password: $password) {\n    email\n    state\n    mobile\n    firstName\n    success\n    __typename\n  }\n}\n',
}
response = requests.post('https://advertising.flipkart.com/api', cookies=cookies, headers=headers, json=json_data)
cookies = response.cookies
# print(cookies)

cookie_dict = {}

for cookie in cookies:
    cookie_dict[cookie.name] = cookie.value



#################################################db realted things ############################################################


DB_HOST = "tr-wp-database.cfqdq6ohjn0p.us-east-1.rds.amazonaws.com"
DB_USER = "shivam"
DB_PASSWORD = "Trailytics@789"
DB_DATABASE = "amazon_ads_api"
DB_PORT = 3306

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_DATABASE,
    port=DB_PORT,
    connect_timeout=1000,
    autocommit=True
)

cursor = connection.cursor()
cursor.execute("SELECT MAX(Date) FROM fk_pla_nivea_pca;")
max_date = cursor.fetchone()[0]
max_date = max_date.date()


cursor.execute("SELECT DISTINCT(Campaign_ID) FROM fk_pla_nivea_pca WHERE troas < -1 AND DATE(Date) = %s;", (max_date,))
campaign_ids = cursor.fetchall()

if campaign_ids:
    for campaign_id in campaign_ids:
        print(campaign_id[0])
else:
    print("No campaigns found")





# for campaign_id in campaign_ids:
#     placement_dict = []
#     cursor.execute("SELECT Absolute_Cost, Percentage,Placement_Type FROM fk_pla_nivea_pca  WHERE Campaign_ID = %s;", (campaign_id,))
#     placements = cursor.fetchall()
#     for placement in placements:
#         placement_dict.append({
#             'absoluteCost': int(placement[0]),
#             'percentage': placement[1],
#             'type': placement[2]
#         })

#     print(placement_dict)
    


def adjust_absolute_cost(absolute_cost, percentage_change):
    if percentage_change:
        adjusted_cost = float(absolute_cost) * (1 + percentage_change / 100)
    else:
        pass
        #adjusted_cost = float(absolute_cost) * (1 + percentage_change / 100)
    return adjusted_cost

i=0
for campaign_id in campaign_ids:
    placement_dict = []
    cursor.execute("SELECT Absolute_Cost, Percentage, Placement_Type FROM fk_pla_nivea_pca WHERE Campaign_ID = %s;", (campaign_id,))
    placements = cursor.fetchall()
    for placement in placements:
        percentage_change = 2  # frontend se pass hogea
        adjusted_absolute_cost = adjust_absolute_cost(placement[0], percentage_change)

        cursor.execute("UPDATE fk_pla_nivea_pca SET Absolute_Cost = %s WHERE Campaign_ID = %s AND Placement_Type = %s;",
                       (adjusted_absolute_cost, campaign_id, placement[2]))
        connection.commit()

        placement_dict.append({
            'absoluteCost': float(adjusted_absolute_cost),
            'percentage': placement[1],
            'type': placement[2]
        })
    # print(campaign_id[i])
    # exit()
    # print(placement_dict)

    ###########################support_pca####################
    
    cookies_x = {
        'T': 'TI169891842149300161944937865135939588577615020537527148270186391420',
        '_pxvid': 'c6c61fc1-7964-11ee-8e5a-1d67ccbdf2e0',
        'dpr': '1.25',
        '_fbp': 'fb.1.1700471257731.638459595',
        '_ga_B9RGC9GN63': 'GS1.1.1702722512.1.1.1702722682.54.0.0',
        'DID': 'clr1pup252bqp0x0wejpe1ajo',
        'ULSN': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjb29raWUiLCJhdWQiOiJmbGlwa2FydCIsImlzcyI6ImF1dGguZmxpcGthcnQuY29tIiwiY2xhaW1zIjp7ImdlbiI6IjEiLCJ1bmlxdWVJZCI6IlVVSTI0MDIxNDEyNTQxMjc4NE85TU9OTE0iLCJma0RldiI6bnVsbH0sImV4cCI6MTcyMzY3NTQ1MiwiaWF0IjoxNzA3ODk1NDUyLCJqdGkiOiIzZmIzYjAxZS02MzU2LTRjM2ItYTg3Yi1lNDQ3ZWNmMWJiYzEifQ.qbw3LDnvt96oOTYcrXvedJeOeJteVaWqgwkYlaKjyuw',
        'vh': '730',
        'vw': '1536',
        '_ga_0RGM1K38MN': 'GS1.2.1708195526.2.1.1708195657.0.0.0',
        '_ga_C00F4Q43Q7': 'GS1.2.1708196044.1.0.1708196044.0.0.0',
        '_gcl_au': '1.1.856723108.1708257205',
        'ud': '3.-hCuLDZfVJf9kwEcWhK4arj09yD35YGA9WD7yo1zRPr-6c1rmX2_xdHegqPpB3V8IXYz3NsAnP3SBWNaEKufBfykm01W9EISet6O__tpbwLut1-EZphHbJ0c9MzW0rczeRXhalfDVODMz8JTNMlQlgc9FtPFTSU9rNePFCXS_okASoEjAhPorkspIuB6dUcZtsYfTSEOj6D6fCfEhHGTX040PuZMdyiyk409VK7VDUArNQCXrRjfusSZdRR_dSa_IYardO48M5GyGz8FGpTkPTBYE_1zDB-5NXEc93lP2wklWoHEa-Dtp_7e6v2PvoLYEnO9q9WRO923E1MzbxEsgQzTal18ocz6m1QhVKcLAkifQY1CVPvSCEDYAhYysg7Cifn25pVGYReJE-wqKz__XeZKWQ6m9S5ylJWi8ZCNic_rQWkW8tl4jP7uwPxupbq0hBk3YeSRAVvcjX09zDY5qn4jmi-pJicw3oOin6BBwh5j4AEuCE1_UBhyu1FzQ6HXVin354_zqMKmt5Ez4awQztwLbxHMqBrzPLNw1nVv-mMH56A0UIV523BaT7wlgFXFKDY9PgZuquXJtkpqqSSPK3sdeoBmL_SsoP5XdHnW3U3lvtJigEiuV1-2In3wufWsqsHYvXC8tj7Vr6X8srs_3ehJ7eFh0ZMdB7QsQTCynabS2sW3gILSeLC2-NwmdaemzanTaScNERb6Z6uBV6aYgxLtiUZZci5cqwxPaCVTIRHxdKh90EtL6MagI-T8KaMNUkYxg3mOLw4UnS1OIQr5vw',
        '_ga_2P94RMW04V': 'GS1.2.1711394187.7.1.1711394237.0.0.0',
        'AMCV_55CFEDA0570C3FA17F000101%40AdobeOrg': '-227196251%7CMCIDTS%7C19815%7CMCMID%7C83672356534473986601461754159478791217%7CMCAAMLH-1712558585%7C12%7CMCAAMB-1712558585%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1711960985s%7CNONE%7CMCAID%7CNONE',
        'mp_9ea3bc9a23c575907407cf80efd56524_mixpanel': '%7B%22distinct_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24device_id%22%3A%20%2218bf5c79f2b403-04403e63bfeec8-26031051-144000-18bf5c79f2ca33%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fseller.flipkart.com%2Fsell-online%2Fmulti-select%22%2C%22%24initial_referring_domain%22%3A%20%22seller.flipkart.com%22%2C%22%24user_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24search_engine%22%3A%20%22google%22%7D',
        '_ga': 'GA1.1.1819741834.1700633034',
        's_nr': '1711953817499-Repeat',
        '_ga_0SJLGHBL81': 'GS1.1.1711963800.32.0.1711963800.0.0.0',
        '_ga_TVF0VCMCT3': 'GS1.1.1711963800.153.0.1711963800.60.0.0',
        'SN': 'VI6C522DFEDDDB47B094DBAB8FB82537CC.TOK635F5023E626455C82262BA71755319E.1712039145.LI',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNhNzdlZTgxLTRjNWYtNGU5Ni04ZmRlLWM3YWMyYjVlOTA1NSJ9.eyJleHAiOjE3MTIwNDA5NDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZWNhMjk4YmItYjg2OS00NDUzLWFmN2QtYmRmNTMxMzRkOTUxIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwiZWFJZCI6ImJlMHVRSWdQSVRwMlpxYW5OTmhobkdIamhSdi1QMVhOTmNURnloQS16QVNBWU40QlZ2NF9Odz09IiwidnMiOiJMSSIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QlU14s5wGMPi9nFMdwxMyzDo4smmVhEtrHlqVyVhTNk',
        'rt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhlM2ZhMGE3LTJmZDMtNGNiMi05MWRjLTZlNTMxOGU1YTkxZiJ9.eyJleHAiOjE3Mjc4NTAzNDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiNDIzZjU0NzUtNTlkNC00MDg1LWFiODctOGU0MDE0NGVkMzhlIiwidHlwZSI6IlJUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwibSI6eyJ0eXBlIjoibiJ9LCJ2IjoiRkE2Mk4wIn0.vIfnR1RG69lqB0Dlfy-vB7OQGL32CezHdZQXRXRkHig',
        'K-ACTION': 'null',
        'vd': 'VI6C522DFEDDDB47B094DBAB8FB82537CC-1707110391153-52.1712039145.1712039145.162207728',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19816%7CMCMID%7C88087235322683450901903204835359161911%7CMCAAMLH-1712211807%7C12%7CMCAAMB-1712643946%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1712046346s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t12NCs/Pz8/Pxk/P3A/Pz8JCuxBp8CZTkB6LhkuhmGxb3OZDRSvEpQiuwSBYjDolxx3NUwQmcjYwfQ5cOfkx/edsg==',
        'CURRENT_TENANT': 'BSS',
        '_csrf': '7S6DGRDbnuz7EYAcagR-y80A',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTI3MjI2ODEsImlhdCI6MTcxMjcyMDg4MSwiaXNzIjoia2V2bGFyIiwianRpIjoiMThjZDE5YjEtZjk0NC00MTMyLTgxNGItM2FmZDViZmFlYmNkIiwidHlwZSI6IkFUIiwiZElkIjoiY2xyMXB1cDI1MmJxcDB4MHdlanBlMWFqbyIsImJJZCI6IkhHRlQ1QSIsImtldklkIjoiVklEMDZDOTNGNjQ0MkE0RUZBQUEwNTdCQTI4NjBDNEQ4MSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.BAIl-1dv2qOmSx2Nt9xmIdzQtzXy-s1mgKPbfkBxj04',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTI3MjE1MTIsImV4cCI6MTcxMjcyMjExMn0.yL6474ZmhuKlBxea5pEaYffwyafDdS8YehqYh-axIwU',
        '_ga_ZPGRNTNNRT': 'GS1.1.1712720879.246.1.1712721768.0.0.0',
        'nonce': 'ss-1905968056',
}

    for key in cookie_dict.keys():
        if key in cookies_x:
            cookies_x[key] = cookie_dict[key]




    headers = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://advertising.flipkart.com',
    'Pragma': 'no-cache',
    'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/BEN3ALHQBTDF/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'accept': '*/*',
    'apollographql-client-name': 'Flipkart-Ads',
    'apollographql-client-version': '1.0.0',
    'content-type': 'application/json',
    'downlink': '9.7',
    'dpr': '1.25',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'viewport-width': '1083',
    'x-aaccount': '4616HEEMH03Q',
    'x-baccount': 'org-9J4HV93IJV',
    'x-csrf-token': 'rt0HAo8z-ZHskDyIb6pmpo60yvFLZMvpFP8g',
    'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/BEN3ALHQBTDF/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=1',
    'x-tenant': 'BSS',
}

    json_data = {
        'operationName': 'GetCampaign',
        'variables': {
            'seller': False,
            'adProduct': 'BRAND_PCA',
            'id': campaign_id[0],
        },
        'query': 'query GetCampaign($id: String!, $adProduct: String!, $seller: Boolean! = false) {\n  getCampaignForId(id: $id, adProduct: $adProduct) {\n    ... on CampaignPLAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        fsnIds\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        withPreferredSellers\n        preferredSellerIds\n        preferredSellerNames\n        businessZones\n        tillBudgetEnds\n        fsnMeta {\n          id\n          title\n          image\n          minListingPrice\n          maxListingPrice\n          listingCurrency\n          brand\n          storeList\n          __typename\n        }\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        productCount\n        commodityId\n        cost\n        budget\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        storePaths\n        fsnBanners {\n          id\n          fsnId\n          __typename\n        }\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      preferredSellers {\n        alias\n        sellerId\n        __typename\n      }\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignPCAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        startDate\n        endDate\n        costModel\n        marketplace\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        excludeKeywords\n        marketplace\n        showAdInBroadMatchStores\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        allowedActions\n        pacing\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            creativeTemplateId\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              assetId\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              __typename\n            }\n            isSelected\n            id\n            language\n            __typename\n          }\n          collectionUrl\n          landingPageUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isPreferredSeller\n          creativeTemplateId\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignDisplayAdsResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        budgetType\n        adFormat\n        publisher\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        allowedActions\n        marketplace\n        pacing\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            videoMediaStatus\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              isSystemAsset\n              __typename\n            }\n            isSelected\n            id\n            __typename\n          }\n          collectionUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isUrlSystemCreated\n          landingPageUrl\n          status\n          isPreferredSeller\n          __typename\n        }\n        frequencyCapping {\n          interval\n          value\n          numberOfIntervals\n          __typename\n        }\n        customScheduling\n        channels\n        userTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        contextTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      __typename\n    }\n    __typename\n  }\n  getAdAccountDetails @skip(if: $seller) {\n    marketplaceConfigurationResponse {\n      marketplaceList\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PlacementsFragment on CostVariationType {\n  placements {\n    absoluteCost\n    percentage\n    type\n    pageType\n    __typename\n  }\n  __typename\n}\n\nfragment PlacementsMetaInfoFragement on PlacementsMeta {\n  type\n  title\n  detail\n  pageType\n  __typename\n}\n',
    }
    

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_x, headers=headers, json=json_data)
    x = json.loads(response.text)
    campaign_id = x["data"]["getCampaignForId"]["campaignInfo"]["id"]
    campaign_type = x["data"]["getCampaignForId"]["campaignInfo"]["name"]
    campaign_status = x["data"]["getCampaignForId"]["campaignInfo"]["status"]
    campaign_currency = x["data"]["getCampaignForId"]["campaignInfo"]["currency"]
    campaign_paymentType = x["data"]["getCampaignForId"]["campaignInfo"]["paymentType"]
    campaign_budget = x["data"]["getCampaignForId"]["campaignInfo"]["budget"]
    campaign_budgetType = x["data"]["getCampaignForId"]["campaignInfo"]["budgetType"]
    campaign_startDate = x["data"]["getCampaignForId"]["campaignInfo"]["startDate"]
    campaign_endDate = x["data"]["getCampaignForId"]["campaignInfo"]["endDate"]
    campaign_costModel = x["data"]["getCampaignForId"]["campaignInfo"]["costModel"]
    campaign_marketplace = x["data"]["getCampaignForId"]["campaignInfo"]["marketplace"]
    campaign_name_ad = x["data"]["getCampaignForId"]["adGroups"][0]["id"]
    campaign_ad_status = x["data"]["getCampaignForId"]["adGroups"][0]["status"]
    campaign_ad_ui_status = x["data"]["getCampaignForId"]["adGroups"][0]["uiStatus"]
    campaign_ad_start = x["data"]["getCampaignForId"]["adGroups"][0]["startDate"]
    campaign_ad_end = x["data"]["getCampaignForId"]["adGroups"][0]["endDate"]
    campaign_ad_cost = x["data"]["getCampaignForId"]["adGroups"][0]['cost']
    campaign_ad_budget = x["data"]["getCampaignForId"]["adGroups"][0]["budget"]
    campaign_ad_excludeKeywords = x["data"]["getCampaignForId"]["adGroups"][0]["excludeKeywords"]
    campaign_ad_marketplace = x["data"]["getCampaignForId"]["adGroups"][0]["marketplace"]
    campaign_ad_costVariation = x["data"]["getCampaignForId"]["adGroups"][0]["costVariation"]['placements']
    placement = [{k: v for k, v in item.items() if k not in ['pageType', '__typename']} for item in campaign_ad_costVariation]
    campaign_ad_marketplace = x["data"]["getCampaignForId"]["adGroups"][0]["marketplace"]
    campaign_content_id = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["contentId"]
    campaign_creative_id = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["creativeBanners"][0]["creativeId"]
    campaign_name = x["data"]["getCampaignForId"]["campaignInfo"]["name"]
    campaign_pacing = x["data"]["getCampaignForId"]["adGroups"][0]["pacing"]
    campaign_creative_template_id = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["creativeBanners"][0]["creativeTemplateId"]
    campaign_media_id = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["creativeBanners"][0]["mediaId"]
    campaign_creative_name = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["creativeBanners"][0]["creativeName"]
    campaign_store_id = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["stores"][0]["storeId"]
    campaign_store_name = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["stores"][0]["storeName"]
    campaign_type = x["data"]["getCampaignForId"]["campaignInfo"]["type"]
    campaign_collection_url = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["collectionUrl"]
    campaign_targeting_type = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][0]['type']
    campaign_targeting_pages = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][0]['pages']
    campaign_targeting_kw_exclude = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][0]['excludeKeywords']
    campaign_targeting_kw_includee = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][0]['includeKeywords']
    campaign_targeting_kw_include = [{k: v for k, v in item.items() if k not in ['pageType', '__typename']} for item in campaign_targeting_kw_includee]
    campaign_targeting_names = x["data"]["getCampaignForId"]["adGroups"][0]["name"]
    campaign_store_brand = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["brands"]
    campaign_adgrp_exculde_kw = x["data"]["getCampaignForId"]["adGroups"][0]['excludeKeywords']
    campaign_page_target = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][1]["type"]
    campaign_page_pages = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][1]["pages"]
    campaign_page_exc_kw = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][1]["excludeKeywords"]
    campaign_page_inc_kw = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"][1]["includeKeywords"]
    # print(placement)
    # exit()

    ###########################################budget_main#####################################################
    
    cookies_y = {
        'T': 'TI169891842149300161944937865135939588577615020537527148270186391420',
        '_pxvid': 'c6c61fc1-7964-11ee-8e5a-1d67ccbdf2e0',
        'dpr': '1.25',
        '_fbp': 'fb.1.1700471257731.638459595',
        '_ga_B9RGC9GN63': 'GS1.1.1702722512.1.1.1702722682.54.0.0',
        'DID': 'clr1pup252bqp0x0wejpe1ajo',
        'ULSN': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjb29raWUiLCJhdWQiOiJmbGlwa2FydCIsImlzcyI6ImF1dGguZmxpcGthcnQuY29tIiwiY2xhaW1zIjp7ImdlbiI6IjEiLCJ1bmlxdWVJZCI6IlVVSTI0MDIxNDEyNTQxMjc4NE85TU9OTE0iLCJma0RldiI6bnVsbH0sImV4cCI6MTcyMzY3NTQ1MiwiaWF0IjoxNzA3ODk1NDUyLCJqdGkiOiIzZmIzYjAxZS02MzU2LTRjM2ItYTg3Yi1lNDQ3ZWNmMWJiYzEifQ.qbw3LDnvt96oOTYcrXvedJeOeJteVaWqgwkYlaKjyuw',
        'vh': '730',
        'vw': '1536',
        '_ga_0RGM1K38MN': 'GS1.2.1708195526.2.1.1708195657.0.0.0',
        '_ga_C00F4Q43Q7': 'GS1.2.1708196044.1.0.1708196044.0.0.0',
        '_gcl_au': '1.1.856723108.1708257205',
        'ud': '3.-hCuLDZfVJf9kwEcWhK4arj09yD35YGA9WD7yo1zRPr-6c1rmX2_xdHegqPpB3V8IXYz3NsAnP3SBWNaEKufBfykm01W9EISet6O__tpbwLut1-EZphHbJ0c9MzW0rczeRXhalfDVODMz8JTNMlQlgc9FtPFTSU9rNePFCXS_okASoEjAhPorkspIuB6dUcZtsYfTSEOj6D6fCfEhHGTX040PuZMdyiyk409VK7VDUArNQCXrRjfusSZdRR_dSa_IYardO48M5GyGz8FGpTkPTBYE_1zDB-5NXEc93lP2wklWoHEa-Dtp_7e6v2PvoLYEnO9q9WRO923E1MzbxEsgQzTal18ocz6m1QhVKcLAkifQY1CVPvSCEDYAhYysg7Cifn25pVGYReJE-wqKz__XeZKWQ6m9S5ylJWi8ZCNic_rQWkW8tl4jP7uwPxupbq0hBk3YeSRAVvcjX09zDY5qn4jmi-pJicw3oOin6BBwh5j4AEuCE1_UBhyu1FzQ6HXVin354_zqMKmt5Ez4awQztwLbxHMqBrzPLNw1nVv-mMH56A0UIV523BaT7wlgFXFKDY9PgZuquXJtkpqqSSPK3sdeoBmL_SsoP5XdHnW3U3lvtJigEiuV1-2In3wufWsqsHYvXC8tj7Vr6X8srs_3ehJ7eFh0ZMdB7QsQTCynabS2sW3gILSeLC2-NwmdaemzanTaScNERb6Z6uBV6aYgxLtiUZZci5cqwxPaCVTIRHxdKh90EtL6MagI-T8KaMNUkYxg3mOLw4UnS1OIQr5vw',
        '_ga_2P94RMW04V': 'GS1.2.1711394187.7.1.1711394237.0.0.0',
        'AMCV_55CFEDA0570C3FA17F000101%40AdobeOrg': '-227196251%7CMCIDTS%7C19815%7CMCMID%7C83672356534473986601461754159478791217%7CMCAAMLH-1712558585%7C12%7CMCAAMB-1712558585%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1711960985s%7CNONE%7CMCAID%7CNONE',
        'mp_9ea3bc9a23c575907407cf80efd56524_mixpanel': '%7B%22distinct_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24device_id%22%3A%20%2218bf5c79f2b403-04403e63bfeec8-26031051-144000-18bf5c79f2ca33%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fseller.flipkart.com%2Fsell-online%2Fmulti-select%22%2C%22%24initial_referring_domain%22%3A%20%22seller.flipkart.com%22%2C%22%24user_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24search_engine%22%3A%20%22google%22%7D',
        '_ga': 'GA1.1.1819741834.1700633034',
        's_nr': '1711953817499-Repeat',
        '_ga_0SJLGHBL81': 'GS1.1.1711963800.32.0.1711963800.0.0.0',
        '_ga_TVF0VCMCT3': 'GS1.1.1711963800.153.0.1711963800.60.0.0',
        'SN': 'VI6C522DFEDDDB47B094DBAB8FB82537CC.TOK635F5023E626455C82262BA71755319E.1712039145.LI',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNhNzdlZTgxLTRjNWYtNGU5Ni04ZmRlLWM3YWMyYjVlOTA1NSJ9.eyJleHAiOjE3MTIwNDA5NDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZWNhMjk4YmItYjg2OS00NDUzLWFmN2QtYmRmNTMxMzRkOTUxIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwiZWFJZCI6ImJlMHVRSWdQSVRwMlpxYW5OTmhobkdIamhSdi1QMVhOTmNURnloQS16QVNBWU40QlZ2NF9Odz09IiwidnMiOiJMSSIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QlU14s5wGMPi9nFMdwxMyzDo4smmVhEtrHlqVyVhTNk',
        'rt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhlM2ZhMGE3LTJmZDMtNGNiMi05MWRjLTZlNTMxOGU1YTkxZiJ9.eyJleHAiOjE3Mjc4NTAzNDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiNDIzZjU0NzUtNTlkNC00MDg1LWFiODctOGU0MDE0NGVkMzhlIiwidHlwZSI6IlJUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwibSI6eyJ0eXBlIjoibiJ9LCJ2IjoiRkE2Mk4wIn0.vIfnR1RG69lqB0Dlfy-vB7OQGL32CezHdZQXRXRkHig',
        'K-ACTION': 'null',
        'vd': 'VI6C522DFEDDDB47B094DBAB8FB82537CC-1707110391153-52.1712039145.1712039145.162207728',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19816%7CMCMID%7C88087235322683450901903204835359161911%7CMCAAMLH-1712211807%7C12%7CMCAAMB-1712643946%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1712046346s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t12NCs/Pz8/Pxk/P3A/Pz8JCuxBp8CZTkB6LhkuhmGxb3OZDRSvEpQiuwSBYjDolxx3NUwQmcjYwfQ5cOfkx/edsg==',
        '_csrf': '7S6DGRDbnuz7EYAcagR-y80A',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTI3NjEwNzcsImlhdCI6MTcxMjc1OTI3NywiaXNzIjoia2V2bGFyIiwianRpIjoiNjcyOWQ1NDQtZTM1NC00NTVkLWFmZDctNmI5NWY5MThlZDg5IiwidHlwZSI6IkFUIiwiZElkIjoiY2xyMXB1cDI1MmJxcDB4MHdlanBlMWFqbyIsImJJZCI6IkhUVkFVUyIsImtldklkIjoiVklBQkY3MTJENTg0NzI0MDE5OEI4ODE3OEQwRTI4MDMzNSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.jv5V0eaIWK31eoOVrp0gpw7879waSNjwU15LhwAM9UE',
        'CURRENT_TENANT': 'BSS',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwic3VjY2VzcyI6dHJ1ZSwidGVuYW50IjoiQlNTIiwiYWFjY291bnQiOnt9LCJpYXQiOjE3MTI3NTkyNzcsImV4cCI6MTcxMjc1OTg3N30.5zwSGVfgsludpEoB2Y9L26dKNzzIKKIm6Tev4tYiKmg',
        '_ga_ZPGRNTNNRT': 'GS1.1.1712759274.251.1.1712759372.0.0.0',
        'nonce': 'ss-399089435',
    }

    for key in cookie_dict.keys():
        if key in cookies_y:
            cookies_y[key] = cookie_dict[key]



    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://advertising.flipkart.com',
        'Pragma': 'no-cache',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/BEN3ALHQBTDF/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=2',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '10',
        'dpr': '1.25',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '936',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': 'cAFI9lY3-joXqDWj34cDRZ2J5dn7DgSn2WHk',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/BEN3ALHQBTDF/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=2',
        'x-tenant': 'BSS',
}

    json_data = {
        'operationName': 'UpdatePCACampaign',
        'variables': {
            'data': {
                'adGroups': [
                    {
                        'name': campaign_targeting_names,
                        'cost': campaign_ad_cost,
                        'startDate': campaign_ad_start,
                        'endDate': campaign_ad_end,
                        'costModel': campaign_costModel,
                        'budget': campaign_ad_budget,
                        'pacing': campaign_pacing,
                        'marketplace': campaign_marketplace,
                        'excludeKeywords': campaign_adgrp_exculde_kw,
                        'contents': [
                            {
                                'collectionUrl': campaign_collection_url,
                                'landingPageUrl': '',
                                'contentId': campaign_content_id,
                                'creativeTemplateId': campaign_creative_template_id,
                                'isPreferredSeller': True,
                                'name': 'PCA_CONTENT',
                                'creatives': [
                                    {
                                        'creativeId':  campaign_creative_id,
                                        'creativeName': campaign_creative_name,
                                        'creativeTemplateId': campaign_creative_template_id,
                                        'creativeType': 'MANUAL',
                                        'isSelected': True,
                                        'creativeImage': {
                                            'mediaId': campaign_media_id,
                                            'mediaName': 'PCA Media',   #yeh ni mila
                                            'url': 'https://rukminim1.flixcart.com/fk-p-ads/{@width}/{@height}/dp-doc/1712384645187-clunplsg33q970qg1xotd87p3-aloe-body-lotions_PCA.jpg?q={@quality}',#yeh ni mila
                                            'mediaType': 'IMAGE', #Yen ni mila
                                            'altText': 'PCA Media',
                                            'preApproved': True,
                                            'locales': [
                                                'en',
                                            ],
                                            'widgetType': [
                                                'FLEXIBLE_BANNER',
                                            ],
                                        },
                                    },
                                ],
                                'brands':campaign_store_brand,
                                'stores': {
                                    'storeId': campaign_store_id ,
                                    'storeName': campaign_store_name,
                                },
                            },
                        ],
                        'id': 'EQPZBLAW5A29',
                        'showAdInBroadMatchStores': False,
                        'costVariation': {
                            'placements': placement_dict
                        },
                        'targeting': [
                            {
                                'type': campaign_targeting_type,
                                'pages': campaign_targeting_pages,
                                'excludeKeywords': campaign_targeting_kw_exclude,
                                'includeKeywords': campaign_targeting_kw_include,
                            } if campaign_targeting_type is not None else {},
                            {
                                'type': campaign_page_target,    # yha pr kch mjhe krna pdega
                                'pages': campaign_page_pages,
                                'excludeKeywords': campaign_page_exc_kw,
                                'includeKeywords': campaign_page_inc_kw,
                            } if campaign_page_target is not None else {},
                        ],
                    },
                ],
                'campaignInfo': {
                    'budget': campaign_budget,    #budget change kr lo
                    'costModel': campaign_costModel,
                    'endDate': None,
                    'marketplace': campaign_marketplace,
                    'name': campaign_name,                  #idr name change kro
                    'startDate': campaign_startDate,
                    'tillBudgetEnds': True,
                    'type': campaign_type,
                    'budgetType': campaign_budgetType,
                },
            },
            'id': campaign_id,
        },
        'query': 'mutation UpdatePCACampaign($data: SaveCampaignPayload!, $id: String!) {\n  updateCampaign(data: $data, id: $id) {\n    ...CampaignPCAFragment\n    __typename\n  }\n}\n\nfragment CampaignPCAFragment on CampaignPCAResponse {\n  campaignInfo {\n    id\n    status\n    uiStatus\n    startDate\n    endDate\n    costModel\n    pacing\n    type\n    budget\n    name\n    grossBudget\n    budgetType\n    marketplace\n    allowedActions\n    __typename\n  }\n  adGroups {\n    id\n    contents {\n      contentId\n      collectionUrl\n      isPreferredSeller\n      creativeTemplateId\n      creativeBanners {\n        creativeId\n        creativeName\n        status\n        creativeTemplateId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_y, headers=headers, json=json_data)
    print(response.text)
    i+=1






