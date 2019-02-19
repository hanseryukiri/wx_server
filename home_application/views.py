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

from common.mymako import render_mako_context
from django.http import HttpResponse
from wx_crypt import WXBizMsgCrypt
from django.views.decorators.csrf import csrf_exempt

# 微信公众号信息
encodingAESKey = "L0DCOdO4gwT19Qme65ctAKEPaNKCbDq8mQ8jdwmNQna"
to_xml = """ <xml><ToUserName><![CDATA[oia2TjjewbmiOUlr6X-1crbLOvLw]]></ToUserName><FromUserName><![CDATA[gh_7f083739789a]]></FromUserName><CreateTime>1407743423</CreateTime><MsgType>  <![CDATA[video]]></MsgType><Video><MediaId><![CDATA[eYJ1MbwPRJtOvIEabaxHs7TX2D-HV71s79GUxqdUkjm6Gs2Ed1KF3ulAOA9H1xG0]]></MediaId><Title><![CDATA[testCallBackReplyVideo]]></Title><Descript  ion><![CDATA[testCallBackReplyVideo]]></Description></Video></xml>"""
url_to_xml = "<xml><ToUserName>< ![CDATA[toUser] ]></ToUserName><FromUserName>< ![CDATA[fromUser] ]></FromUserName><CreateTime>12345678</CreateTime><MsgType>< ![CDATA[news] ]></MsgType><ArticleCount>1</ArticleCount><Articles><item><Title>< ![CDATA[title1] ]></Title> <Description>< ![CDATA[description1] ]></Description><PicUrl>< ![CDATA[picurl] ]></PicUrl><Url>< ![CDATA[url] ]></Url></item></Articles></xml>"
token = "weixin"
appid = "wx9872d15c79f229bf"

def index(request):
    return render_mako_context(request, '/home_application/fadein_index.html')

def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


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
