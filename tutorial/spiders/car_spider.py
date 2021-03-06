from scrapy import Request
import scrapy
import re
import execjs
from tutorial.items import TutorialItem
from collections import OrderedDict


class CarSpider(scrapy.Spider):
    name = 'car'
    allowed_domains = ['guazi.com']
    url = 'https://www.guazi.com/www/'

    def start_requests(self):
        yield Request(url=self.url, dont_filter=True, callback=self.get_cookie)

    def get_cookie(self, response):
        pattern = re.compile('var value=anti\(\'(.*?)\',\'(.*?)\'\);')
        value = re.search(pattern, response.text).groups()

        with open('antipas.js', 'r', encoding='utf-8') as f:
            source = f.read()
            phantom = execjs.get('PhantomJS')
            getpass = phantom.compile(source)
            antipas = getpass.call('get_antipas', value[0], value[1])

        cookies = {
            'antipas': antipas
        }
        yield Request(url=self.url, cookies=cookies, dont_filter=True, callback=self.buy_car)

    def buy_car(self, response):
        for page in range(1, 100):
            buy_url = 'https://www.guazi.com/www/buy/o{page}'.format(page=page)
            yield Request(url=buy_url, callback=self.buy_parse)

    def buy_parse(self, response):
        res = response.xpath('//ul[@class="carlist clearfix js-top"]/li/a')
        for cell in res:
            name = cell.xpath('./div[@class="t"]/text()').extract()[0]
            line = cell.xpath('./div[@class="t-i"]/text()').extract()
            price = cell.xpath('./div[@class="t-price"]/p/text()').extract()[0] + cell.xpath('./div[@class="t-price"]/p/span/text()').extract()[0]
            new_car_price = cell.xpath('./div[@class="t-price"]/em/text()').extract()
            tag = '; '.join(cell.xpath('./div[@class="t-price"]/i/text()').extract())
            pic = cell.xpath('./img/@src').extract()[0]
            url = 'https://www.guazi.com' + cell.xpath('./@href').extract()[0]

            item = OrderedDict(TutorialItem())
            item['name'] = name
            item['time'] = line[0]
            item['mileage'] = line[1]
            item['place'] = line[2]
            item['price'] = price
            item['new_car_price'] = new_car_price[0] if new_car_price else ''
            item['tag'] = tag
            item['pic'] = pic
            item['url'] = url
            yield item
