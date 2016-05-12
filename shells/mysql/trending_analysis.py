# -*- coding: utf-8 -*-
#!/usr/bin/python

# 分析每个行业月同比增长率，用于分析新兴行业

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
	'investment_num' : 0,
	'increasment_rate' : 0.5
}

for row in cur.fetchall():
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
		new_date = datetime(int(yearmonth[:4]), int(yearmonth[-2:]), 1)
		last_date = datetime(int(current['yearmonth'][:4]), int(current['yearmonth'][-2:]), 1)
		months = diff_month(new_date, last_date)

		adjustment = 5

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
	cur.execute(insert_if_not_exists)

db.commit()
db.close()