#coding:utf-8
# 
# 
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
import zlib
import requests
import os
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time

class DM5Spider():
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
        if not os.path.exists(self.main_path):
            os.makedirs(self.main_path)
        self.logfile = open(self.log_txt,'w')
        self.logfile.close()
        self.iserr = False

    def close(self):
        self.errfile.close()

    def parse(self,url):
        driver = webdriver.Chrome()
        driver.get(url)
        
        dm = driver.find_element_by_class_name("detail-more")
        ActionChains(driver).move_to_element(dm).click(dm).perform()

        
        content = driver.page_source
        soup = BeautifulSoup(content, 'html5lib')

        list_tag = soup.find('div',id='chapterlistload')
        com_a_list = list_tag.find_all('a',attrs={'href':True})
        base = 'http://www.dm5.com'
        comics_info_list = []
        
        for tag_a in com_a_list:
            url = base + tag_a['href']
            chapter = tag_a.next.strip()
            page = int(tag_a.find('span').string[1:-2])

            comics_info_list.append((url,chapter,page))

        for url,cha,page_num in comics_info_list:
            for ec in self.err_char:
                if(cha.find(ec) != -1):
                    cha = cha.replace(ec,"_")
            
            self.chapter_path = self.main_path + cha
            ms = []
            isExist = os.path.exists(self.chapter_path)
            str1 = cha[:]
            if isExist:
                ms = self.CheckFile(page_num)       
                self.WriteLog(ms,str1,'Check')
            while(ms or not isExist):
                self.comics_parse(url,ms,page_num)
                isExist = os.path.exists(self.chapter_path)
                if isExist:
                    ms = self.CheckFile(page_num)
                    self.WriteLog(ms,str1,'Fix')
        driver.quit()

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

    def comics_parse(self,url,r_step,count):
        try:
            driver = webdriver.Chrome()
            driver.get(url)
            step = []
            if r_step == []:
                for i in range(0,count):
                    step.append(i+1)
            else:
                step = r_step
            end = step[-1]
            while(1):
                time.sleep(3)
                content = driver.page_source
                # fw = open('html.txt','w',encoding='utf-8')
                # fw.write(content)
                # fw.close()
                soup = BeautifulSoup(content, 'html5lib')
                container = soup.find('div',class_='view-paging').find('div',class_='container')
                currentpage = int(container.find('span',class_='current').string)
                if(currentpage not in step):
                    continue

                img_div = soup.find('div',id='cp_img')
                img_url = img_div.find('img',id='cp_image')['src']

                img_page = str(currentpage).zfill(3)
                self.save_image(img_page,img_url)
                if(currentpage == end):
                    break
                
                blocks = driver.find_elements_by_class_name('block')
                for block  in blocks:
                    tt = block.text
                    if(tt == '下一页'):
                        ActionChains(driver).move_to_element(block).click(block).perform()
                        break
            driver.close()
            
        except Exception as e:
            print('page load error.')
            print(e)
            self.errfile = open(self.err_txt,'a')
            self.errfile.write('err chapter: '+self.chapter_path+'\n\n')
            self.close()

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

            # urllib.request.urlretrieve(img_url,filename=pic_name)

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
    
    def CheckFile(self , c_num = 0):
        res = []
        files = os.listdir(self.chapter_path)
        k = 1
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
        file_count = len(files)
        if res == [] and c_num != 0 and c_num != file_count:
            for i in range(len(files),c_num):
                res.append(i+1)
        return res

