# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from dailytool import selenium_test
import requests
import json
from common.mymako import render_mako_context
from django.http import HttpResponse, JsonResponse
from wx_crypt import WXBizMsgCrypt
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger("root")

# 微信公众号信息
encodingAESKey = "L0DCOdO4gwT19Qme65ctAKEPaNKCbDq8mQ8jdwmNQna"
to_xml = """ <xml><ToUserName><![CDATA[oia2TjjewbmiOUlr6X-1crbLOvLw]]></ToUserName><FromUserName><![CDATA[gh_7f083739789a]]></FromUserName><CreateTime>1407743423</CreateTime><MsgType>  <![CDATA[video]]></MsgType><Video><MediaId><![CDATA[eYJ1MbwPRJtOvIEabaxHs7TX2D-HV71s79GUxqdUkjm6Gs2Ed1KF3ulAOA9H1xG0]]></MediaId><Title><![CDATA[testCallBackReplyVideo]]></Title><Descript  ion><![CDATA[testCallBackReplyVideo]]></Description></Video></xml>"""
url_to_xml = "<xml><ToUserName>< ![CDATA[toUser] ]></ToUserName><FromUserName>< ![CDATA[fromUser] ]></FromUserName><CreateTime>12345678</CreateTime><MsgType>< ![CDATA[news] ]></MsgType><ArticleCount>1</ArticleCount><Articles><item><Title>< ![CDATA[title1] ]></Title> <Description>< ![CDATA[description1] ]></Description><PicUrl>< ![CDATA[picurl] ]></PicUrl><Url>< ![CDATA[url] ]></Url></item></Articles></xml>"
token = "weixin"
appid = "wx9872d15c79f229bf"


