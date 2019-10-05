#coding:utf-8
# 
# 
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
import zlib
import requests
import os

class MHDSpider_m():
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
        mobile = {'deviceName': 'iPhone X'}  #设置所模拟的硬件
        options = webdriver.ChromeOptions() 
        options.add_experimental_option('mobileEmulation',mobile)
        driver = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=options)

        #driver = webdriver.Chrome()
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, 'html5lib')

        list_tag = soup.find('ul',id='chapter-list-1')
        com_a_list = list_tag.find_all('a',attrs={'href':True})
        base = 'https://m.manhuadui.com'
        comics_url_list = []
        
        for tag_a in com_a_list:
            url = base + tag_a['href']
            #chapter = tag_a['title'] # PC
            chapter = tag_a.find('span').string # phone
            comics_url_list.append((url,chapter))
        # url = comics_url_list[0][0]
        # url = comics_url_list[0][0]
        # url = url+'?p=1'
        # if self.iserr:
        #     count = len(self.err_img)
        #     for i in range(count):
        #         self.chapter_path = self.err_path[i]
        #         self.pic_parse(self.err_img[i][1])
        for url,cha in comics_url_list:
            self.chapter_path = self.main_path + cha
            ms = []
            isExist = os.path.exists(self.chapter_path)
            str1 = cha[:]
            if isExist:
                ms = self.CheckFile()       
                self.WriteLog(ms,str1,'Check')
            while(ms or not isExist):
                cha_count = self.comics_parse(url,ms)
                isExist = os.path.exists(self.chapter_path)
                if isExist:
                    ms = self.CheckFile(cha_count)
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

    def comics_parse(self,url,r_step):
        try:
            #driver = webdriver.Chrome()
            mobile = {'deviceName': 'iPhone X'}  #设置所模拟的硬件
            options = webdriver.ChromeOptions() 
            options.add_experimental_option('mobileEmulation',mobile)
            driver = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=options)

            driver.get(url)
            content = driver.page_source
            soup = BeautifulSoup(content, 'html5lib')
            img_html = soup.find('div',id='images')
            img_info = img_html.find('p',class_='img_info')
            page_info = img_info.string
            page_num = page_info[page_info.find('/')+1:-1]
            page_num_i = int(page_num)
            step = []
            if r_step == []:
                step = range(2,page_num_i + 1)
                img_tag = img_html.find('img')
                img_url = img_tag['src']
                img_page = img_tag['data-index']
                img_page = img_page.zfill(3)
                self.save_image(img_page,img_url)
            else:
                step = r_step
            driver.close()
            for i in step:
                _url = url + '?p=' + str(i)
                print(_url)
                self.pic_parse(_url)
            return page_num_i
        except Exception as e:
            print('page load error.')
            print(e)
            self.errfile = open(self.err_txt,'a')
            self.errfile.write('err chapter: '+self.chapter_path+'\n\n')
            self.close()
            return 0 

    def pic_parse(self,url):
        try:
            #driver = webdriver.Chrome()
            mobile = {'deviceName': 'iPhone X'}  #设置所模拟的硬件
            options = webdriver.ChromeOptions() 
            options.add_experimental_option('mobileEmulation',mobile)
            driver = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=options)

            driver.get(url)
            content = driver.page_source
            soup = BeautifulSoup(content, 'html5lib')
            img_html = soup.find('div',id='images')
            img_tag = img_html.find('img')
            img_url = img_tag['src']
            img_page = img_tag['data-index']
            img_page = img_page.zfill(3)
            self.save_image(img_page,img_url)
            driver.close()
        except Exception as e:
            print('page load error.')
            print(e)
            self.errfile = open(self.err_txt,'a')
            self.errfile.write('err url: '+url+'\n')
            #self.errfile.write('err info: '+e+'\n')
            self.errfile.write('right path: '+self.chapter_path+'\n\n')   
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

    def ReLoad(self):
        err_txt = self.main_path + 'err.txt'
        if not os.path.exists(err_txt):
            return
        err = open(err_txt,'r')

        lines = err.readlines()
        
        for line in lines:
            if line == '\n':
                continue
            if(line.find('err chapter') != -1):
                self.err_chapter.append(line[line.rfind('/')+1:line.find('\n')])
                continue
            if(line.find('err url') != -1):
                img_num = line[line.rfind('=')+1:line.find('\n')]
                img_link = line[line.find(':')+2:line.find('\n')]
                self.err_img.append((img_num,img_link))
            else :
                self.err_path.append(line[line.find(':')+2:line.find('\n')])
        
        if self.err_chapter or self.err_img:
            self.iserr = True
        err.close()
        err = open(err_txt,'w')
        err.write('')
        err.close()

