from dynamic_scraper.spiders.django_spider import DjangoSpider
from ii.models import Source, Company, CompanyItem
import django
from ii import util
django.setup()

class IISpider(DjangoSpider):
    
    name = 'ii_spider'

    def __init__(self, *args, **kwargs):

    	util.fetch_token()

        self._set_ref_object(Source, **kwargs)
        self.scraper = self.ref_object.scraper
        self.scrape_url = self.ref_object.url
        self.scheduler_runtime = self.ref_object.scraper_runtime
        self.scraped_obj_class = Company
        self.scraped_obj_item_class = CompanyItem
        super(IISpider, self).__init__(self, *args, **kwargs)