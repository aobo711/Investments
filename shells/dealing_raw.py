# -*- coding: utf-8 -*-
#!/usr/bin/python

# 把投资原始数据按 yearmonth 分拆，并插入到 ii_monthlydata 表中
# 用于分析每个行业的月总投资笔数

import sqlite3

conn = sqlite3.connect('/home/hzzhengjintian/works/ii.db')

cursor = conn.execute('select EXTRACT(YEAR_MONTH FROM i.invest_date),c_t.tname, \
	i.id from (select c.id as cid, c.name as cname, t.name as tname from ii_company as c,ii_company_tags as ct, ii_tag as t \
	where c.id=ct.company_id and ct.tag_id = t.id and c.updated_at >= "20160301") as c_t,ii_investment as i \
	where c_t.cid=i.invest_to_id')

for row in cursor:
	yearmonth = row[0]
	tag = row[1]
	investment_id = row[2]

	insert_if_not_exists = "INSERT INTO ii_monthlydata (`yearmonth`, `tag`, `investment_id`) SELECT * FROM (SELECT '%s','%s', %d) AS tmp \
		WHERE NOT EXISTS (SELECT * FROM ii_monthlydata WHERE \
		`yearmonth`='%s' and `tag`='%s' and `investment_id`=%d) LIMIT 1" % (yearmonth,tag,investment_id, yearmonth,tag,investment_id)
	conn.execute(insert_if_not_exists)

conn.commit()
conn.close()