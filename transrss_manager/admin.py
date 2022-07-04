from django.contrib import admin
from .models import FeedSource, FeedMatcher, Torrent

# Register your models here.
class FeedSourceAdmin(admin.ModelAdmin):
    list_display = ('title',)

class FeedMatcherAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'download_dir', 'source')

class TorrentAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')

admin.site.register(FeedSource, FeedSourceAdmin)
admin.site.register(FeedMatcher, FeedMatcherAdmin)
admin.site.register(Torrent, TorrentAdmin)
