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
from wx_crypt import WXBizMsgCrypt

def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def resp(request):
    nonce = request.GET.get('nonce')
    timestamp = request.GET.get('timestamp')
    signature = request.GET.get('signature')
    encodingAESKey = "WamDqAgkoSWRg1NzU6rTOQHxO1B5H90jfg6C0gb2LQr"
    to_xml = """ <xml><ToUserName><![CDATA[oia2TjjewbmiOUlr6X-1crbLOvLw]]></ToUserName><FromUserName><![CDATA[gh_7f083739789a]]></FromUserName><CreateTime>1407743423</CreateTime><MsgType>  <![CDATA[video]]></MsgType><Video><MediaId><![CDATA[eYJ1MbwPRJtOvIEabaxHs7TX2D-HV71s79GUxqdUkjm6Gs2Ed1KF3ulAOA9H1xG0]]></MediaId><Title><![CDATA[testCallBackReplyVideo]]></Title><Descript  ion><![CDATA[testCallBackReplyVideo]]></Description></Video></xml>"""
    token = "weixin"
    appid = "wx9872d15c79f229bf"
    print('微信发送的签名',signature)
    import hashlib
    sortlist = [token, timestamp, nonce]
    sortlist.sort()
    sha = hashlib.sha1()
    sha.update("".join(sortlist))
    print('本地拼接的签名',sha.hexdigest())

    encryp = WXBizMsgCrypt(token, encodingAESKey, appid)
    ret, encrypt_xml = encryp.EncryptMsg(to_xml, nonce)
    print(ret, encrypt_xml)

    return ret

