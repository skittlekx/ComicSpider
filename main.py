from Spider import MHDSpider

if __name__ == '__main__':
    save_path = 'C:/Users/skittle/Downloads/ToolKit/ComicSpider/Comics/'

    url = 'https://www.manhuadui.com/manhua/shanchangzhuonongrendeyuangaomutongxue/'
    name = '擅长捉弄的(原)高木同学'

    # url = 'http://www.dm5.com/manhua-yaojingdeweiba-bainianrenwu/'
    # name = '妖精的尾巴 百年任务'

    # url = 'https://m.manhuadui.com/manhua/NTRqiyue/'
    # name = 'NTR契约'

    spider = MHDSpider(save_path,name)
    spider.parse(url)