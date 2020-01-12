import subprocess
import re
import os
import requests
import json

_URL_PATTERN = 'https://www.bilibili.com/video/{av}/?p={p}'
# 防止下载中断，设置超时检查时间间隔(秒s)
timeout = 120


def call_command(command) -> bool:
    a = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    a.wait()
    if a.returncode == 0:
        return True
    else:
        print('命令执行失败！')
        return False


def rename_file(path, part_index, prefix='', num=None):
    '''将目录下的文件重新命名
    可以单独运行此方法，以去掉指定文件夹下，
    所有文件的最大公共前缀, 或者指定的prefix
    '''
    if num:
        name = part_index[num]
        for d in os.listdir(path):
            if d.endswith('xml'):
                os.remove(os.path.join(path, d))
                continue
            if name in d:
                # version :1
                # newname = re.search('\d+\.\s*'+ name + '\..*', d).group()
                temp = re.search(r'\(([^)]*)\).*?(\..*)$', d)
                newname = temp.group(1) + temp.group(2)
                if newname != d:
                    os.rename(d, newname)
                    print('重命名：', d, '-->', newname)
        return

    for d in os.listdir(path):
        if d.endswith('xml'):
            os.remove(os.path.join(directory, d))
        elif d.endswith('download'):
            continue
        else:
            try:
                temp = re.search('(' + prefix + ')*' + r'.*?P(\d+).*(\..*)$',
                                 d)
                if temp:
                    newname = 'P' + temp.group(2) + '.' + part_index[int(
                        temp.group(2))] + temp.group(3)
                    if d != newname:
                        os.rename(d, newname)
                        print('重命名：', d, '-->', newname)
                else:
                    newname = re.sub('(' + prefix + ')+' + r'[\s#]*', '', d)
                    if d != newname:
                        os.rename(d, newname)
                        print('重命名：', d, '-->', newname)
            except KeyError as e:
                print('重命名失败，请检查已下载文件前缀是否与视频标题一致，\
                    若不一致，请在main 方法里手动指定prefix\n', e)
                return
            except Exception as e:
                print('Error in "rename_file"', e)
                continue


def get_index(av):
    '''获取所有part标题
    return : dict
    eg:
    {1: '01_项目资料说明',
     2: '02_前后端分离的认识',
     .....
    '''
    # 找到数据位置
    pattern = '<script>[^<]*?({[^<]*}).*?</script>'
    # 清洗多余js
    fun_pattern = r'[\s;\(]*?function\s?\(.*?\{.*\}$'
    # 获取标题
    title_pattern = '<h1 title="([^"]+?)"'
    header = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'
    }
    try:
        res = requests.get(make_url(av, 1), headers=header)
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


def download_task(av: str, start: int = 1, end: int = -1, task_list=[]):
    part_index, prefix = get_index(av)

    if len(task_list) == 0:
        if end == -1 or end > len(part_index.values()):
            end = len(part_index.values())
        if end < start:
            raise ValueError("请输入正确的分片地址")
        # 生成下载队列
        task_list = list(range(start, end + 1))

    while task_list:
        p = task_list.pop(0)
        try:
            result = download_av_p(av, p)
            if result:
                # 下载成功，重命名
                rename_file(os.getcwd(), part_index, num=p)
                print('OK')
            else:
                print('稍后下载： {}'.format(p))
                task_list.append(p)
        except subprocess.TimeoutExpired:
            task_list.insert(0, p)
        except Exception as e:
            print(e)
            exit(-1)


def make_url(av, p):
    return _URL_PATTERN.format(av=av, p=p)


def download_av_p(av, p):
    url = make_url(av, p)
    return _download_from_url(url)


def _download_from_url(url) -> bool:
    """
    从url下载视频，保存到当前工作目录下
    """
    cmd = 'you-get -o {directory} {url}'.format(url=url, directory=os.getcwd())
    print(cmd)
    result = subprocess.call(cmd, timeout=timeout)
    if result == 0:
        print('Download Success!', end='')
        return True
    else:
        print('Download Fail!\n请检查保存路径是否有非法字符，或者尝试\
            pip instal -U you-get')
        return False
