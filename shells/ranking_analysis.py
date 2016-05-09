# -*- coding: utf-8 -*-
#!/usr/bin/python

# 分析每个行业月投资热度，用于分析热门行业

import MySQLdb
import math

from datetime import datetime

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month

db = MySQLdb.connect(host='localhost',    
                     user='root',         
                     passwd='',  
                     db='ii')

cur = db.cursor()
cur.execute('select tag,yearmonth,count(investment_id) from ii_monthlydata where yearmonth>"20160301" group by tag,yearmonth order by tag,yearmonth')

current = {
	'tag' : '',
	'yearmonth' : '',
	'score' : 0
}

for row in cur.fetchall():
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
		new_date = datetime(int(yearmonth[:4]), int(yearmonth[-2:]), 1)
		last_date = datetime(int(current['yearmonth'][:4]), int(current['yearmonth'][-2:]), 1)
		months = diff_month(new_date, last_date)

		# 新的得分 = 本月融资数量 + 上期得分 * exp((-冷却系数)*上期与本期的间隔月份数)
		new_score = investment_num + current['score'] * math.exp(-0.1 * months)
		current = {
			'tag' : tag,
			'yearmonth' : yearmonth,
			'score' : new_score
		}

	
	insert_if_not_exists = "INSERT INTO ii_rankingdata (`yearmonth`, `tag`, `score`) SELECT * FROM (SELECT '%s','%s', %f) AS tmp \
		WHERE NOT EXISTS (SELECT * FROM ii_rankingdata WHERE \
		`yearmonth`='%s' and `tag`='%s') LIMIT 1" % (current['yearmonth'], current['tag'], current['score'], current['yearmonth'], current['tag'])
	cur.execute(insert_if_not_exists)

db.commit()
db.close()