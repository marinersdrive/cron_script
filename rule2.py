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
cursor.execute("SELECT MAX(Date) FROM fk_pla_nivea;")
max_date = cursor.fetchone()[0]
max_date = max_date.date()

rule_id = 1655
cursor = connection.cursor()
sql = "SELECT * FROM rule_table_bkp WHERE rule_id = %s"
cursor.execute(sql, (rule_id,))
fetched_data = cursor.fetchall()

column_mapping = {
    "spends": "Ad_Spend",
    "impression": "Views",
    "clicks": "Clicks",
    "ctr": "CTR",
    "created_on": "Date",
    "placement_type": "Placement_Type",
    "status": "Status"
}


data = {
    "platform_name": [str(fetched_data[0][0])],
    "pf_id": [str(fetched_data[0][1])],
    "user_id": [str(fetched_data[0][2])],
    "user_name": [str(fetched_data[0][3])],
    "rule_name": [str(fetched_data[0][4])],
    "rule_id": [str(fetched_data[0][5])],
    "spends": [str(fetched_data[0][6])],
    "spends_op": [str(fetched_data[0][7])],
    "sales": [str(fetched_data[0][8])],
    "sales_op": [str(fetched_data[0][9])],
    "roas": [str(fetched_data[0][10])],
    "roas_op": [str(fetched_data[0][11])],
    "troas": [str(fetched_data[0][12])],
    "troas_op": [str(fetched_data[0][13])],
    "impression": [str(fetched_data[0][14])],
    "impression_op": [str(fetched_data[0][15])],
    "clicks": [str(fetched_data[0][16])],
    "clicks_op": [str(fetched_data[0][17])],
    "ctr": [str(fetched_data[0][18])],
    "ctr_op": [str(fetched_data[0][19])],
    "created_on": [fetched_data[0][20].strftime('%Y-%m-%d %H:%M:%S')],
    "operation_name": [str(fetched_data[0][21])],
    "operation_type": [str(fetched_data[0][22])],
    "report_type": [str(fetched_data[0][23])],
    "placement_type": [str(fetched_data[0][24])],
    "frequency": [str(fetched_data[0][25])],
    "limit_type": [str(fetched_data[0][26])],
    "limit_value": [str(fetched_data[0][27])],
    "status": [str(fetched_data[0][28])]
}

df = pd.DataFrame(data)

operator_mapping = {
    "eq": "=",
    "neq": "!=",
    "gt": ">",
    "lt": "<",
    "gte": ">=",
    "lte": "<="
}

conditions = []
for index, row in df.iterrows():
    for column in df.columns:
        if column.endswith('_op') and row[column] != '0' and row[column.replace('_op', '')] != '0':
            operator = operator_mapping.get(row[column], row[column])
            value = row[column.replace('_op', '')]
            column_name = column.replace('_op', '')
            if column_name in ["spends", "impression", "clicks", "ctr", "created_on", "placement_type", "status"]:
                column_name = column_mapping.get(column_name, column_name)
            conditions.append(f"{column_name} {operator} {value}")
conditions.append("platform_name = '{}'".format(data["platform_name"][0]))
if conditions:
    query = "SELECT DISTINCT(Campaign_ID) FROM  fk_pla_nivea WHERE TYPE='PCA' AND " + " AND ".join(conditions) 
    print(query)
    cursor.execute(query)
    campaign_ids_pca = cursor.fetchall()
else:
    print("No conditions found.")

# print(campaign_ids_pca)
# campaign_ids_pca = [row[0] for row in campaign_ids_pca]

if campaign_ids_pca:
    for campaign_id_pca in campaign_ids_pca:
        print(campaign_id_pca)
        
else:
    print("No campaigns found")

exit()



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
placement_dict = []

