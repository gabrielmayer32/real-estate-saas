import scrapy
import pandas as pd
import time

class MauritiusRealEstateSpider(scrapy.Spider):
    name = 'mauritius_realestate_ref'
    allowed_domains = ['lexpressproperty.com']
    max_retries = 10

    custom_settings = {
        'DOWNLOAD_DELAY': 10,  # Example delay, adjust as needed
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': True,
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'real_estate_data_with_ref.csv',  # Check this path
    }

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        self.df = pd.read_csv('real_estate_listings_modified.csv')
        
        # Create a new column 'ref' initialized to None
        self.df['ref'] = None

        for index, row in self.df.iterrows():
            yield scrapy.Request(
                url=row['details_link'], 
                callback=self.parse_details, 
                errback=self.errback, 
                headers=headers,  # Include headers with User-Agent
                meta={'index': index, 'retry_count': 0}
            )

    def parse_details(self, response):
        index = response.meta['index']
        ref = response.css('p:contains("Ref. LP")::text').re_first(r'Ref. LP : (\d+)')
        self.logger.info(f'Parsed ref for index {index}: {ref}')
        
        # Update the dataframe with the ref
        if ref:
            self.df.at[index, 'ref'] = ref

    def errback(self, failure):
        request = failure.request
        index = request.meta['index']
        retry_count = request.meta['retry_count']

        if hasattr(failure, 'value') and hasattr(failure.value, 'response') and failure.value.response is not None:
            response = failure.value.response
            if response.status == 429:
                if retry_count < self.max_retries:
                    retry_count += 1
                    self.logger.warning(f'Rate limit reached. Retrying {retry_count}/{self.max_retries} for index {index}.')
                    time.sleep(60)  # Add a longer delay before retrying
                    return scrapy.Request(
                        url=request.url, 
                        callback=self.parse_details, 
                        errback=self.errback, 
                        dont_filter=True,
                        headers=request.headers,  # Include original headers
                        meta={'index': index, 'retry_count': retry_count}
                    )
                else:
                    self.logger.error(f'Max retries reached for index {index}. Skipping.')
            else:
                self.logger.error(f'Non-retryable error encountered for index {index}. Status code: {response.status}.')
                self.logger.error(f'Error message: {failure.getErrorMessage()}')
        else:
            self.logger.error(f'Unknown error encountered for index {index}. Skipping.')

    def closed(self, reason):
        # Save the updated dataframe to a new CSV file
        self.df.to_csv(self.custom_settings['FEED_URI'], index=False)
        self.logger.info(f'Spider closed: {reason}')
