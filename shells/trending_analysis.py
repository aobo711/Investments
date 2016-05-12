# -*- coding: utf-8 -*-
#!/usr/bin/python

# 分析每个行业月同比增长率，用于分析新兴行业

import sqlite3
import math
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month


# trending 的得分也是按月来算的，所以只需要一个月跑一次脚本
# 先拿一下上个月的月份
today = datetime.date.today()
first = today.replace(day=1)

conn = sqlite3.connect('../ii.db')


cursor = conn.execute('select yearmonth, tag, investment_num,increasment_rate from ii_trendingdata where yearmonth<"%s"' % first.strftime("%Y%m"))

existed_data = {}

for row in cursor:
    yearmonth = str(row[0])
    tag = str(row[1])
    increasment_rate = row[3]
    existed_data[ tag + yearmonth ] = increasment_rate


cursor = conn.execute('select tag,yearmonth,count(investment_id) from ii_monthlydata where yearmonth<"%s" group by tag,yearmonth order by tag,yearmonth' % first.strftime("%Y%m"))

current = {
    'tag' : '',
    'yearmonth' : '',
    'investment_num' : 0,
    'increasment_rate' : 0.5
}

for row in cursor:
    tag = row[0]
    yearmonth = row[1]
    investment_num = row[2]
    if current['tag'] != tag:
        current = {
            'tag' : tag,
            'yearmonth' : yearmonth,
            'investment_num' : investment_num,
            'increasment_rate' : 0.5
        }
    else:
        new_date = datetime.datetime(int(yearmonth[:4]), int(yearmonth[-2:]), 1)
        last_date = datetime.datetime(int(current['yearmonth'][:4]), int(current['yearmonth'][-2:]), 1)
        months = diff_month(new_date, last_date)

        adjustment = 5

        dict_key = str(tag) + str(yearmonth)
        if dict_key in existed_data:
            continue
        else:
            new_score = (investment_num - current['investment_num']) / float(current['investment_num'] + adjustment) / float(months)

        current = {
            'tag' : tag,
            'yearmonth' : yearmonth,
            'investment_num' : investment_num,
            'increasment_rate' : new_score
        }

    
    insert_if_not_exists = "INSERT INTO ii_trendingdata (`yearmonth`, `tag`, `investment_num`, `increasment_rate`) SELECT * FROM (SELECT '%s','%s',%d, %f) AS tmp \
        WHERE NOT EXISTS (SELECT * FROM ii_trendingdata WHERE \
        `yearmonth`='%s' and `tag`='%s') LIMIT 1" % (current['yearmonth'], current['tag'], current['investment_num'], current['increasment_rate'], current['yearmonth'], current['tag'])
    conn.execute(insert_if_not_exists)

conn.commit()
conn.close()