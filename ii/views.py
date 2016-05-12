# -*- coding: utf-8 -*-
from django.http import HttpResponse,JsonResponse,HttpResponseNotFound,HttpResponseBadRequest
from django.template.loader import render_to_string
from datetime import timedelta
import datetime
import json
from ii.models import Company, Investment, Tag, MonthlyData, RankingData, TrendingData
from django.template import loader, Context
from django.db.models import Count,Avg
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  


def investment_date_range(tag_name):
    base = datetime.date.today()
    from_date = datetime.date(base.year - 3, base.month, base.day)

    from_year = from_date.year
    from_month = from_date.month
    date_list = []

    for x in range(0,37):
        date_list.append(datetime.date(from_year, from_month, 1))

        from_month += 1
        if from_month >=13:
            from_year += 1
            from_month = 1
    
    monthlydata = MonthlyData.objects\
        .filter(investment__invest_date__gte=from_date)

    if tag_name:
        monthlydata = monthlydata.filter(tag=tag_name)

    monthlydata =  monthlydata.values('yearmonth')\
        .annotate(count=Count('id'))\
        .order_by('yearmonth')

    monthlydata_list = []
    date_label = []

    for d in date_list:
        d = d.strftime("%Y%m")
        date_in_range = [x for x in monthlydata if str(x['yearmonth']) == d]

        date_label.append(d[2:])
        if date_in_range:
            monthlydata_list.append(date_in_range[0]['count'])
        else:
            monthlydata_list.append(0)

    return (date_label,monthlydata_list)


def diff_tag(request):
    tags = request.GET.get('tags', '')

    tags = tags.split(',')
    labels = ''
    data = []

    for tag in tags:
        date_label, monthlydata_list = investment_date_range(tag)
        temp = []
        for m in monthlydata_list:
            temp.append({
                'meta' : tag,
                'value' : m
            })
        data.append(temp)

    response_data = {
        'labels' : date_label,
        'data' : data
    }    
    return HttpResponse(json.dumps(response_data), content_type="application/json")



def home(request):

    date_label, monthlydata_list = investment_date_range(None)

    date_label_str = ','.join(date_label)
    monthlydata_str = ','.join(str(v) for v in monthlydata_list)

    tags = Tag.objects\
    	.annotate(num_companies=Count('company'))\
    	.filter(num_companies__gt=30)\
    	.order_by('-num_companies')

    # 看热门行业只需要看上个月的最终得分就可以，所以先算一下上个月的月份
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    ranking_data = RankingData.objects.filter(yearmonth=lastMonth.strftime("%Y%m"))\
        .order_by('-score')[:30]

    half_year_ago = datetime.datetime.now() - datetime.timedelta(days=180)

    trending_data = TrendingData.objects\
        .values('tag')\
        .annotate(avg=Avg('increasment_rate'), count=Count('yearmonth'))\
        .filter(count__gt=3, yearmonth__gt=half_year_ago.strftime('%Y%m'))\
        .order_by('-avg')[:30]

    print trending_data.query

    t = loader.get_template('home.html')
    c = Context({ 
    	'tags' : tags,
        'labels' : date_label_str,
        'data' : monthlydata_str,
        'ranking_data' : ranking_data,
        'trending_data' : trending_data
    	})

    rendered = t.render(c)

    return HttpResponse(rendered, content_type='text/html;charset=utf-8')



def tag(request, tag_name):
    tags = Tag.objects.filter(name=tag_name)

    investments = Investment.objects\
        .filter(invest_to__tags__in=tags)\
        .values('invest_to__name','invest_to__id','invest_date','invest_to__investment_raw','invest_to__homepage')\
        .annotate(count=Count('id'))\
        .order_by('-invest_date')

    date_label, monthlydata_list = investment_date_range(tag_name)

    date_label_str = ','.join(date_label)
    monthlydata_str = ','.join(str(v) for v in monthlydata_list)

    t = loader.get_template('tag.html')
    c = Context({ 
        'tag_name' : tag_name,
        'labels' : date_label_str,
        'data' : monthlydata_str,
    	'investments': investments[:30],
    	})

    rendered = t.render(c)

    return HttpResponse(rendered, content_type='text/html;charset=utf-8')

def companies(request):
    where = 'YEAR(invest_date) >= "2015"'

    investments = Investment.objects\
        .extra(where=[where])\
        .values('invest_to__region', 'invest_to__name',
            'invest_to__tags_raw', 'invest_to__email', 'invest_date', 
            'invest_to__homepage', 'invest_to__investment_raw')\
        .exclude(invest_to__email__exact='暂未收录')\
        .order_by('-invest_date')\
        .distinct()
        

    t = loader.get_template('companies.html')
    c = Context({ 
    	'companies': investments,
    	})

    rendered = t.render(c)

    return HttpResponse(rendered, content_type='text/html;charset=utf-8')
