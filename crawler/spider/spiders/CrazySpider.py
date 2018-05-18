from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from spider.items.CrazyItem import CrazyItem

def str2num(string):
    try:
        return float(string)
    except ValueError:
        return None


class CrazySpider(CrawlSpider):
    name = "crazy_spider"
    allowed_domains = ['zoopla.co.uk', 'lid.zoocdn.com']
    start_urls = ["https://www.zoopla.co.uk/for-sale/property/nottingham/?identifier=nottingham&q=Nottingham&search_source=refine&radius=0&pn=1"]
    rules = (
        Rule(LinkExtractor(allow=('/for-sale/property/nottingham',),
                           deny=('tel',))),
        Rule(LinkExtractor(allow=('/for-sale/details/[0-9]+',),
                           deny=('image', 'play_movie')),
             callback="parse_info")
    )
    custom_settings = {'LOG_LEVEL':'INFO',}
                       #'LOG_FILE': 'log.txt',}


    def parse_info(self, response):
        '''Parse the house information'''

        image_addr = response.css("#images-main img::attr(src)").extract_first()
        # drop the house which does not provide image
        if(image_addr.find('noimage') != -1):
            return

        item = CrazyItem()

        item['price'] = str2num(response.css(
            ".text-price > strong::text").extract_first().strip().replace(",",
            "").replace("£",""))

        # drop the house which does not price or invalid price
        if not item['price']:
            return

        item['house_id'] = response.url.split("/")[-1]

        outcode = response.css(
            "html").re('outcode", "(.*)"')[0]
        incode = response.css(
            "html").re('incode", "(.*)"')[0]
        item['postcode'] = (outcode + " " + incode).lower()

        item['latitude'] = response.css('html').re('latitude" content="(.*)"')[0]
        item['longitude'] = response.css('html').re('longitude" content="(.*)"')[0]
        
        candidates_type = ['detached', 'semi_detached', 'flat', 'terraced',
            'detached_bungalow', 'end_terrace', 'town_house', 'bungalow',
            'cottage', 'semi_detached_bungalow', 'maisonette']
        item['property_type'] = response.css(
            "html").re('property_type", "(.*)"')
        
        # drop the house which does not belong to provided the house type
        if (len(item['property_type']) == 0 or
            item['property_type'][0] not in candidates_type):
            return
        else:
            item['property_type'] = item['property_type'][0]

        item['num_of_bathrooms'] = response.css(
            "html").re('num_baths", "(.*)"')
        if len(item['num_of_bathrooms']) == 0:
            item['num_of_bathrooms'] = None
        else:
            item['num_of_bathrooms'] = str2num(
                item['num_of_bathrooms'][0])

        item['num_of_bedrooms'] = response.css(
            "html").re('num_beds", "(.*)"')
        if len(item['num_of_bedrooms']) == 0:
            item['num_of_bedrooms'] = None
        else:
            item['num_of_bedrooms'] = str2num(
                item['num_of_bedrooms'][0])

        item['num_of_receptions'] = response.css(
            "html").re('num_recepts", "(.*)"')
        if len(item['num_of_receptions']) == 0:
            item['num_of_receptions'] = None
        else:
            item['num_of_receptions'] = str2num(
                item['num_of_receptions'][0])

        # drop the house without description
        if len(response.css("#tab-details > div")) < 4:
            return
        item['description'] = ''
        for each in response.css("#tab-details > div")[3:]:
            description = ' '.join(map(str.strip, each.css('*::text').extract()))
            if (description.find('Property description') != -1 or
                description.find('Property features') != -1):

                item['description'] += description


        # zoopla users rating
        item['overall_rating'] = str2num(
            response.css("span.star-rating-msg::text")[0].re("- (.*)%")[0])

        rating_rawstr = (
            response.css("li.current-rating::attr(style)").extract()[1:7])

        item['cs_rating'], item['en_rating'], item['pr_rating'], \
        item['rs_rating'], item['sp_rating'], item['tt_rating'] = \
            [str2num(each[6:-1]) for each in rating_rawstr]


        # parse svg // really tricky way
        url = ("https://www.zoopla.co.uk/widgets/local-info/local-authority-stats"
               "-chart.html?outcode=%s&amp;incode=%s&amp;category=demographic"
               % (outcode, incode))

        category_list = ['demographic', 'education', 'crime', 'counciltax',
                         'housing', 'employment', 'family', 'newspapers',
                         'interests']
        yield Request(url=url,
            callback=self.parse_svg,
            meta={'item': item,
                  'index': 0,
                  'category_list': category_list})

        yield Request(url=image_addr,
                      callback=self.save_image,
                      meta={'house_id': item['house_id'],
                            'price': str(item['price'])})

    def save_image(self, response):
        house_id = response.meta['house_id']
        price = response.meta['price']
        with open('./images/' + house_id +'.'+ price +'.jpg', 'wb') as image:
            image.write(response.body)

    def parse_svg(self, response):
        item = response.meta['item']
        index = response.meta['index']
        category_list = response.meta['category_list']
        category = category_list[index]
        url = response.url
        
        if index >= 4:
            i = 1
        else:
            i = 0
            if index == 3:
                url = url.replace(
                    "local-authority-stats-chart","neighbours-chart")

        list_of_str = response.css("script::text").re("\[(.*)\]")[i].split(",")
        item[category] = list(map(str2num, list_of_str))
        index += 1
        if index == len(category_list):
            yield item
        else:
            url = url.replace(category, category_list[index])
            yield Request(url=url,
                callback=self.parse_svg,
                meta={'item': item,
                      'index': index,
                      'category_list': category_list,})

