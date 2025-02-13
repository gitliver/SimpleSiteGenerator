#-------------------------------------------------------------------------------
#
#    reportconfig.py
#
#    This file has the constants and defaults for SimpleSiteGenerator
#
#-------------------------------------------------------------------------------

### Constants etc.

# Version
VERSION = '4.8.0'

# Allowed types of pages:
# 'sectionvisual' is a page with links to a particular subset of visual posts
# 'sectionarticle' is a page with links to a particular subset of article posts
# 'img' is a visual post page with an image
# 'video' is a visual post page with a video
# 'article' is an article post page
# 'error' is for 404 errors
# 'specialpage' is anything other than the above
ALLOWED_TYPES = [
    'sectionvisual',
    'sectionarticle',
    'img',
    'video',
    'article',
    'specialpage',
    'error'
]

# These special urls and words are reserved and may not be used as ordinary post url keys
RESERVED = [
    'static',
    'cover',
    'latest',
    'selected',
    'feed',
    'post'
]

# Allowed (recognized) social media types
# (For now, these are the only ones with SVG icons (mostly courtesy of National Geographic!))
ALLOWED_SOCIAL = [
    'instagram',
    'youtube',
    'twitter',
    'facebook',
    'linkedin',
    'tiktok',
    'bluesky',
    'reddit',
    'github'
]

# Required fields for post objects
REQUIRED_POST_FIELDS = [
    "name",
    "showname",
    "shownamesection",
    "subtitle",
    "showsubtitle",
    "type",
    "border",
    "files",
    "thumbnail",
    "url",
    "urlexternal",
    "publishedexternal",
    "publish",
    "specialpage",
    "selected",
    "author",
    "showauthor",
    "category",
    "series",
    "keywords",
    "date",
    "showdate",
    "blurb",
    "showblurb",
    "paywall",
    "ispreview",
    "description",
    "notes"
]

REQUIRED_SECTION_FIELDS = [
    "name",
    "showname",
    "subtitle",
    "showsubtitle",
    "category",
    "url",
    "publish",
    "specialpage",
    "type",
    "blurb",
    "showblurb",
    "description",
    "notes"
]