for campaign_id_pca in campaign_ids_pca:
    campaign_id_pca=campaign_id_pca[0]
    print(campaign_id_pca)
    # cursor.execute("SELECT MAX(Date) FROM fk_pla_nivea WHERE  Campaign_ID = %s ;", (campaign_id_pca,))
    # max_date = cursor.fetchone()[0]
    # max_date = max_date.date()
    
    # cursor.execute("SELECT Absolute_Cost, Percentage, Placement_Type FROM fk_pla_nivea WHERE Campaign_ID = %s AND DATE(Date) = %s", (campaign_id_pca, max_date))

    
    # placements = cursor.fetchall()
    
    
    # print(campaign_id[i])
    # exit()
    

    ###########################support_pca####################
    
    cookies_x = {
        'DID': 'cltfsxlmh69cj0x080ko71pv7',
        '_ga': 'GA1.1.1167863333.1709729726',
        'T': 'TI171041253423100159177482711189994566661456194141317532355081987438',
        'rt': 'null',
        'K-ACTION': 'null',
        '_pxvid': '97877fb5-e1ee-11ee-848c-42c3808d2940',
        'ud': '2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ',
        'vh': '607',
        'vw': '1366',
        'dpr': '1',
        'CURRENT_TENANT': 'BSS',
        '_csrf': 'pxTCMbPA-LkqH17yl01k1Svh',
        'TENANT': 'BSS',
        'SN': 'VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A',
        'vd': 'VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413',
        'pxcts': '68c93d81-fe3a-11ee-9bdf-782a4a118d40',
        'AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg': '1',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1Mjc3NDQsImlhdCI6MTcxMzUyNTk0NCwiaXNzIjoia2V2bGFyIiwianRpIjoiZTE4OGZkYTEtNDI2NC00MTMwLTgxOTctZjZiNWFiYWU1NGEwIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IjZNRkkwMiIsImtldklkIjoiVklBNDY5MjZFMTc3RjQ0NDhDODFGMDVCRjlCOUE2RDFFNCIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.kPPyPCT_b2rFJYCbKNzYB0uH2a8A-yB4JnEeheLqXoQ',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM1MjYyNzcsImV4cCI6MTcxMzUyNjg3N30.iCfC90S8eY2RzDJhTKB2Ww-128byDKFLujwxfNToRek',
        'nonce': 'ss-2899789514',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713515946.8.1.1713526478.0.0.0',
    }

    for key in cookie_dict.keys():
        if key in cookies_x:
            cookies_x[key] = cookie_dict[key]

    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'DID=cltfsxlmh69cj0x080ko71pv7; _ga=GA1.1.1167863333.1709729726; T=TI171041253423100159177482711189994566661456194141317532355081987438; rt=null; K-ACTION=null; _pxvid=97877fb5-e1ee-11ee-848c-42c3808d2940; ud=2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ; vh=607; vw=1366; dpr=1; CURRENT_TENANT=BSS; _csrf=pxTCMbPA-LkqH17yl01k1Svh; TENANT=BSS; SN=VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A; vd=VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413; pxcts=68c93d81-fe3a-11ee-9bdf-782a4a118d40; AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg=1; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE; S=d1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1Mjc3NDQsImlhdCI6MTcxMzUyNTk0NCwiaXNzIjoia2V2bGFyIiwianRpIjoiZTE4OGZkYTEtNDI2NC00MTMwLTgxOTctZjZiNWFiYWU1NGEwIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IjZNRkkwMiIsImtldklkIjoiVklBNDY5MjZFMTc3RjQ0NDhDODFGMDVCRjlCOUE2RDFFNCIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.kPPyPCT_b2rFJYCbKNzYB0uH2a8A-yB4JnEeheLqXoQ; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM1MjYyNzcsImV4cCI6MTcxMzUyNjg3N30.iCfC90S8eY2RzDJhTKB2Ww-128byDKFLujwxfNToRek; nonce=ss-2899789514; _ga_ZPGRNTNNRT=GS1.1.1713515946.8.1.1713526478.0.0.0',
        'Origin': 'https://advertising.flipkart.com',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '10',
        'dpr': '1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '952',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': '09I13gAj-1V1ZcxgXsN5PwSF7-lDYo3SPQSE',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q',
        'x-tenant': 'BSS',
    }
    
    
    json_data = {
        'operationName': 'GetCampaign',
        'variables': {
            'seller': False,
            'adProduct': 'BRAND_PCA',
            'id': campaign_id_pca,  #pass campaignId
        },
        'query': 'query GetCampaign($id: String!, $adProduct: String!, $seller: Boolean! = false) {\n  getCampaignForId(id: $id, adProduct: $adProduct) {\n    ... on CampaignPLAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        fsnIds\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        withPreferredSellers\n        preferredSellerIds\n        preferredSellerNames\n        businessZones\n        tillBudgetEnds\n        fsnMeta {\n          id\n          title\n          image\n          minListingPrice\n          maxListingPrice\n          listingCurrency\n          brand\n          storeList\n          __typename\n        }\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        productCount\n        commodityId\n        cost\n        budget\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        storePaths\n        fsnBanners {\n          id\n          fsnId\n          __typename\n        }\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      preferredSellers {\n        alias\n        sellerId\n        __typename\n      }\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignPCAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        startDate\n        endDate\n        costModel\n        marketplace\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        excludeKeywords\n        marketplace\n        showAdInBroadMatchStores\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        allowedActions\n        pacing\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            creativeTemplateId\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              assetId\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              __typename\n            }\n            isSelected\n            id\n            language\n            __typename\n          }\n          collectionUrl\n          landingPageUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isPreferredSeller\n          creativeTemplateId\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignDisplayAdsResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        budgetType\n        adFormat\n        publisher\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        allowedActions\n        marketplace\n        pacing\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            videoMediaStatus\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              isSystemAsset\n              __typename\n            }\n            isSelected\n            id\n            __typename\n          }\n          collectionUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isUrlSystemCreated\n          landingPageUrl\n          status\n          isPreferredSeller\n          __typename\n        }\n        frequencyCapping {\n          interval\n          value\n          numberOfIntervals\n          __typename\n        }\n        customScheduling\n        channels\n        userTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        contextTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      __typename\n    }\n    __typename\n  }\n  getAdAccountDetails @skip(if: $seller) {\n    marketplaceConfigurationResponse {\n      marketplaceList\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PlacementsFragment on CostVariationType {\n  placements {\n    absoluteCost\n    percentage\n    type\n    pageType\n    __typename\n  }\n  __typename\n}\n\nfragment PlacementsMetaInfoFragement on PlacementsMeta {\n  type\n  title\n  detail\n  pageType\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_x, headers=headers, json=json_data)
    print("status pca getcampaign",response.status_code)
    
    x = json.loads(response.text)
    

    campaign_id_pca = x["data"]["getCampaignForId"]["campaignInfo"]["id"]
# print(campaign_id)
# exit()
    campaign_type = x["data"]["getCampaignForId"]["campaignInfo"]["type"]

    campaign_name=x["data"]["getCampaignForId"]["campaignInfo"]["name"]

    campaign_budget = x["data"]["getCampaignForId"]["campaignInfo"]["budget"]

    campaign_budgetType = x["data"]["getCampaignForId"]["campaignInfo"]["budgetType"]

    campaign_startDate = x["data"]["getCampaignForId"]["campaignInfo"]["startDate"]

    campaign_endDate = x["data"]["getCampaignForId"]["campaignInfo"]["endDate"]

    campaign_costModel = x["data"]["getCampaignForId"]["campaignInfo"]["costModel"]

    campaign_marketplace = x["data"]["getCampaignForId"]["campaignInfo"]["marketplace"]

    ad_group_name = x["data"]["getCampaignForId"]["adGroups"][0]['name']
    ad_group_id = x["data"]["getCampaignForId"]["adGroups"][0]['id']
    ad_group_cost=x["data"]["getCampaignForId"]["adGroups"][0]['cost']
    ad_group_startdate=x["data"]["getCampaignForId"]["adGroups"][0]['startDate']
    ad_group_enddate=x["data"]["getCampaignForId"]["adGroups"][0]['endDate']

    ad_group_budget=x["data"]["getCampaignForId"]["adGroups"][0]['budget']
    ad_group_pacing=x["data"]["getCampaignForId"]["adGroups"][0]['pacing']
    ad_group_marketPlace=x["data"]["getCampaignForId"]["adGroups"][0]['marketplace']
    ad_group_excludeKeywords=x["data"]["getCampaignForId"]["adGroups"][0]['excludeKeywords']


    content = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]

    targeting = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"]
    for item in targeting:
        item.pop('__typename', None)
        include_keywords = item.get('includeKeywords')  # Get includeKeywords, if exists
        if include_keywords is not None:  # Check if includeKeywords is not None
            for keyword in include_keywords:
                keyword.pop('__typename', None)


    # print(targeting)

    placements = x["data"]["getCampaignForId"]["adGroups"][0]["costVariation"]["placements"] 
    
    for placement in placements:
        del placement['pageType']
        del placement['__typename']
    print(placements)
    
        
    for placement in placements:
        percentage_change = 100 # frontend se pass hogea
        adjusted_absolute_cost = adjust_absolute_cost(placement['absoluteCost'], percentage_change)

        cursor.execute("UPDATE fk_pla_nivea SET Absolute_Cost = %s WHERE Campaign_ID = %s AND Placement_Type = %s;",
                    (adjusted_absolute_cost, campaign_id_pca, placement['type']))
        connection.commit()

        placement_dict.append({
            'absoluteCost': float(adjusted_absolute_cost),
            'percentage': placement['percentage'],
            'type': placement['type']
        })
        
    print(placement_dict)
    # exit()
    landing_page_url = content.get("landingPageUrl")
    collection_url = content.get("collectionUrl")
    content_id = content["contentId"]
    creative_template_id = content["creativeBanners"][0]["creativeTemplateId"]
    is_preferred_seller = content.get("isPreferredSeller")
    store_name = x['data']['getCampaignForId']['adGroups'][0]['contents'][0]['stores'][0]['storeName']

    brand = x['data']['getCampaignForId']['adGroups'][0]['contents'][0]['brands']
    stores = x['data']['getCampaignForId']['adGroups'][0]['contents'][0]['stores']
    for store in stores:
        del store['__typename']

    cookies_z = {
        'DID': 'cltfsxlmh69cj0x080ko71pv7',
        '_ga': 'GA1.1.1167863333.1709729726',
        'T': 'TI171041253423100159177482711189994566661456194141317532355081987438',
        'rt': 'null',
        'K-ACTION': 'null',
        '_pxvid': '97877fb5-e1ee-11ee-848c-42c3808d2940',
        'ud': '2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ',
        'vh': '607',
        'vw': '1366',
        'dpr': '1',
        'SN': 'VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A',
        'vd': 'VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==',
        'CURRENT_TENANT': 'BSS',
        '_csrf': 'U7_Azf6qHpckxTd-H04-AMWk',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTM2MTM3MzQsImlhdCI6MTcxMzYxMTkzNCwiaXNzIjoia2V2bGFyIiwianRpIjoiMGMwOThlMzAtN2QxNS00NWQ4LTgyODUtNjIzN2FmZTBkNmU2IiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IjRNWkZETiIsImtldklkIjoiVklGRkI4MkNGQTAzNTk0NDJBOTJFRkJBQ0ZBQTQyRDc4MyIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.KGJN7jEBO4xQD-IOBTEXigvI7OBYl7GCokQLpzgTSCA',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM2MTMxNTksImV4cCI6MTcxMzYxMzc1OX0.uSKoCD-x0rohudb479RdB78Z-2fx83u_-oj91l_WTjA',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713610042.11.1.1713613543.0.0.0',
        'nonce': 'ss-485854553',
    }
    for key in cookie_dict.keys():
        if key in cookies_z:
            cookies_z[key] = cookie_dict[key]
    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'DID=cltfsxlmh69cj0x080ko71pv7; _ga=GA1.1.1167863333.1709729726; T=TI171041253423100159177482711189994566661456194141317532355081987438; rt=null; K-ACTION=null; _pxvid=97877fb5-e1ee-11ee-848c-42c3808d2940; ud=2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ; vh=607; vw=1366; dpr=1; SN=VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A; vd=VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE; S=d1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==; CURRENT_TENANT=BSS; _csrf=U7_Azf6qHpckxTd-H04-AMWk; TENANT=BSS; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTM2MTM3MzQsImlhdCI6MTcxMzYxMTkzNCwiaXNzIjoia2V2bGFyIiwianRpIjoiMGMwOThlMzAtN2QxNS00NWQ4LTgyODUtNjIzN2FmZTBkNmU2IiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IjRNWkZETiIsImtldklkIjoiVklGRkI4MkNGQTAzNTk0NDJBOTJFRkJBQ0ZBQTQyRDc4MyIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.KGJN7jEBO4xQD-IOBTEXigvI7OBYl7GCokQLpzgTSCA; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM2MTMxNTksImV4cCI6MTcxMzYxMzc1OX0.uSKoCD-x0rohudb479RdB78Z-2fx83u_-oj91l_WTjA; _ga_ZPGRNTNNRT=GS1.1.1713610042.11.1.1713613543.0.0.0; nonce=ss-485854553',
        'Origin': 'https://advertising.flipkart.com',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/NPJHPWEH4QGZ/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '10',
        'dpr': '1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '952',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': '7HrDjOHM-Ml-dFcwNEu0BAOdW5L_2aLGGXdc',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/NPJHPWEH4QGZ/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=1',
        'x-tenant': 'BSS',
    }

    json_data = {
        'operationName': 'QueryGetPCAAdgroupDetails',
        'variables': {
            'adgroupid': ad_group_id, 
            'adProduct': 'BRAND_PCA',
            'marketplace': ad_group_marketPlace,
        },
        'query': 'query QueryGetPCAAdgroupDetails($adgroupid: String!, $adProduct: String, $marketplace: String) {\n  getAdgroupInfo(adgroupid: $adgroupid, adProduct: $adProduct, marketplace: $marketplace) {\n    ...ADGROUP_DETAIL\n    __typename\n  }\n}\n\nfragment ADGROUP_DETAIL on AdGroupResponse {\n  id\n  name\n  status\n  uiStatus\n  startDate\n  endDate\n  cost\n  costModel\n  budget\n  pacing\n  collectionRules {\n    filters {\n      attribute {\n        data_type\n        display_name\n        id\n        is_whitelisted\n        type\n        whitelisted\n        __typename\n      }\n      operator\n      values\n      __typename\n    }\n    __typename\n  }\n  excludeKeywords\n  fsnIds\n  fsnMeta {\n    id\n    image\n    title\n    minListingPrice\n    maxListingPrice\n    listingCurrency\n    storeList\n    __typename\n  }\n  showAdInBroadMatchStores\n  allowedActions\n  campaignName\n  campaignId\n  marketplace\n  costVariation {\n    ...PlacementsFragment\n    __typename\n  }\n  contents {\n    contentId\n    creativeBanners {\n      creativeId\n      creativeName\n      creativeTemplateId\n      uiStatus\n      status\n      allowedActions\n      referenceId\n      mediaId\n      creativeType\n      assets {\n        macro\n        value\n        type\n        origin\n        assetId\n        __typename\n      }\n      isSelected\n      id\n      language\n      __typename\n    }\n    collectionUrl\n    collectionId\n    landingPageUrl\n    collectionType\n    brands\n    isPreferredSeller\n    creativeTemplateId\n    stores {\n      storeId\n      storeName\n      __typename\n    }\n    __typename\n  }\n  targeting {\n    type\n    pages\n    excludeKeywords {\n      q\n      r\n      __typename\n    }\n    includeKeywords {\n      q\n      r\n      matchType\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlacementsFragment on CostVariationType {\n  placements {\n    absoluteCost\n    percentage\n    type\n    pageType\n    __typename\n  }\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_z, headers=headers, json=json_data)
    # print(response.text)
    print("status pca pca adgrouo details",response.status_code)
    
    y = json.loads(response.text)

    assets = []
    for content in y['data']['getAdgroupInfo']['contents']:
        for banner in content['creativeBanners']:
            for asset in banner['assets']:
                # Remove the '__typename' field
                asset.pop('__typename', None)
                assets.append(asset)
            
            
    print(assets)



    creative_banners_list = x["data"]["getCampaignForId"]["adGroups"][0]["contents"][0]["creativeBanners"]
    print("*************************************************************************************")

    print("length:  ",len(creative_banners_list))

    media_ids = []
    print("==============================================================================================")
    for item in creative_banners_list:
        creative_id = item['creativeId']
        creative_name = item['creativeName']
        creative_template_id = item['creativeTemplateId']
        creative_type = item['creativeType']
        is_selected = item['isSelected']
        media_id = item['mediaId']
        language = item['language']
        widgetType = item['__typename']
        ui_status = item['uiStatus']
        status = item['status']
        allowed_actions = item['allowedActions']
        reference_id = item['referenceId']
        # assets = item['assets']
        id_value = item['id']
        media_ids.append(media_id)



    contents = []
    for item in creative_banners_list:
        creative_id = item['creativeId']
        creative_name = item['creativeName']
        creative_template_id = item['creativeTemplateId']
        creative_type = item['creativeType']
        is_selected = item['isSelected']
        media_id = item['mediaId']
        language = item['language']
        widgetType = item['__typename']
        # assets=item['assets']
        
        creative = {
            'creativeId': creative_id,
            'creativeName': creative_name,
            'creativeTemplateId': creative_template_id,
            'creativeType': creative_type,
            'isSelected': is_selected,
            'assets':assets,
            'creativeImage': {
                'mediaId': media_id,
                'mediaName': 'PCA Media',
                'url': None,
                'mediaType': 'IMAGE',
                'altText': 'PCA Media',
                'preApproved': True,
                'locales': [language],
                'widgetType': [widgetType],
            },
        }
        contents.append(creative)
        


    cookies_y = {
        'DID': 'cltfsxlmh69cj0x080ko71pv7',
        '_ga': 'GA1.1.1167863333.1709729726',
        'T': 'TI171041253423100159177482711189994566661456194141317532355081987438',
        'rt': 'null',
        'K-ACTION': 'null',
        '_pxvid': '97877fb5-e1ee-11ee-848c-42c3808d2940',
        'ud': '2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ',
        'vh': '607',
        'vw': '1366',
        'dpr': '1',
        'SN': 'VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A',
        'vd': 'VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==',
        '_csrf': 'rO4QHqBgjWI0g3iO6d3_rJuF',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1OTA2NzMsImlhdCI6MTcxMzU4ODg3MywiaXNzIjoia2V2bGFyIiwianRpIjoiYzEwNjg0ODAtZGJkNi00MzlmLWI1YTctZTgxMTdiMjI4ZmFiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IlZDSEhRQSIsImtldklkIjoiVklEMTFCNTY2NzE2RTk0RjY1OUUzOEM3RTMwOTdFREJCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.mnE6p-1xEVEQYr7YdB6oCDg8AH7Slxl8R5yS0SoL41E',
        'CURRENT_TENANT': 'BSS',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwic3VjY2VzcyI6dHJ1ZSwidGVuYW50IjoiQlNTIiwiYWFjY291bnQiOnt9LCJpYXQiOjE3MTM1ODg4NzQsImV4cCI6MTcxMzU4OTQ3NH0.Tyy4PbipLQGfjiskV1WwForVcp11uCAky2YiaSl1MlQ',
        'nonce': 'ss-1540632417',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713588775.9.1.1713589301.0.0.0',
    }

    for key in cookie_dict.keys():
        if key in cookies_y:
            cookies_y[key] = cookie_dict[key]

    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'DID=cltfsxlmh69cj0x080ko71pv7; _ga=GA1.1.1167863333.1709729726; T=TI171041253423100159177482711189994566661456194141317532355081987438; rt=null; K-ACTION=null; _pxvid=97877fb5-e1ee-11ee-848c-42c3808d2940; ud=2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ; vh=607; vw=1366; dpr=1; SN=VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A; vd=VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE; S=d1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==; _csrf=rO4QHqBgjWI0g3iO6d3_rJuF; TENANT=BSS; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1OTA2NzMsImlhdCI6MTcxMzU4ODg3MywiaXNzIjoia2V2bGFyIiwianRpIjoiYzEwNjg0ODAtZGJkNi00MzlmLWI1YTctZTgxMTdiMjI4ZmFiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IlZDSEhRQSIsImtldklkIjoiVklEMTFCNTY2NzE2RTk0RjY1OUUzOEM3RTMwOTdFREJCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.mnE6p-1xEVEQYr7YdB6oCDg8AH7Slxl8R5yS0SoL41E; CURRENT_TENANT=BSS; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwic3VjY2VzcyI6dHJ1ZSwidGVuYW50IjoiQlNTIiwiYWFjY291bnQiOnt9LCJpYXQiOjE3MTM1ODg4NzQsImV4cCI6MTcxMzU4OTQ3NH0.Tyy4PbipLQGfjiskV1WwForVcp11uCAky2YiaSl1MlQ; nonce=ss-1540632417; _ga_ZPGRNTNNRT=GS1.1.1713588775.9.1.1713589301.0.0.0',
        'Origin': 'https://advertising.flipkart.com',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&adgroupid=A99UOINYJZES&substep=2',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '10',
        'dpr': '1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '952',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': 'YJoF03HC-1lAUZNiKILIwDwhseHIPvm2ZorI',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&adgroupid=A99UOINYJZES&substep=2',
        'x-tenant': 'BSS',
    }

    json_data = {
        'operationName': 'GET_CREATIVE_DETAILS',
        'variables': {
            'data': {
                'brands': brand,
                'collectionUrl': collection_url,
                'requestType': 'PCA_CREATE',
                'storeTitle': store_name,
                'dpr': 1,
                'contentId': content_id,
                'creativesInfo': {
                    'mediaIds': media_ids,
                    'externalCreativeIds': [],
                },
                'recommendedCreativesRequired': False,
                'language':language ,
                'creativeReferenceIds': [],
            },
        },
        'query': 'query GET_CREATIVE_DETAILS($data: CreativeInput) {\n  getCreatives(data: $data) {\n    creativeDetails {\n      logoCreative {\n        ...CREATIVE\n        __typename\n      }\n      productCreative {\n        ...CREATIVE\n        __typename\n      }\n      __typename\n    }\n    manualCreativeImageUrls {\n      medias\n      externalCreatives\n      __typename\n    }\n    contentRejectionInfo {\n      rejectedCreatives {\n        creativeId\n        rejectionReasons {\n          macro\n          reasons\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    collectionId\n    __typename\n  }\n}\n\nfragment CREATIVE on Creative {\n  referenceId\n  status\n  image\n  text\n  icon\n  language\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_y, headers=headers, json=json_data)
    print("status pca creative details",response.status_code)



    parsed_data = json.loads(response.text)

    rukmini_urls = {}
    medias = parsed_data['data']['getCreatives']['manualCreativeImageUrls']['medias']
    for key, value in medias.items():
        rukmini_urls[key] = value['rukminiUrl']


    for item in contents:
        media_id = item['creativeImage']['mediaId']
        if media_id in rukmini_urls:
            url = rukmini_urls[media_id]
            item['creativeImage']['url'] = url

    ###########################################budget_main#####################################################
    
    
    
    
        cookies_q = {
        'DID': 'cltfsxlmh69cj0x080ko71pv7',
        '_ga': 'GA1.1.1167863333.1709729726',
        'T': 'TI171041253423100159177482711189994566661456194141317532355081987438',
        'rt': 'null',
        'K-ACTION': 'null',
        '_pxvid': '97877fb5-e1ee-11ee-848c-42c3808d2940',
        'ud': '2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ',
        'vh': '607',
        'vw': '1366',
        'dpr': '1',
        'SN': 'VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A',
        'vd': 'VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==',
        'CURRENT_TENANT': 'BSS',
        '_csrf': 'U7_Azf6qHpckxTd-H04-AMWk',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1OTQ3MzgsImlhdCI6MTcxMzU5MjkzOCwiaXNzIjoia2V2bGFyIiwianRpIjoiMGE1MWVlMzctNTE4MC00OGM2LWJiZjYtMWQxODUxYzIwYjJiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6Ik9OVE8yMyIsImtldklkIjoiVklEMTFCNTY2NzE2RTk0RjY1OUUzOEM3RTMwOTdFREJCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.zoK1zDnvUd79WpncB7Zq_VRJTICFGzXxwuf2Dnu1cN0',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM1OTI5MzgsImV4cCI6MTcxMzU5MzUzOH0.Kl1vrB063pcdlgalllLUyjYDLBUH0_K1f8Q6adXwY-w',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713592938.10.1.1713592996.0.0.0',
        'nonce': 'ss-3529659493',
    }
    for key in cookie_dict.keys():
        if key in cookies_q:
            cookies_q[key] = cookie_dict[key]
    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'DID=cltfsxlmh69cj0x080ko71pv7; _ga=GA1.1.1167863333.1709729726; T=TI171041253423100159177482711189994566661456194141317532355081987438; rt=null; K-ACTION=null; _pxvid=97877fb5-e1ee-11ee-848c-42c3808d2940; ud=2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ; vh=607; vw=1366; dpr=1; SN=VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A; vd=VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE; S=d1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==; CURRENT_TENANT=BSS; _csrf=U7_Azf6qHpckxTd-H04-AMWk; TENANT=BSS; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjA1MGRjYzRjLTE0MGYtNDNkYy1iYTUzLTM2NTY3MTQ3MWVlZSJ9.eyJleHAiOjE3MTM1OTQ3MzgsImlhdCI6MTcxMzU5MjkzOCwiaXNzIjoia2V2bGFyIiwianRpIjoiMGE1MWVlMzctNTE4MC00OGM2LWJiZjYtMWQxODUxYzIwYjJiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6Ik9OVE8yMyIsImtldklkIjoiVklEMTFCNTY2NzE2RTk0RjY1OUUzOEM3RTMwOTdFREJCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJJRDF6b1dKMmIzUV9OOUtBbjJ5Q0dUbHFpYl85TnR2aWRmeDY4M2Y5X1NrPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.zoK1zDnvUd79WpncB7Zq_VRJTICFGzXxwuf2Dnu1cN0; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTM1OTI5MzgsImV4cCI6MTcxMzU5MzUzOH0.Kl1vrB063pcdlgalllLUyjYDLBUH0_K1f8Q6adXwY-w; _ga_ZPGRNTNNRT=GS1.1.1713592938.10.1.1713592996.0.0.0; nonce=ss-3529659493',
        'Origin': 'https://advertising.flipkart.com',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=2',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '10',
        'dpr': '1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '952',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': 'bGzw5TnX-_g7M19TfOEirmBSLCSGHct98v3Q',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pca/0KFZD30K1Y2F/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=2',
        'x-tenant': 'BSS',
    }
    print("placemnbt:+++++++++++++++++++++++++")
    print(contents)
    
    # exit()
    print("ad_group_name:", ad_group_name)
    print("cost:", ad_group_cost)
    print("startDate:", ad_group_startdate)
    print("endDate:", ad_group_enddate)
    print("costModel:", campaign_costModel)
    print("budget:", ad_group_budget)
    print("pacing:", ad_group_pacing)
    print("marketplace:", ad_group_marketPlace)
    print("excludeKeywords:", ad_group_excludeKeywords)
    print("collectionUrl:", collection_url)
    print("landingPageUrl:", landing_page_url)
    print("contentId:", content_id)
    print("creativeTemplateId:", creative_template_id)
    print("isPreferredSeller:", is_preferred_seller)
    print("brands:", brand)
    print("stores:", stores)
    print("id:", ad_group_id)
    print("showAdInBroadMatchStores:", False)
    print("costVariation:", placement_dict)
    print("targeting:", targeting)
    
    # for item in targeting:
    #     if 'excludeKeywords' in item and item['excludeKeywords'] is not None:
    #         item['excludeKeywords'] = [keyword for keyword in item['excludeKeywords'] if '__typename' not in keyword]
    #     if 'includeKeywords' in item and item['includeKeywords'] is not None:
    #         item['includeKeywords'] = [keyword for keyword in item['includeKeywords'] if '__typename' not in keyword]
    # print("targeting:", targeting)

    print("campaign_budget:", campaign_budget)
    print("costModel:", campaign_costModel)
    print("endDate:", campaign_endDate)
    print("marketplace:", campaign_marketplace)
    print("name:", campaign_name)
    print("startDate:", campaign_startDate)
    print("tillBudgetEnds:", True)
    print("type:", campaign_type)
    print("budgetType:", campaign_budgetType)
    print("campaign_id_pca:", campaign_id_pca)

    # exit()  
    json_data = {
        'operationName': 'UpdatePCACampaign',
        'variables': {
            'data': {
                'adGroups': [
                    {
                        'name': ad_group_name,
                        'cost': ad_group_cost,
                        'startDate': ad_group_startdate,
                        'endDate': ad_group_enddate,
                        'costModel': campaign_costModel,
                        'budget': ad_group_budget,
                        'pacing': ad_group_pacing,
                        'marketplace': ad_group_marketPlace,
                        'excludeKeywords': ad_group_excludeKeywords,
                        'contents': [
                            {
                                'collectionUrl': collection_url,
                                'landingPageUrl': landing_page_url,
                                'contentId': content_id,
                                'creativeTemplateId': creative_template_id,
                                'isPreferredSeller': is_preferred_seller,
                                'name': 'PCA_CONTENT',
                                'creatives': contents,
                                'brands': brand,
                                'stores': stores,
                            },
                        ],
                        'id': ad_group_id,
                        'showAdInBroadMatchStores': False,
                        'costVariation': {
                            'placements': placement_dict,
                        },
                        'targeting': targeting,
                    },
                ],
                'campaignInfo': {
                    'budget': campaign_budget,  
                    'costModel': campaign_costModel,
                    'endDate': campaign_endDate,
                    'marketplace': campaign_marketplace,
                    'name': campaign_name,  
                    'startDate': campaign_startDate,
                    'tillBudgetEnds': True,
                    'type': campaign_type,
                    'budgetType': campaign_budgetType,
                },
            },
            'id': campaign_id_pca,
        },
        'query': 'mutation UpdatePCACampaign($data: SaveCampaignPayload!, $id: String!) {\n  updateCampaign(data: $data, id: $id) {\n    ...CampaignPCAFragment\n    __typename\n  }\n}\n\nfragment CampaignPCAFragment on CampaignPCAResponse {\n  campaignInfo {\n    id\n    status\n    uiStatus\n    startDate\n    endDate\n    costModel\n    pacing\n    type\n    budget\n    name\n    grossBudget\n    budgetType\n    marketplace\n    allowedActions\n    __typename\n  }\n  adGroups {\n    id\n    contents {\n      contentId\n      collectionUrl\n      isPreferredSeller\n      creativeTemplateId\n      creativeBanners {\n        creativeId\n        creativeName\n        status\n        creativeTemplateId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
    }
    
    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_q, headers=headers, json=json_data)
    # print(json_data)

    print(response.text)
    print("status pca update campaign",response.status_code)
    
    i+=1


