from scrapy import Request
from scrapy.spiders import Spider
from scrapy.linkextractors import LinkExtractor
from spider.items.CrazyItem import CrazyItem

def str2num(string):
    try:
        return float(string)
    except ValueError:
        return None


class SingleSpider(Spider):
    name = "single_spider"

    def __init__(self, house_id, **kwargs):
        super().__init__(**kwargs)
        self.url = "https://www.zoopla.co.uk/for-sale/details/" + house_id

    def start_requests(self):
        yield Request(self.url, self.parse_info)

    def parse_info(self, response):
        item = CrazyItem()

        item['price'] = str2num(response.css(
            ".ui-pricing__main-price::text").extract_first().strip().replace(",",
            "").replace("£",""))

        if not item['price']:
            return

        item['house_id'] = response.url.split("/")[-1]

        outcode = response.css(
            "html").re('outcode: "(.*)"')[0]
        incode = response.css(
            "html").re('incode: "(.*)"')[0]
        item['postcode'] = (outcode + " " + incode).lower()

        candidates_type = ['detached', 'semi_detached', 'flat', 'terraced',
            'detached_bungalow', 'end_terrace', 'town_house', 'bungalow',
            'cottage', 'semi_detached_bungalow', 'maisonette']
        item['property_type'] = response.css(
            "html").re('property_type: "(.*)"')
        if (len(item['property_type']) == 0 or
            item['property_type'][0] not in candidates_type):
            return
        else:
            item['property_type'] = item['property_type'][0]

        item['num_of_bathrooms'] = response.css(
            "html").re('num_baths: ([0-9]*)')
        if len(item['num_of_bathrooms']) == 0:
            item['num_of_bathrooms'] = None
        else:
            item['num_of_bathrooms'] = str2num(
                item['num_of_bathrooms'][0])

        item['num_of_bedrooms'] = response.css(
            "html").re('num_beds: ([0-9]*)')
        if len(item['num_of_bedrooms']) == 0:
            item['num_of_bedrooms'] = None
        else:
            item['num_of_bedrooms'] = str2num(
                item['num_of_bedrooms'][0])

        item['num_of_receptions'] = response.css(
            "html").re('num_recepts": ([0-9]*)')
        if len(item['num_of_receptions']) == 0:
            item['num_of_receptions'] = None
        else:
            item['num_of_receptions'] = str2num(
                item['num_of_receptions'][0])


        url = "https://www.zoopla.co.uk/local-info/?outcode=%s&incode=%s" % (outcode, incode)
        yield Request(url=url,
            callback=self.parse_local_info,
            meta={'item': item,
                   'outcode': outcode,
                   'incode': incode})

        
    def parse_local_info(self, response):
        item = response.meta['item']
        outcode = response.meta['outcode']
        incode = response.meta['incode']

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


