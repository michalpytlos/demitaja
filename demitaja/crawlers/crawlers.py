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
            posting_raw = json.loads(response.text)['posting']
            posting = {
                'web_id': posting_raw['id'],
                'title': '{} {}'.format(posting_raw['title']['title'], posting_raw['title']['level']),
                'posted': int(posting_raw['posted']/1000),
                'scraped': int(time.time()),
                'text': json.dumps(posting_raw),
                'employment_type': posting_raw['essentials']['employmentType'],
                'salary_from': posting_raw['essentials']['salaryFrom'],
                'salary_to': posting_raw['essentials']['salaryTo'],
                'salary_currency': posting_raw['essentials']['salaryCurrency'],
                'salary_period': posting_raw['essentials']['salaryDuration'],
                'cities': [posting_raw['city']] + [loc['city'] for loc in posting_raw.get('otherLocations', [])],
                'techs_must': [must['value'] for must in posting_raw['musts']],
                'techs_nice': [nice['value'] for nice in posting_raw['nices']]
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
