#coding:utf-8
# 
# 
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import urllib
import zlib
import os

class MHDSpider():
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

    def parse(self,url,retry_count=7):
        driver = webdriver.PhantomJS("../phantomjs-2.1.1-windows/bin/phantomjs.exe")
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, 'html5lib')

        list_tag = soup.find('ul',id='chapter-list-1')
        com_a_list = list_tag.find_all('a',attrs={'href':True})

        driver.quit()

        base = 'https://www.manhuadui.com'
        comics_url_list = []
        for tag_a in com_a_list:
            url = base + tag_a['href']
            chapter = tag_a['title'].strip()
            comics_url_list.append((url,chapter))

        for url,cha in comics_url_list:
            for ec in self.err_char:
                if(cha.find(ec) != -1):
                    cha = cha.replace(ec,"_")
            
            self.chapter_path = self.main_path + cha
            is_ok = False 
            try_count = 0             
            while(not is_ok):
                is_ok = self.comics_parse(url)
                try_count = try_count + 1
                if(try_count > retry_count):
                    break
        

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

    def comics_parse(self,url):
        try:
            driver = webdriver.PhantomJS("../phantomjs-2.1.1-windows/bin/phantomjs.exe")
            #driver = webdriver.Chrome()
            driver.get(url)
            # content = driver.page_source
            # soup = BeautifulSoup(content, 'html5lib')
            # page_selects = soup.find('select',id='page_select')
            select = Select(driver.find_element_by_id('page_select'))
            count = len(select.options)
            r_step = []
            if os.path.exists(self.chapter_path):
                r_step = self.CheckFile(count)   
                str1 = self.chapter_path[len(self.main_path):]    
                self.WriteLog(r_step,str1,'PreCheck')
                if(r_step == []):
                    driver.quit()
                    return True

            step = []
            if r_step == []:
                for i in range(0,count):
                    step.append(i+1)
            else:
                step = r_step

            while(1):
                # content = driver.page_source
                # soup = BeautifulSoup(content, 'html5lib')
                # img_html = soup.find('div',id='images')
                # img_tag = img_html.find('img')
                img_info = driver.find_element_by_id('images').find_element_by_tag_name('img')
            
                #img_url = img_tag['src']
                img_url = img_info.get_attribute('src')
                img_page = img_info.get_attribute('data-index')
                img_page_n = int(img_page)
                img_page = img_page.zfill(3)
                if(img_page_n not in step):
                    driver.find_element_by_class_name('img_land_next').click()
                    continue
                self.save_image(img_page,img_url)
                if(img_page_n == count):
                    break
                driver.find_element_by_class_name('img_land_next').click()

            driver.quit()
            if os.path.exists(self.chapter_path):
                r_step = self.CheckFile(count)    
                str1 = self.chapter_path[len(self.main_path):] 
                self.WriteLog(r_step,str1,'Checked')    
                if(r_step == []):
                    return True
                else:
                    return False
        except Exception as e:
            print('page load error.')
            print(e)
            self.errfile = open(self.err_txt,'a')
            self.errfile.write('err chapter: '+self.chapter_path+'\n\n')
            self.close()
            return 0 

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