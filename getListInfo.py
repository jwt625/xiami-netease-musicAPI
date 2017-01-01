
# encrypt algorithm from
# https://github.com/darknessomi/musicbox/wiki/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%96%B0%E7%89%88WebAPI%E5%88%86%E6%9E%90%E3%80%82
#
# jwt, 2016/12/31

import json
import os
import base64
import requests
from Crypto.Cipher import AES

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext

def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)

def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return data

text = {
    "id": 80854505,
    "offset": 0,
    "total": True,
    "limit": 1000,
    "n": 1000,
    "csrf_token": ''
}

# encrypt the request information
encText = encrypted_request(text)
# component of the encrypted request
print encText['params']
print encText['encSecKey']
# playlist api url
url = "http://music.163.com/weapi/v3/playlist/detail?csrf_token="
sess = requests.Session()
r=sess.post(url, encText)

# number of tracks
idsJSON = r.json()['playlist']['trackIds']
print(len(idsJSON))
file = open('trackIds.json','w')
# file.write(json.dumps(r.json(), sort_keys=True,indent=4, separators=(',', ': ')))
file.write(json.dumps(idsJSON, sort_keys=True,indent=4, separators=(',', ': ')))
file.close()

# extract id only
ids = []
for i in range(len(idsJSON)):
    ids.append(idsJSON[i]['id'])
file = open('ids.json','w')
file.write(ids.__str__())
file.close()

# get song info, not so useful for song information
urlSong = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='

req = {
    "ids": [31168211, 1639852],
    "br": 320000,
    "csrf_token": ''
}

encText = encrypted_request(req)
r=sess.post(urlSong, encText)
file = open('songInfo.json','w')
file.write(json.dumps(r.json(), sort_keys=True,indent=4, separators=(',', ': ')))
file.close()
