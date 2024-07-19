import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import time
from scrapy.spidermiddlewares.httperror import HttpError
import os
import csv

class MauritiusRealEstateSpider(scrapy.Spider):
    name = 'mauritius_realestate'
    allowed_domains = ['lexpressproperty.com']
    base_url = 'https://www.lexpressproperty.com/en/buy-mauritius/all/?currency=MUR&filters%5Binterior_unit%5D%5Beq%5D=m2&filters%5Bland_unit%5D%5Beq%5D=m2&p='
    max_page = 1000  # Specify the maximum number of pages to scrape
    max_retries = 10  # Max retries for 429 errors

    custom_settings = {
        'RETRY_TIMES': 8,
        'RETRY_HTTP_CODES': [429],
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': True,
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'test_new_db.csv',  # Path to save the final data
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_refs = self.load_existing_refs()

    def load_existing_refs(self):
        """Load existing refs from the CSV file into a set."""
        refs = set()
        if os.path.exists(self.custom_settings['FEED_URI']):
            with open(self.custom_settings['FEED_URI'], newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'ref' in row and row['ref']:
                        ref = row['ref'].strip()
                        refs.add(ref)
        return refs

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        for page_number in range(1, self.max_page + 1):
            yield scrapy.Request(url=f'{self.base_url}{page_number}', callback=self.parse, errback=self.errback, dont_filter=True, headers=headers)

    def parse(self, response):
        if response.status == 429:
            self.logger.warning('Rate limit reached. Sleeping for 60 seconds...')
            time.sleep(60)
            yield scrapy.Request(url=response.url, callback=self.parse, errback=self.errback, dont_filter=True)
            return

        properties = response.css('div.card-body')
        if not properties:
            self.logger.warning(f'No properties found on page: {response.url}')
        else:
            self.logger.info(f'Found {len(properties)} properties on page: {response.url}')

        for property in properties:
            title = property.css('h2.h3.mb-1 a::text').get()
            location = property.css('address a::text').get()
            price = property.css('strong.price.text-danger a::text').get()
            details_link = property.css('h2.h3.mb-1 a::attr(href)').get()
            description = property.css('div.option-holder ul.option-list li::text').getall()
            agency = property.css('div.logo-holder a img::attr(alt)').get()
            agency_logo = property.css('div.logo-holder a img::attr(src)').get()
            contact_phone = property.css('ul.list-contact a[href*="viewphone"]::attr(href)').get()
            contact_email = property.css('ul.list-contact a[href*="contact-form"]::attr(href)').get()
            contact_whatsapp = property.css('ul.list-contact a[href*="viewwhatsapp"]::attr(href)').get()

            details_link_full = response.urljoin(details_link)

            yield scrapy.Request(details_link_full, callback=self.parse_details, errback=self.errback, meta={
                'title': title,
                'location': location,
                'price': price,
                'details_link': details_link_full,
                'description': description,
                'agency': agency,
                'agency_logo': agency_logo,
                'contact_phone': contact_phone,
                'contact_email': contact_email,
                'contact_whatsapp': contact_whatsapp,
                'retry_count': 0
            })

        # Handle pagination via next page links if available
        next_page = response.css('li.pagination-next a::attr(href)').get()
        if next_page is not None:
            next_page_full = response.urljoin(next_page)
            yield scrapy.Request(next_page_full, callback=self.parse, errback=self.errback)

    def parse_details(self, response):
        title = response.meta['title']
        location = response.meta['location']
        price = response.meta['price']
        details_link = response.meta['details_link']
        description = response.meta['description']
        agency = response.meta['agency']
        agency_logo = response.meta['agency_logo']
        contact_phone = response.meta['contact_phone']
        contact_email = response.meta['contact_email']
        contact_whatsapp = response.meta['contact_whatsapp']
        retry_count = response.meta['retry_count']

        # Extract additional property details from the details page
        land_surface = response.css('dt:contains("Land surface") + dd::text').get()
        interior_surface = response.css('dt:contains("Interior surface") + dd::text').get()
        swimming_pool = response.css('dt:contains("Swimming pool") + dd::text').get()
        construction_year = response.css('dt:contains("Construction year") + dd::text').get()
        bedrooms = response.css('dt:contains("Bedroom(s)") + dd::text').get()
        accessible_to_foreigners = response.css('dt:contains("Accessible to foreigners") + dd::text').get()
        bathrooms = response.css('dt:contains("Bathroom(s)") + dd::text').get()
        toilets = response.css('dt:contains("Toilet(s)") + dd::text').get()
        aircon = response.css('dt:contains("Air-con") + dd::text').get()

        # Additional details from other sections
        general_features = response.css('#collapse-description-01 ul li::text').getall()
        indoor_features = response.css('#collapse-description-02 ul li::text').getall()
        outdoor_features = response.css('#collapse-description-03 ul li::text').getall()
        location_description = response.css('div.realty-description-block.pt-1.pt-md-2.pt-lg-3 h3 + p::text').getall()

        # Extract ref from details page
        ref = response.css('p:contains("Ref. LP")::text').re_first(r'Ref. LP : (\d+)')

        # Check if ref is already in the set of existing refs
        if ref and ref not in self.existing_refs:
            self.existing_refs.add(ref)
            yield {
                'title': title,
                'location': location,
                'price': price,
                'details_link': details_link,
                'description': description,
                'agency': agency,
                'agency_logo': agency_logo,
                'contact_phone': contact_phone,
                'contact_email': contact_email,
                'contact_whatsapp': contact_whatsapp,
                'land_surface': land_surface,
                'interior_surface': interior_surface,
                'swimming_pool': swimming_pool,
                'construction_year': construction_year,
                'bedrooms': bedrooms,
                'accessible_to_foreigners': accessible_to_foreigners,
                'bathrooms': bathrooms,
                'toilets': toilets,
                'aircon': aircon,
                'general_features': general_features,
                'indoor_features': indoor_features,
                'outdoor_features': outdoor_features,
                'location_description': location_description,
                'ref': ref
            }
        else:
            self.logger.info(f'Skipping property with ref {ref} as it is already in the CSV.')

    def errback(self, failure):
        request = failure.request
        retry_count = request.meta.get('retry_count', 0)

        if failure.check(HttpError):
            response = failure.value.response
            if response.status in [429, 520]:
                if retry_count < self.max_retries:
                    retry_count += 1
                    self.logger.warning(f'HTTP error {response.status} encountered. Retrying {retry_count}/{self.max_retries} for URL: {request.url}')
                    time.sleep(10)  # Add a longer delay before retrying
                    new_meta = request.meta.copy()
                    new_meta['retry_count'] = retry_count
                    yield scrapy.Request(
                        url=request.url, 
                        callback=self.parse_details, 
                        errback=self.errback, 
                        dont_filter=True,
                        headers=request.headers,  # Include original headers
                        meta=new_meta
                    )
                else:
                    self.logger.error(f'Max retries reached for URL: {request.url}. Skipping.')
            else:
                self.logger.error(f'HTTP error encountered: {response.status} for URL: {request.url}. Error message: {failure.getErrorMessage()}')
        else:
            self.logger.error(f'Unknown error encountered for URL: {request.url}. Error message: {failure.getErrorMessage()}')

    def closed(self, reason):
        self.logger.info(f'Spider closed: {reason}')

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(MauritiusRealEstateSpider)
    process.start()
