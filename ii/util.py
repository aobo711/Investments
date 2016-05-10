# -*- coding: utf-8 -*-
import requests
import json
from django.db import connection,transaction

# 获取 itjuzi token
# curl -H "Host: cobra.itjuzi.com" -H "Content-Type: application/x-www-form-urlencoded; charset=utf-8" -H "Accept: */*" 
# -H "User-Agent: v4_itjuzi/2.7.0 (iPhone; iOS 9.3.1; Scale/2.00)" 
# -H "Accept-Language: zh-Hans-CN;q=1" 
# --data-binary "client_id=2&client_secret=7fed6221f1ecad2721e280319bf1cca6&grant_type=client_credentials" --compressed 
# http://cobra.itjuzi.com/oauth/access_token

def fetch_token():
	url = 'http://cobra.itjuzi.com/oauth/access_token'
	data = {
		'client_id': '2',
		'client_secret' : '7fed6221f1ecad2721e280319bf1cca6',
		'grant_type' : 'client_credentials'
	}
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
		'Accept' : '*/*',
		'User-Agent' : 'v4_itjuzi/2.7.0 (iPhone; iOS 9.3.1; Scale/2.00)',
		'Accept-Language' : 'zh-Hans-CN;q=1'
	}

	r = requests.post(url, data=data, headers=headers)
	result = r.json()
	token = result['access_token']

	# save token to DB
	cursor = connection.cursor()            

	main_page_header = '''{ \"User-Agent\":\"v4_itjuzi/2.7.0 (iPhone; iOS 9.3.1; Scale/2.00)\",
		\"Authorization\":\"Bearer %s",
		\"Accept\":\"*/*\",
		\"userid\":\"0\",
		\"Host\":\"cobra.itjuzi.com\",
		\"Accept-Language\":\"zh-Hans-CN;q=1\"
	}''' % token
	detail_page_header = '''{
    	\"User-Agent\":\"v4_itjuzi/2.7.0 (iPhone; iOS 9.3.1; Scale/2.00)\",
    	\"Authorization\":\"Bearer %s\" 
	}''' % token

	cursor.execute('update dynamic_scraper_requestpagetype set headers =\'%s\' where id=10' % main_page_header)
	cursor.execute('update dynamic_scraper_requestpagetype set headers =\'%s\' where id=11' % detail_page_header)

	transaction.commit()