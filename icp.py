"""
author     : Keac@wgpsec
Creat time : 2024/3/1
Email      : admin@wgpsec.org
"""

import json
import requests
import cv2
import time
import hashlib
import base64
import numpy as np
import ujson
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from detnate import detnate


def small_slice(small_image, big_image):
    isma = cv2.imdecode(np.frombuffer(base64.b64decode(small_image), np.uint8), cv2.COLOR_GRAY2RGB)
    isma = cv2.cvtColor(isma, cv2.COLOR_BGRA2BGR)
    ibig = cv2.imdecode(np.frombuffer(base64.b64decode(big_image), np.uint8), cv2.COLOR_GRAY2RGB)
    data = detnate().check_target(ibig, isma)
    return data


def get_point_json(value, key):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(ujson.dumps(value).encode(), AES.block_size))
    ciphertext_base64 = base64.b64encode(ciphertext)
    return ciphertext_base64.decode('utf-8')


def get_uid():
    characters = "0123456789abcdef"
    unique_id = ['0'] * 36
    for i in range(36):
        unique_id[i] = random.choice(characters)
    unique_id[14] = '4'
    unique_id[19] = characters[(3 & int(unique_id[19], 16)) | 8]
    unique_id[8] = unique_id[13] = unique_id[18] = unique_id[23] = "-"
    point_id = "point-" + ''.join(unique_id)
    return {"clientUid": point_id}


class IcpQuery(object):

    def __init__(self):
        self._init_session()
        self.home = "https://beian.miit.gov.cn/"
        self.url = "https://hlwicpfwc.miit.gov.cn/icpproject_query/api/"
        self.headers = self.build_headers()
        self.p_uuid = ""

    def _init_session(self):
        self.session = requests.session()

    def build_headers(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0'
        ]

        ua = random.choice(user_agents)
        token = self.get_token()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/json',
            'Token': token,
            'Origin': 'https://beian.miit.gov.cn',
            'Referer': 'https://beian.miit.gov.cn/',
            'User-Agent': ua
        }
        return headers

    def get_cookie(self):
        self.session.get(self.home, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32'
        })

    def get_token(self):
        self.get_cookie()
        time_stamp = round(time.time() * 1000)
        auth_secret = 'testtest' + str(time_stamp)
        auth_key = hashlib.md5(auth_secret.encode(encoding='UTF-8')).hexdigest()
        auth_data = {'authKey': auth_key, 'timeStamp': time_stamp}
        base_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
            'Origin': 'https://beian.miit.gov.cn',
            'Referer': 'https://beian.miit.gov.cn/',
            'Accept': 'application/json, text/plain, */*'
        }
        try:
            with self.session.post(self.url + "auth", data=auth_data, headers=base_header) as req:
                t = req.json()
                return t['params']['bussiness']
        except Exception as e:
            print(e)
            return e

    def check_img(self):
        uuid = get_uid()
        with self.session.post(self.url + "image/getCheckImagePoint", json=uuid, headers=self.headers) as req:
            res = req.json()['params']
            big_image = res['bigImage']
            small_image = res['smallImage']
            slice_small = small_slice(small_image, big_image)
        point_json = get_point_json(slice_small, res["secretKey"])
        data = {
            "token": res["uuid"],
            "secretKey": res["secretKey"],
            "clientUid": uuid["clientUid"],
            "pointJson": point_json
        }
        self.headers.pop("Uuid", "")
        self.headers.pop("Sign", "")
        with self.session.post(self.url + "image/checkImage", json=data, headers=self.headers) as req:
            r = req.json()
            if r["success"]:
                self.headers["Uuid"] = res["uuid"]
                self.headers["Sign"] = r["params"]["sign"]
                return r["params"]["sign"]
            else:
                return 'verf error'

    def get_icp_info(self):
        self.check_img()
        name = "小米"
        data = {
            "pageNum": "",
            "pageSize": "",
            "unitName": name,
            "serviceType": 1
        }
        data = json.dumps(data, ensure_ascii=False).encode("utf-8").decode("latin1").replace(" ", "")
        with self.session.post(self.url + "icpAbbreviateInfo/queryByCondition", headers=self.headers, data=data) as req:
            return req.json()


if __name__ == '__main__':
    icp = IcpQuery()
    print(icp.get_icp_info())
