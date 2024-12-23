import pandas as pd
pd.set_option('display.max_columns', None)
import requests
import os
import warnings
warnings.filterwarnings('ignore')
import json


def drop_zhaiyao(dataset0):
    # 剔除摘要数据
    dataset0['zhaiyao'] = dataset0['announcementTitle'].apply(lambda x: 1 if '摘要' in x else 0)
    dataset0 = dataset0[dataset0['zhaiyao'] == 0]
    # 把红色的<em> </em>剔除
    dataset0['announcementTitle'] = dataset0['announcementTitle'].apply(lambda x: x.replace('<em>', ''))
    dataset0['announcementTitle'] = dataset0['announcementTitle'].apply(lambda x: x.replace('</em>', ''))
    dataset0.drop('zhaiyao', axis=1, inplace=True)
    return dataset0


# 定义下载文件的函数
def download_file(file_url, file_name, headers):
    response = requests.get(file_url, headers=headers)
    folder_path = "D:\概念板块\巨潮资讯网"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)  # 使用os.path.join来拼接文件路径，这样可以确保跨平台兼容性。
    # 使用with语句确保文件正确关闭。
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


if __name__ == '__main__':
    url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query?'

    # 自动生成的文件头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # 其他必要的headers...
    }


    file_path = 'orgId_dict.json'
    # data = {'000001': '000001,gssz0000001', '000002': '000002,gssz0000002'}
    # with open(file_path, 'w') as file:
    #     json.dump(data, file)
    with open(file_path, 'r') as file:
        json_dict = json.load(file)
    # print(json_dict)
    # 这个代码orgId不知道怎么加密的?
    # 688549,9900052780
    # 605358,9900038308

    stock = '605358'
    if stock in json_dict.keys():
        orgId = json_dict[stock]
    else:
        print('stock not in json_dict.keys()')
        import sys
        sys.exit()


    payload = {'pageNum': '1', 'pageSize': '30', 'column': 'szse', 'tabName': 'fulltext', 'plate': '',
               'stock': f'{stock},{orgId}',
               'searchkey': '年度报告', 'secid': '', 'category': 'category_ndbg_szsh', 'trade': '',
               'seDate': '2021-11-26~2024-11-25', 'sortName': 'code', 'sortType': 'asc', 'isHLtitle': 'true'}
    # 'category': 'category_ndbg_szsh' 年度报告

    url_code = url
    for key, value in payload.items():
        url_code = url_code + '{}={}&'.format(key, value)
    print(url_code)

    # 发送POST请求，获取总页数
    response = requests.post(url_code, headers=headers).json()
    print(response)
    announcements = response['announcements']
    # print(announcements)
    dataset = []
    for data in announcements:
        secCode = data['secCode']
        secName = data['secName']
        orgId = data['orgId']
        announcementId = data['announcementId']
        announcementTitle = data['announcementTitle']
        announcementTime = data['announcementTime']
        adjunctUrl = data['adjunctUrl']
        # adjunctSize = data['adjunctSize']
        # adjunctType = data['PDF']
        # storageTime = data['storageTime']
        # columnId = data['columnId']
        # pageColumn = data['pageColumn']
        # announcementType = data['announcementType']
        # associateAnnouncement = data['associateAnnouncement']
        # shortTitle = data['shortTitle']
        dataset.append([secCode, secName, orgId, announcementId, announcementTitle, announcementTime, adjunctUrl])
    dataset = pd.DataFrame(dataset, columns=['secCode', 'secName', 'orgId', 'announcementId', 'announcementTitle', 'announcementTime', 'adjunctUrl'])
    print(dataset)

    dataset = drop_zhaiyao(dataset)
    print(dataset)

    adjunctUrl = dataset['adjunctUrl'].tolist()
    announcementTitle = dataset['announcementTitle'].tolist()
    for i in range(len(adjunctUrl)):
        file_url = 'https://static.cninfo.com.cn/' + adjunctUrl[i]
        file_name = announcementTitle[i] + '.pdf'
        # download_file(file_url, file_name, headers)

