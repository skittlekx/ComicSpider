from phantomjsTestMHD import MHDSpider
from driverTestMHD import MHDSpider_m
from phantomjsTestDM5 import DM5Spider

if __name__ == '__main__':
    save_path = 'C:/Users/skittle/Downloads/ToolKit/ComicSpider/Comics/'

    url = 'https://www.manhuadui.com/manhua/yeliangshen/'
    name = '野良神'

    # url = 'http://www.dm5.com/manhua-yaojingdeweiba-bainianrenwu/'
    # name = '妖精的尾巴 百年任务'

    # url = 'https://m.manhuadui.com/manhua/NTRqiyue/'
    # name = 'NTR契约'

    spider = MHDSpider(save_path,name)
    spider.parse(url)