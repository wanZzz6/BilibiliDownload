import subprocess
import os
from function import call_command, get_index, rename_file, download_task

# 保存目录(不能有空格以及其他非法字符，否则会下载失败)
directory = r'F:\python操作数据库ORM'

# 视频编号，av开头
av = 'av83014115'

# 从第几个part开始下载， 如果一次没下载完，则下次需要调整此参数
# 若该视频没有 分 part，则设置 start = end =1, 若下载所有分片,设置end=-1
start = 1
end = -1


def main():
    global part_index, prefix
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)

    download_task(av, start, end)
    part_index, prefix = get_index(av)
    rename_file(directory, part_index, prefix)
    print('Finish!')

if __name__ == '__main__':
    main()
