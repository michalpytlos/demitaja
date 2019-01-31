import scrapy
import json
import time
from urllib.parse import urljoin
from scrapy.crawler import CrawlerProcess
from demitaja.utils.utils import create_posting, get_posting


class FluffSpider(scrapy.Spider):
    name = "quotes"
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True
    }
    base_url = 'https://nofluffjobs.com'

    def start_requests(self):
        urls = [
            urljoin(FluffSpider.base_url, 'api/search/posting?criteria=category%3Dbackend')
            ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse basic data on all the postings and create requests for
        those which are seen for the first time by the app.
        """
        for posting in json.loads(response.text)['postings']:
            if not get_posting(posting['id']):
                url = urljoin(FluffSpider.base_url, 'api/postingNew/' + posting['id'])
                yield scrapy.Request(url, callback=self.parse_posting)
                # break

    def parse_posting(self, response):
        """Parse full text of the posting and make a new posting
        entry in the database.
        """
        try:
            posting_raw = json.loads(response.text)
            posting = {
                'web_id': posting_raw['id'],
                'title': posting_raw['title'],
                'posted': int(posting_raw['posted']/1000),
                'scraped': int(time.time()),
                'text': json.dumps(posting_raw),
                'salaries': posting_raw['essentials']['salary']['types'],
                'salary_currency': posting_raw['essentials']['salary']['currency'],
                'salary_period': posting_raw['essentials']['salary']['period'],
                'cities': [loc['city'] for loc in posting_raw['location']['places']],
                'techs_must': [must['value'] for must in posting_raw['requirements']['musts']
                               if must['type'] == 'main'],
                'techs_nice': [nice['value'] for nice in posting_raw['requirements']['nices']
                               if nice['type'] == 'main']
            }
            create_posting(posting)
        except KeyError as err:
            print('Missing posting data:', err)


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(FluffSpider)
    process.start()
