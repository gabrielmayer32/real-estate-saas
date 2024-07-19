import scrapy

class MauritiusRealEstateSpider(scrapy.Spider):
    name = 'mauritius_realestate'
    allowed_domains = ['lexpressproperty.com']
    base_url = 'https://www.lexpressproperty.com/en/buy-mauritius/all/?currency=MUR&filters%5Binterior_unit%5D%5Beq%5D=m2&filters%5Bland_unit%5D%5Beq%5D=m2&p='
    max_page = 1000  # Specify the maximum number of pages to scrape

    def start_requests(self):
        for page_number in range(1, self.max_page + 1):
            yield scrapy.Request(url=f'{self.base_url}{page_number}', callback=self.parse)

    def parse(self, response):
        for property in response.css('div.card-body'):
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

            # Follow the details link to scrape additional property details
            yield response.follow(details_link, self.parse_details, meta={
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
            })

        # Optionally, handle pagination via next page links if available
        # next_page = response.css('li.pagination-next a::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

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
            'location_description': location_description
        }
