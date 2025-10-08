import scrapy

class FuelStationItem(scrapy.Item):
    # Basic information
    name = scrapy.Field()
    place_id = scrapy.Field()
    
    # Rating and reviews
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    
    # Location
    address = scrapy.Field()
    
    # Category
    category = scrapy.Field()
    
    # Links
    link = scrapy.Field()
    
    # Metadata
    scraped_at = scrapy.Field()
    source = scrapy.Field()
