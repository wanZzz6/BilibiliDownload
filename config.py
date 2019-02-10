# 保存目录
directory = r'E:\Download'

url = 'https://www.bilibili.com/video/av{}/?p={}'

# 视频编号，从url获得
av = '43029596'

# 从第几个part开始下载， 如果一次没下载完，则下次需要调整此参数
# 若该视频没有 分 part，则设置 start = end =1
start = 1

#总 part 数
end = 80

# 防止下载中断，设置超时检查时间间隔(秒s)
timeout = 90