def index(request):
    # 检验用户
    openid = request.GET.get('opendid')
    # 获取 access_token
    resp = requests.get(
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx9872d15c79f229bf&secret=5f1560a4e631f17bdb48444f274281d2')

    access_token = eval(resp.text)['access_token']

    data = {
        'tagid': '101',
    }
    resp = requests.post('https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token={}'.format(access_token),
                         data=json.dumps(data))

    openid_list = json.loads(resp.content)['data']['openid']
    if openid not in openid_list:
        return HttpResponse(403)

    return render_mako_context(request, '/home_application/fadein_index.html')


def home(request):
    """
   首页
   """
    return render_mako_context(request, '/home_application/home.html')


@csrf_exempt
def bankcard(request):
    # 获取参数
    user_name = requests.POST.get('user_name')
    real_name = requests.POST.get('real_name')
    session_id = selenium_test.get_session()

    headers = {
        "Cookie": "bcsession={}".format(session_id),
        "host": "bms.shitou.com"
    }
    if user_name:
        data = {
            "userName": user_name,
            "realName": "",
            "idCard": "",
            "type": -1,
            "page": 1,
            "rows": 10,
        }
    else:
        data = {
            "userName": "",
            "realName": real_name,
            "idCard": "",
            "type": -1,
            "page": 1,
            "rows": 10,
        }
    # 调用获取userid接口
    resp = requests.post('http://10.117.20.152:8080/console/memberManage/queryUserInfoList', data=data, headers=headers)
    user_id = json.loads(resp.content)["rows"][0]["id"]

    # 调用本地银行卡查询接口
    resp = requests.post('http://10.117.20.152:8080/console/memberManage/localcardInfoList/{}'.format(user_id),
                         headers=headers)
    info = json.loads(resp.content)
    local_bank_type = info["rows"][0]['bankPropTypeFormat']
    local_bank_card = info["rows"][0]['openAcctId']
    local_bank_id = info["rows"][0]['openBankId']
    local_is_default = info["rows"][0]['isDefault']
    local_is_sign = info["rows"][0]['isSignFormat']
    local_is_express = info["rows"][0]['expressFlag']
    # 调用汇付银行卡查询接口
    resp = requests.post('http://10.117.20.152:8080/console/memberManage/cardInfoComparisonList/{}'.format(user_id),
                         headers=headers)
    info = json.loads(resp.content)
    try:
        huifu_bank_card = info["rows"][0]['cardId']
        huifu_bank_id = info["rows"][0]['bankId']
        huifu_is_default = info["rows"][0]['isDefault']
        huifu_is_express = info["rows"][0]['expressFlag']
    except Exception as e:
        logger.error(e, '汇付银行卡信息读取异常')
        return JsonResponse({'code': '-1', 'msg': '汇付银行卡信息读取异常请联系运维颜传辉'})

    data = {'code': '0', 'msg': 'ok',
            'local_info': {"local_bank_type": local_bank_type, 'local_bank_card': local_bank_card,
                           "local_bank_id": local_bank_id, "local_is_default": local_is_default,
                           "local_is_sign": local_is_sign, "local_is_express": local_is_express,
                           "huifu_bank_card": huifu_bank_card, "huifu_bank_id": huifu_bank_id,
                           "huifu_is_default": huifu_is_default, "huifu_is_express": huifu_is_express
                           }}

    return JsonResponse(data)


@csrf_exempt
def wx_response(request):
    # 服务器验证
    if request.method == "GET":
        nonce = request.GET.get('nonce')
        timestamp = request.GET.get('timestamp')
        signature = request.GET.get('signature')
        echostr = request.GET.get('echostr')
        print('wxsend', signature)
        import hashlib
        sortlist = [token, timestamp, nonce]
        sortlist.sort()
        sha = hashlib.sha1()
        sha.update("".join(sortlist))
        print('local', sha.hexdigest())

        encryp = WXBizMsgCrypt.WXBizMsgCrypt(token, encodingAESKey, appid)
        ret, encrypt_xml = encryp.EncryptMsg(to_xml, nonce)
        print(ret, encrypt_xml)
        if signature == sha.hexdigest():
            print('ok')
            return HttpResponse(echostr)
        return HttpResponse('')
    # 消息回复
    elif request.method == 'POST':
        # 解码
        nonce = request.GET.get('nonce')
        timestamp = request.GET.get('timestamp')
        openid = request.GET.get('openid')
        # signature = request.GET.get('signature')
        msg_signature = request.GET.get('msg_signature')
        decrypt_test = WXBizMsgCrypt.WXBizMsgCrypt(token, encodingAESKey, appid)
        from_xml = request.body
        print(from_xml)
        print('========')
        ret, decryp_xml = decrypt_test.DecryptMsg(from_xml, msg_signature, timestamp, nonce)
        print(ret)
        print('========')
        print(decryp_xml)
        othercontent = autoreply(decryp_xml, openid)
        print('------')
        print(othercontent)
        print('------')
        return HttpResponse(othercontent)


import xml.etree.ElementTree as ET


def autoreply(decryp_xml, openid):
    try:
        xml_data = ET.fromstring(decryp_xml)
        msg_type = xml_data.find('MsgType').text
        to_user_name = xml_data.find('ToUserName').text
        from_user_name = xml_data.find('FromUserName').text
        create_time = xml_data.find('CreateTime').text
        msg_type = xml_data.find('MsgType').text
        msg_id = xml_data.find('MsgId').text

        to_user = from_user_name
        from_user = to_user_name

        if msg_type == 'text':
            content = "test"
            reply_msg = TextMsg(to_user, from_user, content, openid)
            return reply_msg.send()
        if msg_type == 'image':
            reply_msg = PhotoTextMsg(to_user, from_user, openid)
            return reply_msg.send()

    except Exception, e:
        return e


# class Msg(object):
#     def __init__(self, xml_data):
#         self.ToUserName = xml_data.find('ToUserName').text
#         self.FromUserName = xml_data.find('FromUserName').text
#         self.CreateTime = xml_data.find('CreateTime').text
#         self.MsgType = xml_data.find('MsgType').text
#         self.MsgId = xml_data.find('MsgId').text


import time


class TextMsg(object):
    def __init__(self, to_user_name, from_user_name, content, openid):
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)


class PhotoTextMsg(object):

    def __init__(self, to_user_name, from_user_name, openid):
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] = int(time.time())
        self.__dict[
            'Picurl'] = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcWO3m0yLORQ1FqzPhNTZPnXo1oH7qxGGNnwbvr-qbrBFLFOz-'
        self.__dict['Url'] = 'http://wxops.invstone.cn/wx/index?openid={}'.format(openid)

    def send(self):
        xml = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount>
        <Articles>
        <item><Title><![CDATA[用户信息查询]]></Title>
        <Description><![CDATA[用户信息查询]]></Description>
        <PicUrl><![CDATA[{Picurl}]]></PicUrl>
        <Url><![CDATA[{Url}]]></Url>
        </item>
        </Articles>
        </xml>        
        """
        print(self.__dict)
        return xml.format(**self.__dict)
