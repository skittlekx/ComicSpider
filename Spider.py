from Base import Base
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import os
import time

class MHDSpider(Base):
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
            ms = []
            if(cha in self.meta_data):
                ms = self.CheckFile(self.meta_data[cha])
                self.WriteLog(ms,cha,'PreCheck')
                if(ms == []):
                    continue
            
            is_ok = False 
            try_count = 0             
            while(not is_ok):
                page = self.comics_parse(url,ms)
                if(page == -1):
                    try_count = try_count + 1
                    if(try_count > retry_count):
                        break
                    continue
                if(cha not in self.meta_data):
                    self.meta_data[cha] = page
                    self.WriteMetaData()
                ms = self.CheckFile(self.meta_data[cha])
                self.WriteLog(ms,cha,'DownLoad')
                if ms == [] :
                    is_ok = True
                else:
                    is_ok = False

                try_count = try_count + 1
                if(try_count > retry_count):
                    break
 
    def comics_parse(self,url,r_step):
        try:
            driver = webdriver.PhantomJS("../phantomjs-2.1.1-windows/bin/phantomjs.exe")
            #driver = webdriver.Chrome()
            driver.get(url)
            # content = driver.page_source
            # soup = BeautifulSoup(content, 'html5lib')
            # page_selects = soup.find('select',id='page_select')
            select = Select(driver.find_element_by_id('page_select'))
            count = len(select.options)
            cha_page = count
            if os.path.exists(self.chapter_path):
                r_step = self.CheckFile(count)   
                str1 = self.chapter_path[len(self.main_path):]    
                self.WriteLog(r_step,str1,'PreCheck')
                if(r_step == []):
                    driver.quit()
                    return cha_page

            step = []
            if r_step == []:
                for i in range(0,count):
                    step.append(i+1)
            else:
                step = r_step

            if(step == []):
                return -1

            end = step[-1]
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
                if(img_page_n == end):
                    break
                driver.find_element_by_class_name('img_land_next').click()

            driver.quit()
            return cha_page
            # if os.path.exists(self.chapter_path):
            #     r_step = self.CheckFile(count)    
            #     str1 = self.chapter_path[len(self.main_path):] 
            #     self.WriteLog(r_step,str1,'Checked')    
            #     if(r_step == []):
            #         return True
            #     else:
            #         return False
        except Exception as e:
            print('page load error.')
            print(e)
            self.errfile = open(self.err_txt,'a')
            self.errfile.write('err chapter: '+url+'\n\n')
            self.errfile.close()
            return -1 

class MHDSpider_Phone(Base):
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
                ms = self.CheckFile(0)       
                self.WriteLog(ms,str1,'Check')
            while(ms or not isExist):
                cha_count = self.comics_parse(url,ms)
                isExist = os.path.exists(self.chapter_path)
                if isExist:
                    ms = self.CheckFile(cha_count)
                    self.WriteLog(ms,str1,'Fix')
        driver.quit()
    
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
            self.errfile.close()
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
            self.errfile.close()

class DM5Spider(Base):
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
            self.errfile.close()

