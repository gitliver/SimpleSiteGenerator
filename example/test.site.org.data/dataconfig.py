#-------------------------------------------------------------------------------
#
#    dataconfig.py
#
#    This file has the constants and defaults for the data directory
#
#-------------------------------------------------------------------------------

# Note:
# PEP 8 Style Guide for Python Code | https://www.python.org/dev/peps/pep-0008/
# Constants are usually defined on a module level and
# written in all capital letters with underscores separating words.
# Examples include
# MAX_OVERFLOW and TOTAL.

### Constants and Defaults

# Site title (e.g., French Wines)
SITETITLE = 'test.site.org'

# Domain name (e.g., frenchwines.com)
DOMAIN = 'test.site.org'

# Site keywords
SITEWORDS = 'food,wine,travel'

# Site author
SITEAUTHOR = 'myname'

# Public contact email on website
EMAIL = 'myemail@email.com'

# homepage url key
# This determines the homepage at the root url path
# It can be a special page defined in l_SPECIAL_PAGES
HOMEPAGE = 'selected'

# This determines is the url that will be linked by your webpage title text
# (usually in the upper left corner).
# Leave this empty if you want this to be your homepage (root url).
# If special cases, however, you might want to set this — 
# the main example being if you have a cover page
# and you do not want to revisit this cover page
# when you click on the title.
# In that case (e.g., HOMEPAGE = 'cover', HOMELINK = 'selected')
# HOMELINK serves as your de facto home page.
HOMELINK = ''
#HOMELINK = 'selected'

# If True, the homepage page will have two paths on your website:
# one at the root url path, and one at its normal url attribute
# If, e.g., HOMEPAGE == 'cover', you will want to turn this off.
# If, on the other hand, you want your page on the homepage and in a section category, turn on
DUPLICATEHOME = False

# If True, show news box on homepage
SHOWNEWS = False

### Sidebar (Navbar)

# Sidebar url keys
# This determines what will be in the sidebar and its ordering
SIDEBAR = [
    'latest',
    'france',
    'food',
    'wine',
    'feed',
    'blog',
    'about'
]

## CSS

# CSS Files for every page of your website
# Paths of the CSS files in your output directory
BASE_CSS = [
    'static/css/theme_minimalist.min.css'
]

# Various global CSS parameters
# 'socialiconsize' is the size in pixels of social media icons. E.g., if 24 then size is 24x24
# 'thumbnail_width' is the thumbnail width for imgs on the image section pages
# 'body_extra' is any extra css class to be applied to the <body> tag (think: font)
# 'main_extra' is any extra css class to be applied to the tag with class 'ssg-main' (think: color)
# 'nav_extra' is any extra css class to be applied to the tag with class 'ssg-nav' (think: font)
d_CSS = {
    'socialiconsize': 16,
    'thumbnail_width': 300,
    'body_extra': 'ssg-text2',
    'main_extra': '',
    'nav_extra': ''
}

# Addtional CSS files associated with particular page types
d_TYPE2CSS = {
    'article': [],
    'visual': [],
    'cover': []
}

# This dict maps url key to Addtional CSS files.
# It's for the more granular case in which
# you want to have some CSS for a single url key
d_URL2CSS = {}

## JS

# JS Files for every page of your website
# Paths of the JS files in your output directory
BASE_JS = [
    'static/js/theme_default.min.js'
]

# Addtional JS files associated with particular page types
d_TYPE2JS = {
    'article': [],
    'visual': [],
    'cover': []
}

# This dict maps url key to Addtional JS files.
# It's for the more granular case in which
# you want to have some JS for a single url key
d_URL2JS = {}

## Favicon

# Favicon path in your output directory
FAVICON = ''

# Path of the avatar img file in your output directory
AVATAR = ''

## Templates

# This dict maps page type to template
d_TYPE2TEMPLATE = {
    'article': 'theme_minimalist.post.article.html',
    'img': 'theme_minimalist.post.visual.whitesmoke.html',
    'video': 'theme_minimalist.post.visual.whitesmoke.html',
    'sectionarticle': 'theme_minimalist.section.article.html',
    'sectionvisual': 'theme_minimalist.section.visual.html',
    'error': 'theme_minimalist.404.html'
}

## Socials

# Links for social media
d_SOCIALMEDIA = {
    'instagram': 'https://www.instagram.com/username',
    'youtube': 'https://www.youtube.com/@username',
    'twitter': 'https://x.com/username',
    'facebook': 'https://www.facebook.com/username',
    # 'linkedin': 'https://www.linkedin.com/company/username',
    # 'tiktok': 'https://www.tiktok.com/@username',
    # 'bluesky': 'https://bsky.app/profile/username',
    # 'reddit': 'https://www.reddit.com/r/username/',
    # 'github': 'https://github.com/username',
    # 'mail': EMAIL
}

## Special Pages

# This json-y list turns various special pages on and off

# Number of posts to show in the feed section (if present)
NUMPOSTSFEED = 5

# Create a Latest Feed set of pages (containing NUMPOSTSFEED pages)
LATESTFEED = False

l_SPECIAL_PAGES = [
    {
        "name": "Cover",
        "showname": 0,
        "url": "cover",
        "publish": 0,
        "specialpage": 1,
        "blurb": "",
        "showblurb": 0,
        "type": "article",
        "template": "theme_minimalist.cover.html",
        "description": "A coverpage which doesn't inherit from base.html",
        "notes": ""
    },
    {
        "name": "Latest",
        "showname": 0,
        "url": "latest",
        "publish": 1,
        "specialpage": 1,
        "blurb": "",
        "showblurb": 0,
        "type": "img",
        "template": "theme_minimalist.post.visual.html",
        "description": "The single most recent post",
        "notes": "type is subject to change, as this could be either img or video"
    },
    {
        "name": "Selected",
        "showname": 0,
        "url": "selected",
        "publish": 1,
        "subtitle": "",
        "showsubtitle": 0,
        "specialpage": 1,
        "blurb": "",
        "showblurb": 0,
        "type": "sectionvisual",
        "template": "theme_minimalist.section.visual.html",
        "description": "A smattering of selected posts",
        "notes": ""
    },
    {
        "name": "Feed",
        "showname": 0,
        "url": "feed",
        "publish": 1,
        "specialpage": 1,
        "blurb": "The latest 5 posts",
        "showblurb": 0,
        "type": "specialpage",
        "template": "theme_minimalist.feed.visual.html",
        "description": "The Feed is a page with a limited number of recent posts",
        "notes": ""
    }
]