exit()

#++++++++++++++++++++++++++++++++++++++++++++StartPLA+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if conditions:
    query = "SELECT DISTINCT(Campaign_ID) FROM  fk_pla_nivea WHERE TYPE='PLA' AND " + " AND ".join(conditions)
    print(query)
    cursor.execute(query)
    campaign_ids_pla = cursor.fetchall()
else:
    print("No conditions found.")


if campaign_ids_pla:
    for campaign_id_pla in campaign_ids_pla:
        print(campaign_id_pla[0])
else:
    print("No campaigns found")


def adjust_absolute_cost(absolute_cost, percentage_change):
    if percentage_change:
        adjusted_cost = float(absolute_cost) * (1 + percentage_change / 100)
    else:
        pass
        #adjusted_cost = float(absolute_cost) * (1 + percentage_change / 100)
    return adjusted_cost

j=0
placement_dict_pla = []

for campaign_id_pla in campaign_ids_pla:
    campaign_id_pla=campaign_id_pla[0]
    print(campaign_id_pla)
    # cursor.execute("SELECT MAX(Date) FROM fk_pla_nivea WHERE  Campaign_ID = %s ;", (campaign_id_pla,))
    # max_date = cursor.fetchone()[0]
    # print(max_date)
    # # exit()
    # max_date = max_date.date()
    
    # cursor.execute("SELECT Absolute_Cost, Percentage, Placement_Type FROM fk_pla_nivea WHERE Campaign_ID = %s AND DATE(Date) = %s", (campaign_id_pla, max_date))

    
    # placements = cursor.fetchall()
    # print("+++++++++++++addsdsdsds")
    # print(placements)
    
    # for placement in placements:
    #     percentage_change = 2  # frontend se pass hogea
    #     adjusted_absolute_cost = adjust_absolute_cost(placement[0], percentage_change)

    #     cursor.execute("UPDATE fk_pla_nivea SET Absolute_Cost = %s WHERE Campaign_ID = %s AND Placement_Type = %s;",
    #                    (adjusted_absolute_cost, campaign_id_pla, placement[2]))
    #     connection.commit()

    #     placement_dict_pla.append({
    #         'absoluteCost': float(adjusted_absolute_cost),
    #         'percentage': placement[1],
    #         'type': placement[2]
    #     })
        

    # print(placement_dict_pla)

    # exit()
    cookies_pla = {
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
        'SN': 'VI6C522DFEDDDB47B094DBAB8FB82537CC.TOK635F5023E626455C82262BA71755319E.1712039145.LI',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNhNzdlZTgxLTRjNWYtNGU5Ni04ZmRlLWM3YWMyYjVlOTA1NSJ9.eyJleHAiOjE3MTIwNDA5NDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZWNhMjk4YmItYjg2OS00NDUzLWFmN2QtYmRmNTMxMzRkOTUxIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwiZWFJZCI6ImJlMHVRSWdQSVRwMlpxYW5OTmhobkdIamhSdi1QMVhOTmNURnloQS16QVNBWU40QlZ2NF9Odz09IiwidnMiOiJMSSIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QlU14s5wGMPi9nFMdwxMyzDo4smmVhEtrHlqVyVhTNk',
        'rt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhlM2ZhMGE3LTJmZDMtNGNiMi05MWRjLTZlNTMxOGU1YTkxZiJ9.eyJleHAiOjE3Mjc4NTAzNDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiNDIzZjU0NzUtNTlkNC00MDg1LWFiODctOGU0MDE0NGVkMzhlIiwidHlwZSI6IlJUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwibSI6eyJ0eXBlIjoibiJ9LCJ2IjoiRkE2Mk4wIn0.vIfnR1RG69lqB0Dlfy-vB7OQGL32CezHdZQXRXRkHig',
        'K-ACTION': 'null',
        'vd': 'VI6C522DFEDDDB47B094DBAB8FB82537CC-1707110391153-52.1712039145.1712039145.162207728',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19816%7CMCMID%7C88087235322683450901903204835359161911%7CMCAAMLH-1712211807%7C12%7CMCAAMB-1712643946%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1712046346s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t12NCs/Pz8/Pxk/P3A/Pz8JCuxBp8CZTkB6LhkuhmGxb3OZDRSvEpQiuwSBYjDolxx3NUwQmcjYwfQ5cOfkx/edsg==',
        '_gid': 'GA1.2.848745820.1713091202',
        'AMCV_55CFEDA0570C3FA17F000101%40AdobeOrg': '-227196251%7CMCIDTS%7C19827%7CMCMID%7C83672356534473986601461754159478791217%7CMCAAMLH-1713427685%7C12%7CMCAAMB-1713696009%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713098409s%7CNONE%7CMCAID%7CNONE',
        'mp_9ea3bc9a23c575907407cf80efd56524_mixpanel': '%7B%22distinct_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24device_id%22%3A%20%2218bf5c79f2b403-04403e63bfeec8-26031051-144000-18bf5c79f2ca33%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fseller.flipkart.com%2Fsell-online%2Fmulti-select%22%2C%22%24initial_referring_domain%22%3A%20%22seller.flipkart.com%22%2C%22%24user_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24search_engine%22%3A%20%22google%22%7D',
        's_nr': '1713091411302-Repeat',
        '_ga_0SJLGHBL81': 'GS1.1.1713099129.39.0.1713099129.0.0.0',
        '_ga_TVF0VCMCT3': 'GS1.1.1713099129.160.0.1713099129.60.0.0',
        '_ga': 'GA1.1.1819741834.1700633034',
        'CURRENT_TENANT': 'BSS',
        '_csrf': '8_rTldRkHKcTy4SbbBCU1knX',
        'TENANT': 'BSS',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTMxNzc4ODQsImlhdCI6MTcxMzE3NjA4NCwiaXNzIjoia2V2bGFyIiwianRpIjoiMDIyNGFkZTYtMDQxOS00YWYzLTk3ZWEtMTdmZWJlODVlNGUyIiwidHlwZSI6IkFUIiwiZElkIjoiY2xyMXB1cDI1MmJxcDB4MHdlanBlMWFqbyIsImJJZCI6IlczQjNYWSIsImtldklkIjoiVklFMENDRjY0MkExQ0E0MzFEQTAwQTZDMjk1RTBBNzFENSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.5IRT8ihiCVwCUZM1m_AWz4JJeW69Fqx9kNTXuJUGPik',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTMxNzYwODQsImV4cCI6MTcxMzE3NjY4NH0.IPmFS2AhkrKSWMNSrwkqF-Glj0Fxn-B_hT87NkotaRA',
        'nonce': 'ss-2097335141',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713176080.275.1.1713176189.0.0.0',
    }

    for key in cookie_dict.keys():
        if key in cookies_pla:
            cookies_pla[key] = cookie_dict[key]

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': 'T=TI169891842149300161944937865135939588577615020537527148270186391420; _pxvid=c6c61fc1-7964-11ee-8e5a-1d67ccbdf2e0; dpr=1.25; _fbp=fb.1.1700471257731.638459595; _ga_B9RGC9GN63=GS1.1.1702722512.1.1.1702722682.54.0.0; DID=clr1pup252bqp0x0wejpe1ajo; ULSN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjb29raWUiLCJhdWQiOiJmbGlwa2FydCIsImlzcyI6ImF1dGguZmxpcGthcnQuY29tIiwiY2xhaW1zIjp7ImdlbiI6IjEiLCJ1bmlxdWVJZCI6IlVVSTI0MDIxNDEyNTQxMjc4NE85TU9OTE0iLCJma0RldiI6bnVsbH0sImV4cCI6MTcyMzY3NTQ1MiwiaWF0IjoxNzA3ODk1NDUyLCJqdGkiOiIzZmIzYjAxZS02MzU2LTRjM2ItYTg3Yi1lNDQ3ZWNmMWJiYzEifQ.qbw3LDnvt96oOTYcrXvedJeOeJteVaWqgwkYlaKjyuw; vh=730; vw=1536; _ga_0RGM1K38MN=GS1.2.1708195526.2.1.1708195657.0.0.0; _ga_C00F4Q43Q7=GS1.2.1708196044.1.0.1708196044.0.0.0; _gcl_au=1.1.856723108.1708257205; ud=3.-hCuLDZfVJf9kwEcWhK4arj09yD35YGA9WD7yo1zRPr-6c1rmX2_xdHegqPpB3V8IXYz3NsAnP3SBWNaEKufBfykm01W9EISet6O__tpbwLut1-EZphHbJ0c9MzW0rczeRXhalfDVODMz8JTNMlQlgc9FtPFTSU9rNePFCXS_okASoEjAhPorkspIuB6dUcZtsYfTSEOj6D6fCfEhHGTX040PuZMdyiyk409VK7VDUArNQCXrRjfusSZdRR_dSa_IYardO48M5GyGz8FGpTkPTBYE_1zDB-5NXEc93lP2wklWoHEa-Dtp_7e6v2PvoLYEnO9q9WRO923E1MzbxEsgQzTal18ocz6m1QhVKcLAkifQY1CVPvSCEDYAhYysg7Cifn25pVGYReJE-wqKz__XeZKWQ6m9S5ylJWi8ZCNic_rQWkW8tl4jP7uwPxupbq0hBk3YeSRAVvcjX09zDY5qn4jmi-pJicw3oOin6BBwh5j4AEuCE1_UBhyu1FzQ6HXVin354_zqMKmt5Ez4awQztwLbxHMqBrzPLNw1nVv-mMH56A0UIV523BaT7wlgFXFKDY9PgZuquXJtkpqqSSPK3sdeoBmL_SsoP5XdHnW3U3lvtJigEiuV1-2In3wufWsqsHYvXC8tj7Vr6X8srs_3ehJ7eFh0ZMdB7QsQTCynabS2sW3gILSeLC2-NwmdaemzanTaScNERb6Z6uBV6aYgxLtiUZZci5cqwxPaCVTIRHxdKh90EtL6MagI-T8KaMNUkYxg3mOLw4UnS1OIQr5vw; _ga_2P94RMW04V=GS1.2.1711394187.7.1.1711394237.0.0.0; SN=VI6C522DFEDDDB47B094DBAB8FB82537CC.TOK635F5023E626455C82262BA71755319E.1712039145.LI; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNhNzdlZTgxLTRjNWYtNGU5Ni04ZmRlLWM3YWMyYjVlOTA1NSJ9.eyJleHAiOjE3MTIwNDA5NDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZWNhMjk4YmItYjg2OS00NDUzLWFmN2QtYmRmNTMxMzRkOTUxIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwiZWFJZCI6ImJlMHVRSWdQSVRwMlpxYW5OTmhobkdIamhSdi1QMVhOTmNURnloQS16QVNBWU40QlZ2NF9Odz09IiwidnMiOiJMSSIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QlU14s5wGMPi9nFMdwxMyzDo4smmVhEtrHlqVyVhTNk; rt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhlM2ZhMGE3LTJmZDMtNGNiMi05MWRjLTZlNTMxOGU1YTkxZiJ9.eyJleHAiOjE3Mjc4NTAzNDUsImlhdCI6MTcxMjAzOTE0NSwiaXNzIjoia2V2bGFyIiwianRpIjoiNDIzZjU0NzUtNTlkNC00MDg1LWFiODctOGU0MDE0NGVkMzhlIiwidHlwZSI6IlJUIiwiZElkIjoiVEkxNjk4OTE4NDIxNDkzMDAxNjE5NDQ5Mzc4NjUxMzU5Mzk1ODg1Nzc2MTUwMjA1Mzc1MjcxNDgyNzAxODYzOTE0MjAiLCJiSWQiOiJJWVhHSlkiLCJrZXZJZCI6IlZJNkM1MjJERkVERERCNDdCMDk0REJBQjhGQjgyNTM3Q0MiLCJ0SWQiOiJtYXBpIiwibSI6eyJ0eXBlIjoibiJ9LCJ2IjoiRkE2Mk4wIn0.vIfnR1RG69lqB0Dlfy-vB7OQGL32CezHdZQXRXRkHig; K-ACTION=null; vd=VI6C522DFEDDDB47B094DBAB8FB82537CC-1707110391153-52.1712039145.1712039145.162207728; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19816%7CMCMID%7C88087235322683450901903204835359161911%7CMCAAMLH-1712211807%7C12%7CMCAAMB-1712643946%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1712046346s%7CNONE%7CMCAID%7CNONE; S=d1t12NCs/Pz8/Pxk/P3A/Pz8JCuxBp8CZTkB6LhkuhmGxb3OZDRSvEpQiuwSBYjDolxx3NUwQmcjYwfQ5cOfkx/edsg==; _gid=GA1.2.848745820.1713091202; AMCV_55CFEDA0570C3FA17F000101%40AdobeOrg=-227196251%7CMCIDTS%7C19827%7CMCMID%7C83672356534473986601461754159478791217%7CMCAAMLH-1713427685%7C12%7CMCAAMB-1713696009%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713098409s%7CNONE%7CMCAID%7CNONE; mp_9ea3bc9a23c575907407cf80efd56524_mixpanel=%7B%22distinct_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24device_id%22%3A%20%2218bf5c79f2b403-04403e63bfeec8-26031051-144000-18bf5c79f2ca33%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fseller.flipkart.com%2Fsell-online%2Fmulti-select%22%2C%22%24initial_referring_domain%22%3A%20%22seller.flipkart.com%22%2C%22%24user_id%22%3A%20%22ACCABA3F2470AD442FAA32E10D0E76B735F%22%2C%22%24search_engine%22%3A%20%22google%22%7D; s_nr=1713091411302-Repeat; _ga_0SJLGHBL81=GS1.1.1713099129.39.0.1713099129.0.0.0; _ga_TVF0VCMCT3=GS1.1.1713099129.160.0.1713099129.60.0.0; _ga=GA1.1.1819741834.1700633034; CURRENT_TENANT=BSS; _csrf=8_rTldRkHKcTy4SbbBCU1knX; TENANT=BSS; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTMxNzc4ODQsImlhdCI6MTcxMzE3NjA4NCwiaXNzIjoia2V2bGFyIiwianRpIjoiMDIyNGFkZTYtMDQxOS00YWYzLTk3ZWEtMTdmZWJlODVlNGUyIiwidHlwZSI6IkFUIiwiZElkIjoiY2xyMXB1cDI1MmJxcDB4MHdlanBlMWFqbyIsImJJZCI6IlczQjNYWSIsImtldklkIjoiVklFMENDRjY0MkExQ0E0MzFEQTAwQTZDMjk1RTBBNzFENSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.5IRT8ihiCVwCUZM1m_AWz4JJeW69Fqx9kNTXuJUGPik; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwidmFsaWRTZXNzaW9uIjp0cnVlLCJ0ZW5hbnQiOiJCU1MiLCJpYXQiOjE3MTMxNzYwODQsImV4cCI6MTcxMzE3NjY4NH0.IPmFS2AhkrKSWMNSrwkqF-Glj0Fxn-B_hT87NkotaRA; nonce=ss-2097335141; _ga_ZPGRNTNNRT=GS1.1.1713176080.275.1.1713176189.0.0.0',
        'Origin': 'https://advertising.flipkart.com',
        'Pragma': 'no-cache',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pla/6E1IWXWRAW1B/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q',
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
        'viewport-width': '756',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': 'eCF65bmj-n1doRf9-YgZ8SD9xeBV8cnyrP9M',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pla/6E1IWXWRAW1B/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q',
        'x-tenant': 'BSS',
    }

    json_data = {
        'operationName': 'GetCampaign',
        'variables': {
            'seller': False,
            'adProduct': 'BRAND_PLA',
            'id': campaign_id_pla,
        },
        'query': 'query GetCampaign($id: String!, $adProduct: String!, $seller: Boolean! = false) {\n  getCampaignForId(id: $id, adProduct: $adProduct) {\n    ... on CampaignPLAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        fsnIds\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        withPreferredSellers\n        preferredSellerIds\n        preferredSellerNames\n        businessZones\n        tillBudgetEnds\n        fsnMeta {\n          id\n          title\n          image\n          minListingPrice\n          maxListingPrice\n          listingCurrency\n          brand\n          storeList\n          __typename\n        }\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        productCount\n        commodityId\n        cost\n        budget\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        storePaths\n        fsnBanners {\n          id\n          fsnId\n          __typename\n        }\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      preferredSellers {\n        alias\n        sellerId\n        __typename\n      }\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignPCAResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        budgetType\n        startDate\n        endDate\n        costModel\n        marketplace\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        excludeKeywords\n        marketplace\n        showAdInBroadMatchStores\n        costVariation {\n          ...PlacementsFragment\n          __typename\n        }\n        allowedActions\n        pacing\n        targeting {\n          type\n          pages\n          excludeKeywords {\n            q\n            r\n            __typename\n          }\n          includeKeywords {\n            q\n            r\n            matchType\n            __typename\n          }\n          __typename\n        }\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            creativeTemplateId\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              assetId\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              __typename\n            }\n            isSelected\n            id\n            language\n            __typename\n          }\n          collectionUrl\n          landingPageUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isPreferredSeller\n          creativeTemplateId\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      placementsMetaInfo {\n        ...PlacementsMetaInfoFragement\n        __typename\n      }\n      __typename\n    }\n    ... on CampaignDisplayAdsResponse {\n      campaignInfo {\n        id\n        type\n        name\n        status\n        uiStatus\n        currency\n        paymentType\n        budget\n        startDate\n        endDate\n        costModel\n        marketplace\n        pacing\n        budgetType\n        adFormat\n        publisher\n        __typename\n      }\n      adGroups {\n        id\n        name\n        status\n        uiStatus\n        startDate\n        endDate\n        cost\n        budget\n        allowedActions\n        marketplace\n        pacing\n        contents {\n          contentId\n          creativeBanners {\n            creativeId\n            creativeName\n            uiStatus\n            status\n            allowedActions\n            referenceId\n            mediaId\n            videoMediaStatus\n            creativeType\n            assets {\n              macro\n              value\n              type\n              origin\n              subAssets {\n                macro\n                value\n                type\n                __typename\n              }\n              isSystemAsset\n              __typename\n            }\n            isSelected\n            id\n            __typename\n          }\n          collectionUrl\n          collectionId\n          collectionType\n          brands\n          stores {\n            storeId\n            storeName\n            __typename\n          }\n          rejectedCount\n          isUrlSystemCreated\n          landingPageUrl\n          status\n          isPreferredSeller\n          __typename\n        }\n        frequencyCapping {\n          interval\n          value\n          numberOfIntervals\n          __typename\n        }\n        customScheduling\n        channels\n        userTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        contextTargetingExpression {\n          groupId\n          type\n          values\n          publisherSpecific\n          __typename\n        }\n        __typename\n      }\n      brandIds\n      __typename\n    }\n    __typename\n  }\n  getAdAccountDetails @skip(if: $seller) {\n    marketplaceConfigurationResponse {\n      marketplaceList\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PlacementsFragment on CostVariationType {\n  placements {\n    absoluteCost\n    percentage\n    type\n    pageType\n    __typename\n  }\n  __typename\n}\n\nfragment PlacementsMetaInfoFragement on PlacementsMeta {\n  type\n  title\n  detail\n  pageType\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_pla, headers=headers, json=json_data)


    print(response.text)
    print(response.status_code)


    x = json.loads(response.text)
    campaign_id_pla = x["data"]["getCampaignForId"]["campaignInfo"]["id"]
    # print(campaign_id)
    # exit()
    campaign_type = x["data"]["getCampaignForId"]["campaignInfo"]["type"]

    campaign_name=x["data"]["getCampaignForId"]["campaignInfo"]["name"]

    campaign_budget = x["data"]["getCampaignForId"]["campaignInfo"]["budget"]

    campaign_budgetType = x["data"]["getCampaignForId"]["campaignInfo"]["budgetType"]

    campaign_startDate = x["data"]["getCampaignForId"]["campaignInfo"]["startDate"]
    # print(campaign_startDate)
    # exit()
    campaign_endDate = x["data"]["getCampaignForId"]["campaignInfo"]["endDate"]

    campaign_costModel = x["data"]["getCampaignForId"]["campaignInfo"]["costModel"]

    campaign_pacing=x["data"]["getCampaignForId"]["campaignInfo"]["pacing"]

    fsn_ids = x["data"]["getCampaignForId"]["campaignInfo"]["fsnIds"]
    # print(fsn_ids)
    # exit()

    campaign_marketplace = x["data"]["getCampaignForId"]["campaignInfo"]["marketplace"]

    campaign_buisnesszone = x["data"]["getCampaignForId"]["campaignInfo"]["businessZones"]

    campaign_cost_model=x["data"]["getCampaignForId"]["campaignInfo"]["costModel"]
    # print(campaign_costModel)


    ad_group_id = x["data"]["getCampaignForId"]["adGroups"][0]["id"]
    ad_group_name = x["data"]["getCampaignForId"]["adGroups"][0]["name"]
    ad_group_commodity_id = x["data"]["getCampaignForId"]["adGroups"][0]["commodityId"]

    ad_group_cost = x["data"]["getCampaignForId"]["adGroups"][0]["cost"]
    # print(ad_group_commodity_id)
    # exit()
    ad_group_budget = x["data"]["getCampaignForId"]["adGroups"][0]["budget"]
    # print(ad_group_budget)
    # exit()
    placements_pla = x["data"]["getCampaignForId"]["adGroups"][0]["costVariation"]["placements"]
    store_paths = x["data"]["getCampaignForId"]["adGroups"][0]["storePaths"]
    targeting = x["data"]["getCampaignForId"]["adGroups"][0]["targeting"]
    # print(targeting)
    # exit()
    ad_groups = x["data"]["getCampaignForId"]["adGroups"]

    # print(ad_groups)

    for placement in placements_pla:
        del placement['pageType']
        del placement['__typename']
    print(placements_pla)
    # exit()
    for placement in placements_pla:
        percentage_change = 0.1  # frontend se pass hogea
        adjusted_absolute_cost = adjust_absolute_cost(placement['absoluteCost'], percentage_change)

        cursor.execute("UPDATE fk_pla_nivea SET Absolute_Cost = %s WHERE Campaign_ID = %s AND Placement_Type = %s;",
                    (adjusted_absolute_cost, campaign_id_pla, placement['type']))
        connection.commit()

        placement_dict_pla.append({
            'absoluteCost': float(adjusted_absolute_cost),
            'percentage': placement['percentage'],
            'type': placement['type']
        })
        
    print(placement_dict_pla)
    # exit()
    for target in targeting:
        del target['__typename']


        
    for targeting_dict in targeting:
        if 'excludeKeywords' in targeting_dict and targeting_dict['excludeKeywords'] is not None:
            for keyword_dict in targeting_dict['excludeKeywords']:
                keyword_dict.pop('__typename', None)
    # print("Targeting:", targeting)





    datetime_obj = datetime.strptime(campaign_startDate, "%Y-%m-%dT%H:%M:%S.%f%z")
    if campaign_endDate is not None:
        
        datetime_obj = datetime.strptime(campaign_endDate, "%Y-%m-%dT%H:%M:%S.%f%z")

        campaign_endDate=datetime_obj.timestamp()
        campaign_endDate=int(campaign_endDate)*1000
        # print(campaign_endDate)
        
        
    campaign_startDate = datetime_obj.timestamp()

    campaign_startDate=int(campaign_startDate)*1000


    
    
     
    cookies_z = {
        'DID': 'cltfsxlmh69cj0x080ko71pv7',
        '_ga': 'GA1.1.1167863333.1709729726',
        'T': 'TI171041253423100159177482711189994566661456194141317532355081987438',
        'rt': 'null',
        'K-ACTION': 'null',
        '_pxvid': '97877fb5-e1ee-11ee-848c-42c3808d2940',
        'ud': '2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ',
        'vh': '607',
        'vw': '1366',
        'dpr': '1',
        'SN': 'VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO',
        'at': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A',
        'vd': 'VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413',
        'AMCV_17EB401053DAF4840A490D4C%40AdobeOrg': '-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE',
        'S': 'd1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==',
        'CURRENT_TENANT': 'BSS',
        '_csrf': 'dDYoohCbFi4Mckt1kj6WiIst',
        'TENANT': 'BSS',
        'BSS_UDT': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwic3VjY2VzcyI6dHJ1ZSwidGVuYW50IjoiQlNTIiwiYWFjY291bnQiOnt9LCJpYXQiOjE3MTM3NzkxODMsImV4cCI6MTcxMzc3OTc4M30.bq2JCHg0g7b9afQI1jPLGt_DymfkC_p_nsXAsPKyxhk',
        'BSS_SID': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTM3ODA5ODMsImlhdCI6MTcxMzc3OTE4MywiaXNzIjoia2V2bGFyIiwianRpIjoiZDljYzE0OGMtNTc0My00NGQwLTlkNDMtMTBjYWUxMzVkYmZiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IlRNUkMyVyIsImtldklkIjoiVklFNzc5NkZGOTg5MDM0NDY3OEE3MEQ4NzJBRkZDMTZCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.abt3moCY5VYKryfPsFT3jfPfASUT_iUIbYkmlmIDnAc',
        '_ga_ZPGRNTNNRT': 'GS1.1.1713775517.13.1.1713779215.0.0.0',
        'nonce': 'ss-675098816',
    }
    for key in cookie_dict.keys():
        if key in cookies_z:
            cookies_z[key] = cookie_dict[key]
    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'DID=cltfsxlmh69cj0x080ko71pv7; _ga=GA1.1.1167863333.1709729726; T=TI171041253423100159177482711189994566661456194141317532355081987438; rt=null; K-ACTION=null; _pxvid=97877fb5-e1ee-11ee-848c-42c3808d2940; ud=2.YOKqx9JHMp80DdNjUKLH8U41oHBcoHPB5mN02Nb5emkAYdJcMgXK4424tSMYFXzDVcNITmD0Y-b7uPgpErfcMZ2sqO3f_ExMRGrbM-dykk_WjWsgg5XT7cdxVZNmhBNGkrcQGcewPYOraoPf_NDsxQ; vh=607; vw=1366; dpr=1; SN=VI5D0D308D80BD426BA7BB0F3688BC1F65.TOKB156577FC0134B2992D214D88AEE5E71.1713523730.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3MTUyNTE3MzAsImlhdCI6MTcxMzUyMzczMCwiaXNzIjoia2V2bGFyIiwianRpIjoiYTVhMzFmYTctM2FiNy00NzkwLWJhNDItMTZkNWJhNGRjMzM3IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzEwNDEyNTM0MjMxMDAxNTkxNzc0ODI3MTExODk5OTQ1NjY2NjE0NTYxOTQxNDEzMTc1MzIzNTUwODE5ODc0MzgiLCJrZXZJZCI6IlZJNUQwRDMwOEQ4MEJENDI2QkE3QkIwRjM2ODhCQzFGNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjR9.QgJyhc6zJ9eczZkzgxcJ_RTwLjUZ-9yGn8w_Lvauj7A; vd=VI5D0D308D80BD426BA7BB0F3688BC1F65-1710412536056-4.1713523730.1713523730.153884413; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C19833%7CMCMID%7C27540310070417555930568187461838119454%7CMCAAMLH-1714128531%7C12%7CMCAAMB-1714128531%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713530931s%7CNONE%7CMCAID%7CNONE; S=d1t18JD89Zz8KWGdkLz8/ej8/IVDTCbPIVn0qhzRK83rmeJSgnVUSMglHDJ2VxgFLNbGdfhS2vke2CuQbHvdIaRZTpQ==; CURRENT_TENANT=BSS; _csrf=dDYoohCbFi4Mckt1kj6WiIst; TENANT=BSS; BSS_UDT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFzaHV0b3NoLnNodWtsYUB0cmFpbHl0aWNzLmNvbSIsImZpcnN0TmFtZSI6IkFzaHV0b3NoIFNodWtsYSIsIm1vYmlsZSI6Ijg5NjI2MzA3ODEiLCJzdGF0ZSI6IlZFUklGSUVEIiwic3VjY2VzcyI6dHJ1ZSwidGVuYW50IjoiQlNTIiwiYWFjY291bnQiOnt9LCJpYXQiOjE3MTM3NzkxODMsImV4cCI6MTcxMzc3OTc4M30.bq2JCHg0g7b9afQI1jPLGt_DymfkC_p_nsXAsPKyxhk; BSS_SID=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQxZWI3YWU1LTllNmUtNGMxNi04ZjM1LTVlYWJhOGNiYzMyZCJ9.eyJleHAiOjE3MTM3ODA5ODMsImlhdCI6MTcxMzc3OTE4MywiaXNzIjoia2V2bGFyIiwianRpIjoiZDljYzE0OGMtNTc0My00NGQwLTlkNDMtMTBjYWUxMzVkYmZiIiwidHlwZSI6IkFUIiwiZElkIjoiY2x0ZnN4bG1oNjljajB4MDgwa283MXB2NyIsImJJZCI6IlRNUkMyVyIsImtldklkIjoiVklFNzc5NkZGOTg5MDM0NDY3OEE3MEQ4NzJBRkZDMTZCRSIsInRJZCI6ImFkc191aSIsImVhSWQiOiJXMHlCbURjN01OVzd1VzBqN1JfYWZKTHYtdGxsMmw5bm4taGw2SU5xR2xnPSIsInZzIjoiTEkiLCJ6IjoiQ0giLCJtIjpmYWxzZSwiZ2VuIjo0fQ.abt3moCY5VYKryfPsFT3jfPfASUT_iUIbYkmlmIDnAc; _ga_ZPGRNTNNRT=GS1.1.1713775517.13.1.1713779215.0.0.0; nonce=ss-675098816',
        'Origin': 'https://advertising.flipkart.com',
        'Referer': 'https://advertising.flipkart.com/ad-account/campaigns/pla/6E1IWXWRAW1B/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=3',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accept': '*/*',
        'apollographql-client-name': 'Flipkart-Ads',
        'apollographql-client-version': '1.0.0',
        'content-type': 'application/json',
        'downlink': '8.55',
        'dpr': '1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'viewport-width': '952',
        'x-aaccount': '4616HEEMH03Q',
        'x-baccount': 'org-9J4HV93IJV',
        'x-csrf-token': 'RqUASJLb-gSSK9BJDS8zgaJRR_t3prC0q4SA',
        'x-sourceurl': 'https://advertising.flipkart.com/ad-account/campaigns/pla/6E1IWXWRAW1B/edit?baccount=org-9J4HV93IJV&aaccount=4616HEEMH03Q&step=3',
        'x-tenant': 'BSS',
    }
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print(placements)
    print(placement_dict_pla)
    json_data = {
        'operationName': 'UpdateCampaign',
        'variables': {
            'data': {
                'campaignInfo': {
                    'type': campaign_type,
                    'name': campaign_name,
                    'budget': campaign_budget,
                    'budgetType': campaign_budgetType,
                    'startDate': campaign_startDate,  
                    'endDate': campaign_endDate,
                    'costModel': campaign_costModel,
                    'pacing': campaign_pacing,
                    'fsnIds':fsn_ids,
                    'marketplace': campaign_marketplace,
                    'businessZones': campaign_buisnesszone,
                },
                'adGroups': [
                    {
                        'id': ad_group_id,
                        'name': ad_group_name,
                        'commodityId': ad_group_commodity_id,
                        'costModel': campaign_costModel,
                        'cost': ad_group_cost,
                        'budget': ad_group_budget,
                        'costVariation': {
                            'placements': placement_dict_pla,
                        },
                        'storePaths': store_paths,
                        'targeting': targeting,
                        'fsnIds': fsn_ids,
                    },
                ],
            },
            'id': campaign_id_pla,
        },
        'query': 'mutation UpdateCampaign($data: SavePLACampaignPayload!, $id: String!) {\n  updatePLACampaign(data: $data, id: $id) {\n    ...CampaignPLAFragment\n    __typename\n  }\n}\n\nfragment CampaignPLAFragment on CampaignPLAResponse {\n  campaignInfo {\n    id\n    type\n    paymentType\n    currency\n    costModel\n    pacing\n    status\n    uiStatus\n    marketplace\n    name\n    budget\n    grossBudget\n    budgetType\n    startDate\n    endDate\n    allowedActions\n    __typename\n  }\n  adGroups {\n    id\n    name\n    status\n    productCount\n    commodityId\n    cost\n    budget\n    targeting {\n      type\n      pages\n      excludeKeywords {\n        q\n        r\n        __typename\n      }\n      includeKeywords {\n        q\n        r\n        matchType\n        __typename\n      }\n      __typename\n    }\n    storePaths\n    fsnBanners {\n      id\n      fsnId\n      __typename\n    }\n    costVariation {\n      ...PlacementsFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlacementsFragment on CostVariationType {\n  placements {\n    absoluteCost\n    percentage\n    type\n    pageType\n    __typename\n  }\n  __typename\n}\n',
    }

    response = requests.post('https://advertising.flipkart.com/api', cookies=cookies_z, headers=headers, json=json_data)
    print(response.text)
    print(response.status_code)
    
    
    j=j+1

