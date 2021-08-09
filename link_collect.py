#coding: utf-8
from os import error
from typing import Sized
import requests
import re
import argparse
import sys
from requests.api import head

parser = argparse.ArgumentParser(description='收集页面html源码下的url。多多少少还有点问题~')
parser.add_argument("-u", help = 'Input URL (e.g. "http://example.com/")', required=True)
parser.add_argument("-o", help = 'Output to a file. (e.g. "result.txt")')
parser.add_argument("--src", help = 'Search <src>. (e.g. on, default off.)')
parser.add_argument("-b", help = 'Black name. Use "," to split it. (e.g. "jpg,gif")')
args = parser.parse_args()
headers = {
    'Content-Type': 'text/html; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}
result = ''

#判断url中的域名
def find_domain():
    blacklist = ['http://', 'https://', 'www.', '/']
    url = args.u
    for i in range(0,len(blacklist)):
        url = url.replace(blacklist[i],'')
    domain = url
    print('\nDomain: ' + domain + '\n')
    return domain


def find_url(string, domain):
    url_list = []
    
    
    collect_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    for i in range(0, len(collect_url)):
        if domain in collect_url[i]:
            if collect_url[i] not in url_list:      #去重
                url_list.append(collect_url[i])
                #url_list
    
    #爬取href标签
    href_url = re.findall('<a.+?href=\"(.+?)\".*>', string)
    for i in range(0, len(href_url)):
        if ('http' or 'https') not in href_url[i]:
            href_url[i] = args.u + href_url[i]
        if (href_url[i] not in url_list) and (domain in href_url[i]):
            url_list.append(href_url[i])

    return url_list

def find_srcurl(string, domain):
    src_list = []
    #爬取src标签
    src_url = re.findall('<*.+?src=\"(.+?)\".*>', string)
    for i in range(0, len(src_url)):
        if ('http' or 'https') not in src_url[i]:
            if '.' in src_url[i]:
                src_url[i].replace('.', '')
            src_url[i] = args.u + src_url[i]
        if (src_url[i] not in src_list) and (domain in src_url[i]):
            src_list.append(src_url[i])
    
    return src_list


#连接url，返回响应包体
def connect():

    global headers
    res = requests.get(args.u, headers=headers, timeout=5)
    print('\nCode: '+str(res.status_code)+'\n')
    return res.text


#把列表转换成字符串
def exchange(list):

    r = "\n".join([str(list[i]) for i in range(0, len(list),2)])
    return r

#不显示含黑名单单词的url
def block_black(list):
    try:
        blacklist = args.b
        blist = blacklist.split(',')
    except error as e:
        print('Use "," to split it!!!')
   
   #除去黑名单内单词
    for i in range(0, len(blist)):
        for j in range(0, len(list)):
            if blist[i] in list[j]:
                list[j] = ''
    while '' in list:
        list.remove('')
    
    return list
            


#输出成文件
def Output(string):

    try:
        print(string)
        with open('{0}'.format(args.o),'w') as f:
            f.write(string)
            f.write('\n')
    except BaseException as e:
        print("\n文件错误\n")


#选项控制
def control_options(args, domain, text):

    global result
    if args == None or args.u == None:
        print('\nTry to use -h, and -u is required.\n')
        exit(0)
    #run -u
    if args.u:
        url_list = find_url(text, domain)
        if args.b:
            src_result = block_black(url_list)
        url_result = exchange(url_list)
        result = '\nCommon url list: \n' + url_result
    
    if args.src:
        src_list = find_srcurl(text, domain)
        if args.b:
            src_result = block_black(src_list)
        src_result = exchange(src_list)
        
        result = '\nCommon url list: \n' + url_result + '\nSrc list: \n' + src_result
        

    print(result)
    if args.o:  #run -o
        Output(result)



def main():

    try:
        domain = find_domain()
        res_text = connect()

        control_options(args, domain, res_text)
    except KeyboardInterrupt as e:
        print(" Stop !\n")
        exit(0)
    


if __name__ == '__main__':
    main()