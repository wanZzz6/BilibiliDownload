from config import *
import subprocess
import re
import os
import requests
import json


def call_command(command):
    a = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    a.wait()
    if a.returncode == 0:
        out, err = a.communicate()
        return out.decode('utf-8')
    else:
        print('命令执行失败！')


def rename_file(path='.', prefix='', num=None):
    '''将目录下的文件重新命名
    可以单独运行此方法，以去掉指定文件夹下，所有文件的公共前缀prefix
    '''
    if num:
        name = part_index[num]
        for d in os.listdir(path):
            if name in d:
                newname = re.search('\d+\.\s*' + name + '\..*', d).group()
                os.rename(d, newname)
                return
    print('prefix', prefix)
    for d in os.listdir(path):
        if d.endswith('xml'):
            os.remove(os.path.join(directory, d))
        elif d.endswith('download'):
            pass
        else:
            temp = re.search('(' + prefix + ')*' + r'[\s#]*?(\d+).*(\..*)', d)
            if temp:
                try:
                    newname = temp.group(2) + '.' + part_index[int(temp.group(2))] + temp.group(3)
                    if d != newname:
                        os.rename(d, newname)
                        print('重命名：', d, '-->', newname)
                except KeyError as e:
                    print('重命名失败，请检查已下载文件前缀是否与视频标题一致，\
                    若不一致，请在main 方法里手动指定prefix\n',e)
                    return
            else:
                newname = re.sub('(' + prefix + ')?' + r'[\s#]*', '', d)
                if d != newname:
                    print('重命名：', d, '-->', newname)
                    os.rename(d, newname)


def get_index(url):
    '''获取所有part标题
    return : dict
    eg:
    {1: '01_项目资料说明',
     2: '02_前后端分离的认识',
     .....
    '''
    # 找到数据位置
    pattern = '<script>.*?({[^<]*}).*?</script>'
    # 清洗多余js
    fun_pattern = r';*?\s*?\(function\(.*?\{.*\}$'
    # 获取标题
    title_pattern = '<h1 title="([^"]+?)"'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'}
    try:
        res = requests.get(url, headers=header)
        data = re.findall(pattern, res.text)[-1]
        data = re.sub(fun_pattern, '', data)
        data = json.loads(data)
        part_index = {p['page']: p['part'] for p in data['videoData']['pages']}
    except Exception as e:
        print('获取索引失败！', e)
        part_index = {}
    try:
        title = re.search(title_pattern, res.text).group(1)
    except Exception as e:
        print('获取标题失败！', e)
        title = ''
    return part_index, title


part_index, prefix = get_index(url.format(av, 1))