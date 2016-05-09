import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ii.settings")

BOT_NAME = 'Baidu Mobile'

SPIDER_MODULES = ['dynamic_scraper.spiders', 'ii.scraper',]
USER_AGENT = '%s/%s' % (BOT_NAME, '1.0')


CUSTOM_PROCESSORS = 'tvshow_scraper.scraper.processors'

#Scrapy 0.20+
ITEM_PIPELINES = {
    'dynamic_scraper.pipelines.ValidationPipeline': 400,
    'ii.scraper.pipelines.DjangoWriterPipeline': 800,
}

#Scrapy up to 0.18
ITEM_PIPELINES = [
    'dynamic_scraper.pipelines.DjangoImagesPipeline',
    'dynamic_scraper.pipelines.ValidationPipeline',
    'ii.scraper.pipelines.DjangoWriterPipeline',
]


IMAGES_STORE = os.path.join(PROJECT_ROOT, '../thumbnails')

IMAGES_THUMBS = {
    'small': (180, 180),
}

DSCRAPER_IMAGES_STORE_FORMAT = 'ALL' 