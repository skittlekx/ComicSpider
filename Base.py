#coding:utf-8
# 
# 
# from selenium import webdriver
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select
# from bs4 import BeautifulSoup
import urllib
import zlib
import os

class Base():
    main_path = ''
    chapter_path = ''
    errfile = []
    err_chapter=[]
    err_img=[]
    err_path=[]
    iserr = False
    err_txt = ''
    log_txt = ''
    logfile = ''
    meta_data = {}
    meta_txt = ''
    meta_file = ''

    err_char = [
        "\\",
        "/",
        ":",
        "*",
        "?",
        "\"",
        "<",
        ">",
        "|"
    ]

    def __init__(self,m_path,comicName):
        self.main_path = m_path
        self.main_path += comicName + '/'
        self.chapter_path = ''
        self.err_txt = self.main_path + 'err.txt'
        self.log_txt = self.main_path + 'log.txt'
        self.meta_txt = self.main_path + 'metadata.txt'
        if not os.path.exists(self.main_path):
            os.makedirs(self.main_path)
        self.logfile = open(self.log_txt,'w')
        self.logfile.close()
        self.iserr = False
        if(os.path.exists(self.meta_txt)):
            self.ReadMetaDate()

    def ReadMetaDate(self):
        self.meta_file = open(self.meta_txt,'r',encoding='utf-8')
        lines = self.meta_file.readlines()
        for line in lines:
            cha = line[:line.find('\t')]
            page = int(line[line.find('\t')+1:])
            if(cha not in self.meta_data):
                self.meta_data[cha] = page
        self.meta_file.close()

    def WriteMetaData(self):
        self.meta_file = open(self.meta_txt,'w',encoding='utf-8')
        for key in self.meta_data:
            str_ = key + '\t' + str(int(self.meta_data[key])) + '\n'
            self.meta_file.write(str_)
        self.meta_file.close()

    def WriteLog(self,ms,str1,mode):
        self.logfile = open(self.log_txt,'a',encoding='utf-8')
        if ms == []:
            str1 = str1 + ''' : '''+mode+''' OK!\n'''
            self.logfile.write(str1)
        else:
            str1 = str1 + ''' : '''+mode+''' error in pages : '''
            for mm in ms:
                str1 = str1 + str(mm) + ' '
            str1 = str1 + '\n'
            self.logfile.write(str1)
        self.logfile.close()

    def save_image(self,page_num,img_url):
        print('save image: '+page_num)
        print('image url: '+img_url)
        print('image path: '+self.chapter_path)

        Comics_path = self.chapter_path
        if not os.path.exists(Comics_path):
            os.makedirs(Comics_path)
        
        pic_name = Comics_path + '/' + page_num + '.jpg'

        if os.path.exists(pic_name):
            return
        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }

            req = urllib.request.Request(img_url, headers=headers)
            response = urllib.request.urlopen(req, timeout=30)

            # 请求返回到的数据
            data = response.read()

            # 若返回数据为压缩数据需要先进行解压
            if response.info().get('Content-Encoding') == 'gzip':
                data = zlib.decompress(data, 16 + zlib.MAX_WBITS)

            # 图片保存到本地
            fp = open(pic_name, "wb")
            fp.write(data)
            fp.close

            print('save image finished:' + pic_name)
        except Exception as e:
            print('save image error.')
            print(e)
    
    def CheckFile(self , c_num):
        if(c_num == -1):
            return []
        res = []
        files = os.listdir(self.chapter_path)
        k = 1
        end_file_name = 0
        for i,i_file in enumerate(files):
            fname = i_file[:i_file.find('.')]
            n_i = int(fname)
            num = i + k
            if num != n_i:
                sub = n_i - num
                sub_i = 0
                while(sub_i < sub):
                    res.append(num+sub_i)
                    k = k+1
                    sub_i = sub_i + 1
            end_file_name = n_i
        
        # file_count = len(files)
        if c_num != 0 and c_num != end_file_name:
            for i in range(end_file_name,c_num):
                res.append(i+1)
        return res