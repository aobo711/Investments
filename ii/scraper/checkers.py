from dynamic_scraper.spiders.django_checker import DjangoChecker
from ii.models import Company


class IIChecker(DjangoChecker):

    name = 'ii_checker'

    def __init__(self, *args, **kwargs):
        self._set_ref_object(Company, **kwargs)
        self.scraper = self.ref_object.source.scraper
        #self.scrape_url = self.ref_object.url (Not used any more in DDS v.0.8.3+)
        self.scheduler_runtime = self.ref_object.checker_runtime
        super(IIChecker, self).__init__(self, *args, **kwargs)