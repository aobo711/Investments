# -*- coding: utf-8 -*-
#!/usr/bin/python

# 分析每个行业月投资热度，用于分析热门行业

import sqlite3
import math

import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month

conn = sqlite3.connect('../ii.db')


# ranking 的得分是按月来算的，所以只需要一个月跑一次脚本
# 先拿一下上个月的月份
today = datetime.date.today()
first = today.replace(day=1)

cursor = conn.execute('select yearmonth, tag, score from ii_rankingdata where yearmonth<"%s"' % first.strftime("%Y%m"))

existed_data = {}

for row in cursor:
	yearmonth = str(row[0])
	tag = str(row[1])
	score = row[2]
	existed_data[ tag + yearmonth ] = score

cursor = conn.execute('select tag,yearmonth,count(investment_id) from ii_monthlydata where yearmonth<"%s" group by tag,yearmonth order by tag,yearmonth' % first.strftime("%Y%m"))

current = {
	'tag' : '',
	'yearmonth' : '',
	'score' : 0
}

for row in cursor:
	tag = row[0]
	yearmonth = row[1]
	investment_num = row[2]

	if current['tag'] != tag:
		current = {
			'tag' : tag,
			'yearmonth' : yearmonth,
			'score' : investment_num
		}
	else:

		new_date = datetime.datetime(int(yearmonth[:4]), int(yearmonth[-2:]), 1)
		last_date = datetime.datetime(int(current['yearmonth'][:4]), int(current['yearmonth'][-2:]), 1)
		months = diff_month(new_date, last_date)

		# 新的得分 = 本月融资数量 + 上期得分 * exp((-冷却系数)*上期与本期的间隔月份数)

		dict_key = str(tag) + str(yearmonth)
		if dict_key in existed_data:
			continue
		else:
			new_score = investment_num + current['score'] * math.exp(-0.1 * months)

		current = {
			'tag' : tag,
			'yearmonth' : yearmonth,
			'score' : new_score
		}

	
	insert_if_not_exists = "INSERT INTO ii_rankingdata (`yearmonth`, `tag`, `score`) SELECT * FROM (SELECT '%s','%s', %f) AS tmp \
		WHERE NOT EXISTS (SELECT * FROM ii_rankingdata WHERE \
		`yearmonth`='%s' and `tag`='%s') LIMIT 1" % (current['yearmonth'], current['tag'], current['score'], current['yearmonth'], current['tag'])
	conn.execute(insert_if_not_exists)

conn.commit()
conn.close()