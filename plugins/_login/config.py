from global_config import *
headers = {
    'Host': 'ca.nuc.edu.cn',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://ca.nuc.edu.cn/zfca/login',
    'Origin': 'https://ca.nuc.edu.cn',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
headers2 = {
    'origin': "https//ca.nuc.edu.cn",
    'x-devtools-emulate-network-conditions-client-id': "9497628b-38b3-47a8-b563-266e8ccd3a1d",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'accept': "*/*",
    'referer': "",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8",
    'cache-control': "no-cache",
    'postman-token': "7eb9be3a-35b0-2ad5-37ba-564d9b95895a"
}
headers4 = {
    "Host": "ca.nuc.edu.cn",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "http://i.nuc.edu.cn/portal.do?caUserName=1707004548&ticket=ST-12446-0oYw5csczjlmEoS1XyTN-zfca",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
headers3 = {
    "Host": "i.nuc.edu.cn",
    "Connection": "keep-alive",
    "Origin": "http://i.nuc.edu.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "DNT": "1",
    "Content-Type": "text/plain",
    "Accept": "*/*",
    "Referer": "http://i.nuc.edu.cn/portal.do?caUserName=1707004548&ticket=ST-12446-0oYw5csczjlmEoS1XyTN-zfca",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9"

}

postdata = {"username": "",
            "password": "",
            "j_captcha_response": "",
            "lt": "",
            "useValidateCode": "1",
            "isremenberme": "0",
            "ip": "",
            "losetime": "30",
            "_eventId": "submit",
            "submit1": ""}
postdata2 = {'callCount': '1',
             'page': '0',
             'httpSessionId': '',
             'scriptSessionId': '',
             'c0-scriptName': 'portalAjax',
             'c0-methodName': 'getAppList',
             'c0-id': '0',
             'c0-param0': 'string:142104994847723324',
             'batchId': '1'}

caurl = "https://ca.nuc.edu.cn/zfca/login"
vcodeurl = "https://ca.nuc.edu.cn/zfca/captcha.htm"
dwr_url = "http://i.nuc.edu.cn/dwr/call/plaincall/portalAjax.getAppList.dwr"
credit_url = "http://202.207.177.39:8089/gradeLnAllAction.do?oper=fainfo"
