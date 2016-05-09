from django.contrib import admin
from django.conf import settings
from ii.models import Company, Source, Investment, Tag

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', '_icon','email', 'industy', 'updated_at')
    list_display_links = ('name',)
    search_fields = ['name']

    def _icon(self, instance):
        return '<img src="%s" height="100" />' % (settings.MEDIA_URL + instance.icon.name)

    _icon.allow_tags = True

class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'invest_date', 'invest_amount' , 'invest_round', 'invest_to', 'invest_firm')
    search_fields = ['invest_to']
    list_display_links = ('id',)
    
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'scraper')
    list_display_links = ('name',)
    

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(Tag, TagAdmin)