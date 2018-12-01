import os
import sys
import time
import urllib3
import hashlib
import requests


def get_server_file(url, save_file_local_url):  # ,save_file_local_url
    #禁用安全请求警告
    requests.packages.urllib3.disable_warnings()
    # get请求，stream覆盖响应体行为，推迟响应体下载，关闭证书验证
    file_info = requests.get(url, stream=True, verify=False)
    '''为了保证文件下载的完整性，使用md5验证'''
    m = hashlib.md5()
    print('调试使用-请求头部信息==>',file_info.headers)
    # 获取文件大小
    file_size = int(file_info.headers['Content-Length'])
    print('file_size', type(file_size))
    print(file_size)
    # 获取文件名和保存路径进行拼接
    url_file_name = os.path.basename(url)
    absolute_file_path = save_file_local_url + '/' + url_file_name
    #准备计时变量
    old_time = 0
    end_time = 0
    # 判断本地是否有相同文件存在
    if os.path.isfile(absolute_file_path):
        # 文件存在，获取文件已下载大小
        file_exist_size = int(os.path.getsize(absolute_file_path))
        print('文件存在')
        print('file_exist_size====》', file_exist_size)
        print('file_size====》', file_size)
        if file_exist_size >= file_size:
            print('\033[1;31;40m文件下载完成，无需下载\033[0m')
            return
        else:
            print('file_exist_size', type(file_exist_size))
            #获取当前时间，单位时间戳   old_time开始时间
            old_time = time.time()
            # 重新发送请求，开始断点下载  Range请求头格式 range：bytes=[start,end]
            reset_send_request = requests.get(url, headers={'Range': 'bytes=%d-' % file_exist_size}, stream=True,
                                              verify=False)
            file = open(absolute_file_path, 'ab')
            # 使用块传输，减小资源消耗
            for write_disk in reset_send_request.iter_content(1024):
                if write_disk:
                    m.update(write_disk)
                    # 累加写入硬盘的大小
                    file_exist_size += len(write_disk)
                    # 写入数据，这里只是将数据写入内存，如果突然断点数据不会保存到硬盘中
                    file.write(write_disk)
                    # 强行将数据刷入硬盘
                    file.flush()
                    # show_progress(int(file_size),int(file_exist_size))
                    finish = int(50 * file_exist_size / file_size)
                    # print('finish',finish)
                    # print('download_file_size/all_file_size',int(int(download_file_size)/int(all_file_size)))
                    # sys.stdout.write(sys.stdout.write("\r[%s%s] %d%%" % ('>' * finish, ' ' * (50 - finish), 100 * (file_exist_size / file_size))))
                    # sys.stdout.flush()
                    sys.stdout.write(
                        "\r\033[1;36;40m|\033[0m\033[1;31;40m%s%s\033[0m\033[1;36;40m|\033[0m \033[1;32;40m%d%%\033[0m[已下载%.2fMB:总大小%.2fMB]" % ('>' * finish, ' ' * (50 - finish), 100 * file_exist_size / file_size,float(file_exist_size/1024/1024),float(file_size/1024/1024)))
                    # 显示了进度条立刻刷出缓存，否则缓存满的时候才会显示
                    sys.stdout.flush()
                    #print()
                else:
                    print('发送请求失败！！！！！')
            # 获取当前时间，单位时间戳   end_time结束时间
            end_time = time.time()
            file.close()
    else:
        # 获取当前时间，单位时间戳   old_time开始时间
        old_time = time.time()
        print('文件不存在')
        file_exist_size = 0
        # 重新发送请求，开始断点下载  Range请求头格式 range：bytes=[start,end]
        reset_send_request = requests.get(url, stream=True, verify=False,
                                          headers={'Range': 'bytes=%d-' % file_exist_size})
        file = open(absolute_file_path, 'ab')
        # 使用块传输，减小资源消耗
        for write_disk in reset_send_request.iter_content(1024):
            # print('write_disk',write_disk)
            if write_disk:
                m.update(write_disk)
                # 累加写入硬盘的大小
                file_exist_size += len(write_disk)
                # 写入数据，这里只是将数据写入内存，如果突然断点数据不会保存到硬盘中
                file.write(write_disk)
                # 强行将数据刷入硬盘
                file.flush()
                # show_progress(file_size, file_exist_size)
                finish = int(50 * file_exist_size / file_size)
                # print('finish',finish)
                # print('download_file_size/all_file_size',int(int(download_file_size)/int(all_file_size)))
                #显示进度条
                sys.stdout.write(
                    "\r\033[1;36;40m|\033[0m\033[1;31;40m%s%s\033[0m\033[1;36;40m|\033[0m \033[1;32;40m%d%%\033[0m[已下载%.2fMB:总大小%.2fMB]" % ('>' * finish, ' ' * (50 - finish), 100 * file_exist_size / file_size,float(file_exist_size/1024/1024),float(file_size/1024/1024)))
                #显示了进度条立刻刷出缓存，否则缓存满的时候才会显示
                sys.stdout.flush()
                #print()
            else:
                print('发送请求失败！！！！！')
        # 获取当前时间，单位时间戳   end_time结束时间
        end_time = time.time()
    print('\t')
    print('下载耗时:', '%.2f'%float(end_time - old_time),'s')
    print('文件MD5:', m.hexdigest())
    #关闭文件
    file.close()

#开始下载
get_server_file(sys.argv[1], sys.argv[2])

# 测试下载文件：http://p1.music.126.net/UJY2d3Fog3c3xnVcpxb9NQ==/109951163688615250.jpg
