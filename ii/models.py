from django.db import models
from django.utils import timezone
from dynamic_scraper.models import Scraper, SchedulerRuntime
from scrapy_djangoitem import DjangoItem



class Source(models.Model):
    name = models.CharField(max_length=200)

    description = models.TextField(null=True)

    url = models.URLField()

    scraper = models.ForeignKey(Scraper, blank=True, null=True, on_delete=models.SET_NULL)

    scraper_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name



class IC(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name


class Industy(models.Model):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name




class Tag(models.Model):
    
    name = models.CharField(max_length=200)

    description = models.TextField(null=True)

    def __unicode__(self):
        return self.name




class Company(models.Model):

    name = models.CharField(max_length=200)

    icon = models.ImageField(blank=True,null=True,max_length=200)

    url = models.CharField(max_length=200)
    
    address = models.CharField(max_length=200, null=True)
    
    homepage = models.CharField(max_length=200, null=True)

    region = models.CharField(max_length=200, null=True)

    started_at = models.DateTimeField(blank=True,null=True)

    is_running = models.NullBooleanField()

    email = models.CharField(max_length=200, null=True)

    phone = models.CharField(max_length=200, null=True)

    fullname = models.CharField(max_length=200,null=True)

    summary = models.TextField(null=True)

    industy = models.ForeignKey(Industy, null=True, blank=True)

    source = models.ForeignKey(Source)

    checker_runtime = models.ForeignKey(SchedulerRuntime, blank=True, null=True, on_delete=models.SET_NULL)

    updated_at = models.DateTimeField()

    investment_raw = models.TextField(null=True)

    tags_raw = models.CharField(max_length=200)

    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super(Company, self).save(*args, **kwargs)

class Investment(models.Model):
	invest_round = models.CharField(max_length=200)

	invest_amount = models.CharField(max_length=200)

	invest_firm = models.CharField(max_length=200)

	invest_date = models.DateTimeField()

	invest_to = models.ForeignKey(Company)

	def __unicode__(self):
		return self.name

class CompanyItem(DjangoItem):
    django_model = Company


class MonthlyData(models.Model):
    yearmonth = models.CharField(max_length=200)

    tag = models.CharField(max_length=200)

    investment = models.ForeignKey(Investment)


class RankingData(models.Model):
    yearmonth = models.CharField(max_length=200)

    tag = models.CharField(max_length=200)

    score = models.FloatField()

class TrendingData(models.Model):
    yearmonth = models.CharField(max_length=200)

    tag = models.CharField(max_length=200)
    
    investment_num = models.CharField(max_length=200)

    increasment_rate = models.FloatField()