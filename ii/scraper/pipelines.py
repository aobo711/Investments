# -*- coding: utf-8 -*-
from django.db.utils import IntegrityError
from scrapy import log
import logging,json,time,scrapy
from scrapy.exceptions import DropItem
from dynamic_scraper.models import SchedulerRuntime
from ii.models import Company, Industy, IC, Investment, Tag
from bs4 import BeautifulSoup as Soup
from soupselect import select
import ast

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  

def item_to_model(item):
        model_class = getattr(item, 'django_model')
        if not model_class:
            raise TypeError("Item is not a `DjangoItem` or is misconfigured")

        return item.instance


def get_or_create(model):
    model_class = type(model)
    created = False

    # Normally, we would use `get_or_create`. However, `get_or_create` would
    # match all properties of an object (i.e. create a new object
    # anytime it changed) rather than update an existing object.
    #
    # Instead, we do the two steps separately
    try:
        # We have no unique identifier at the moment; use the name for now.
        obj = model_class.objects.get(url=model.url)
        obj.updated_at = time.strftime("%c")
    except model_class.DoesNotExist:
        created = True
        obj = model  # DjangoItem created a model for us.

    return (obj, created)


class DjangoWriterPipeline(object):

    def process_item(self, item, spider):
        if spider.conf['DO_ACTION']: #Necessary since DDS v.0.9+
            try:

                item['source'] = spider.ref_object

                checker_rt = SchedulerRuntime(runtime_type='C')
                checker_rt.save()
                item['checker_runtime'] = checker_rt
                if 'started_at' in item:
                    item['started_at'] = item['started_at'] + '-01-01'
                item['industy'], created = Industy.objects.get_or_create(name=item['industy'])

                try:
                    item_model = item_to_model(item)
                except TypeError:
                    return item

                model, created = get_or_create(item_model)

                model.tags_raw = ''
                model.save();
            
                tags = ast.literal_eval(item['tags_raw'].encode('utf-8'))
                tag_objs = []
                for tag in tags:
                    tag_name = tag['tag_name']
                    tag_obj, tag_created = Tag.objects.get_or_create(name=tag_name)
                    if tag:
                        tag_obj.save()
                        tag_objs.append(tag_obj)

                if tag_objs:
                    model.tags.add(*tag_objs)

                model.tags_raw = ','.join(t.name for t in tag_objs)


                # 保存融资信息
                invest_firm = ''
                investments = ast.literal_eval(item['investment_raw'].encode('utf-8'))                
                for i in investments:

                    invest_date = '-'.join(str(i) for i in [i['invse_year'], i['invse_month'],i['invse_month']])
                    invest_amount = str(i['invse_detail_money']) + i['invse_currency']['invse_currency_name']

                    if i['invse_rel_invst_name']:
                        invest_firm = i['invse_rel_invst_name']
                    else:
                        invest_firm = ' '.join([org['invst_name'] for org in i['invse_orags_list']])



                    invest_round = i['invse_round']['invse_round_name']
                    investment, investment_created = Investment.objects.get_or_create(invest_date = invest_date,
                        invest_firm = invest_firm,
                        invest_round = invest_round,
                        invest_amount = invest_amount,
                        invest_to = model)

                    investment.save()

                model.investment_raw = invest_firm
                model.save()

                # backup
                # save tags_soup
                # tags_soup = Soup(item['tags_raw'], 'lxml')
                # tags = []
                # for tag_soup in select(tags_soup, 'a span'):
                #     tag = tag_soup.string
                #     tag_obj, tag_created = Tag.objects.get_or_create(name=tag)
                #     if tag:
                #         tag_obj.save()
                #         tags.append(tag_obj)

                # if tags:
                #     model.tags.add(*tags)

                # model.tags_raw = ','.join(t.name for t in tags)


                #save investment
                # soup = Soup(item['investment_raw'], 'lxml')
                # invest_firm = ''
                # for investment_soup in soup.find_all('tr'):
                #     invest_date = select(investment_soup, 'span.date')[0].string.replace('.', '-')
                #     invest_amount = select(investment_soup, 'span.finades a')[0].string

                #     tds = select(investment_soup, 'td')
                #     if tds[3]:
                #         invest_firm = ','.join(i.string for i in tds[3].find_all('a'))

                #     invest_round = select(investment_soup, 'span.round a')[0].string
                #     investment, investment_created = Investment.objects.get_or_create(invest_date = invest_date,
                #         invest_firm = invest_firm,
                #         invest_round = invest_round,
                #         invest_amount = invest_amount,
                #         invest_to = model)

                #     investment.save()

                # model.investment_raw = invest_firm
                

                if created:
                    spider.log('==' + model.name + '== created.', log.INFO)
                    
                else:
                    spider.log('==' + model.name + '== updated.', log.INFO)

                spider.action_successful = True
                
            except IntegrityError, e:
                spider.log(str(e), logging.ERROR)
                spider.log(str(item._errors), logging.ERROR)
                raise DropItem("Missing attribute.")

        else:
            if not item.is_valid():
                spider.log(str(item._errors), logging.ERROR)
                raise DropItem("Missing attribute.")

        return item
