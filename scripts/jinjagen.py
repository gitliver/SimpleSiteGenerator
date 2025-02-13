#-------------------------------------------------------------------------------
#
#    jinjagen.py
#
#    Generate a simple static website. See the README for details
#
#-------------------------------------------------------------------------------

import sys
import os
import argparse
import json
import jinja2
import datetime
import pandas as pd
import colorme as color

# Constants from config file

from siteconfig import VERSION
from siteconfig import RESERVED
from siteconfig import ALLOWED_TYPES
from siteconfig import ALLOWED_SOCIAL
from siteconfig import REQUIRED_POST_FIELDS
from siteconfig import REQUIRED_SECTION_FIELDS

#-------------------------------------------------------------------------------
#
#    Global variables
#
#-------------------------------------------------------------------------------

# Using global variable not the best practice, but convenient

# A "json"-like list (a list of dicts) of "log" information
l_log_global = []

# url key to debug
DEBUG = 'XXX'

#-------------------------------------------------------------------------------
#
#    Functions
#
#-------------------------------------------------------------------------------

def getarg():
    """
    Set up arguments
    """

    parser = argparse.ArgumentParser(prog='jinjagen',
                                     usage='%(prog)s [options]',
                                     add_help=False,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-h', '--help',
                        action = 'help',
                        help='show this help message and exit\n\n')
    parser.add_argument('-t', '--templates',
                        type=str,
                        required=True,
                        help='Path to JinJa templates\n\n')
    parser.add_argument('-d', '--data',
                        type=str,
                        required=True,
                        help='Path to the data folder\n\n')
    parser.add_argument('-o', '--outputdir',
                        type=str,
                        help='output directory\n\n'),
    parser.add_argument('--logfile',
                        type=str,
                        help='Path to the log folder (omit to suppress logging)\n\n')
    parser.add_argument('--nostrict',
                        action="store_true",
                        default=False,
                        help='Turn off strict mode\n\n')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        default=False,
                        help='Turn on verbose mode\n\n')

    args =  parser.parse_args()

    return args

def getenv(templatepath):
    """
    Get jinja2 env

    :param templatepath: (str) path to the directory containing templates
    :returns: a jinja2 Environment object
    :rtype: jinja2.environment.Environment
    """

    templateLoader = jinja2.FileSystemLoader(templatepath)
    env = jinja2.Environment(
        loader = templateLoader,
        autoescape = jinja2.select_autoescape(['html', 'xml'])
    )

    return env

def removeemptylines(x):
    """
    Remove empty lines

    :param x: (str) a string, potentially with empty lines
    :returns: a string with no empty lines
    :rtype: str
    """

    return '\n'.join([i for i in x.split('\n') if i.strip()])

def checkpath(mydirectory, l_files, verbose=False):
    """
    Check file existence

    :param mydirectory: (str) Path to the directory
    :param l_files: (list) a list of files
    :param verbose: (bool) If True, print stuff
    """

    for myfile in l_files:
        if verbose:
            print(f'Checking file existence: {mydirectory}/{myfile}')
        assert os.path.isfile(f'{mydirectory}/{myfile}'), f'file not found: {mydirectory}/{myfile}'

def getnews(datadir):
    """
    Get the news as a string of HTML.
    This is for the little blurb on the sidebar that proclaims, well, news!

    :param datadir: (str) path to the data directory
    :returns: (str) HTML content of news
    :rtype: str
    """

    # News (as html str)
    newshtml = ''
    try:
        with open(datadir + '/published/news/content.html', 'r') as g:
            for contentline in g:
                newshtml += contentline
    except:
        pass

    return newshtml

def createsidebar(d_all, l_urls, verbose=False):
    """
    Create the sidebar object

    :param d_all (dict):
        a dict whose keys are urls and whose values are page objects
    :param l_urls: (list) A list of urls associated with the sidebar
    :param verbose: (bool) If True, print stuff
    :returns: (list of dicts) List of sidebar objs
    :rtype: list
    """

    l = []

    for i in l_urls:
        d = {
            'urlpath': d_all[i]['urlpath'],
            'name': d_all[i]['name']
        }

        l.append(d)

    return l

def getcommonprops(
        datadir,
        pagetitle,
        pagedomain,
        version,
        favicon,
        avatar,
        keywords,
        author,
        email,
        l_css,
        l_js,
        d_socialmedia,
        l_sidebar,
        d_css,
        shownews,
        homelink='',
        verbose=False
    ):
    """
    Return the common props dict that every template requires
    It has the CSS, the sidebar items, etc.

    :param datadir: (str) Path to the data directory
    :param pagetitle: (str) Title of page (e.g., French Wines)
    :param pagedomain: (str) domain name of page (e.g., frenchwines.com)
    :param version: (str) software version
    :param favicon: (str) favicon path
    :param avatar: (str) avatar path
    :param keywords: (str) Key words associated with page
    :param author: (str) Author associated with page
    :param email: (str) Public contact email
    :param l_css: (list) List of css files used for every page
    :param l_js: (list) List of css files used for every page
    :param d_socialmedia: (dict) social media urls dict
    :param l_sidebar: (list of dicts) List of objs for the sidebar
    :param d_css: (dict) A dict of various CSS parameters
    :param shownews: (bool) If True, show news
    :param homelink: (str) If set, use this as the "homepage" link
        when you click the page title (in the upper left corner)
    :param verbose: (bool) If True, print stuff
    :returns: (dict) The props dict required by all templates
    :rtype: dict
    """

    news = ''
    if shownews:
        news = getnews(datadir)

    # Set base.html (parent) template properties
    # 'ishomepage' starts as False, and is turned on if homepage
    d_props = {
        'favicon': favicon,
        'avatar': avatar,
        'css': l_css,
        'params': d_css,
        'js': l_js,
        'version': version,
        'year': str(datetime.datetime.now().year),
        'title': pagetitle,
        'domain': pagedomain,
        'sitekeywords': keywords,
        'siteauthor': author,
        'email': email,
        'social': d_socialmedia,
        'news': news,
        'sidebar': l_sidebar,
        'homelink': homelink,
        'ishomepage': 0
    }

    if verbose:
        print('Common props:')
        print(json.dumps(d_props, indent=4))

    return d_props

def errorcheckuniq(mycontentjson, attr='url', verbose=False):
    """
    Check for uniqueness of attribute

    :param mycontentjson: (list of dicts) A json representing page objects
    :param attr: (str) the attribute to check (default: url)
    :param verbose: (bool) If True, print stuff
    """

    if verbose:
        print(f'Checking for {attr} uniqueness ...')

    # inspiration:
    # https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
    seen = []
    duplicates = []

    for i in mycontentjson:
        if i[attr] in seen:
            duplicates.append(i[attr])
        else:
            seen.append(i[attr])

    if len(duplicates) > 0:
        color.warnprint(f'ERROR: {attr} attribute must be unique but found overlap: {duplicates}')
    assert len(duplicates) == 0, f'{attr} attribute must be unique'

def errorcheckuniqcategory(mysectionsjson):
    """
    Check that sidebar json has unique categories.
    If error, stop the whole show

    :param mysectionsjson: (list of dicts) A json representing posts
    """

    mycategories = [i['category'] for i in mysectionsjson]
    assert len(mycategories) == len(set(mycategories)), 'Section category attributes must be unique'

def errorcheckpostfields(mycontentjson, strict=True):
    """
    Ensure a post object has required fields

    :param mycontentjson: (list of dicts) A json representing post objects
    :param strict: (bool) if True, throw errors
    """

    if strict:
        for i in mycontentjson:
            assert set(REQUIRED_POST_FIELDS).issubset(set(i.keys())), f'Missing keys for post: {i}'

def errorchecksectionfields(mycontentjson, strict=True):
    """
    Ensure a section object has required fields

    :param mycontentjson: (list of dicts) A json representing section objects
    :param strict: (bool) if True, throw errors
    """

    if strict:
        for i in mycontentjson:
            assert set(REQUIRED_SECTION_FIELDS).issubset(set(i.keys())), f'Missing keys for post: {i}'

def filterandtweakjson(mycontentjson, homeurl, verbose=False):
    """
    Make some necessary changes to the content json—namely,
    remove the posts where publish == False;
    change the "files" attribute from a string to a list;
    add urlpath attribute.

    :param mycontentjson: (list of dicts) A json representing visual (img, video) posts
    :param homeurl: (str) homepage url
    :param verbose: (bool) If True, print stuff
    :returns: (list of dicts) A revised json
    :rtype: list
    """

    l = []

    for i in mycontentjson:
        # Throw away unpublished elts
        if i['publish']:
            # Deep copy so we don't modify the iterating variable
            j = i.copy()
            # Convert various attribute from str to list
            for attrib in ['category', 'files', 'keywords']:
                # This construction does double duty by checking both presence and that value is not empty
                if i.get(attrib):
                    j[attrib] = [k.strip() for k in i[attrib].split(',')]
                else:
                    j[attrib] = []

            # Ensure no trailing whitespace
            j['url'] = i['url'].strip()

            # Get the url path and save a non-empty copy
            # in case it gets set to '' for the homepage.
            # If the urlpath is already set, do not disturb it
            if not j.get('urlpath'):
                j['urlpath'] = geturlpath(j)
            j['ishomepage'] = False
            j['urlpathnonempty'] = j['urlpath']

            if j['url'] == homeurl:
                j['ishomepage'] = True
                j['urlpath'] = ''

            l.append(j)

    if verbose:
        print('filtered json:')
        print(json.dumps(l, indent=4))

    return l

def geturlpath(d_page, prefix='', override=''):
    """
    Return the full url path.
    Recall the attribute "url" is a unique key, not the actual path.
    This function gets the actual path, with the exception of the homepage.
    The homepage is a special case and its urlpath gets set to the root path
    just before it's created

    :param d_page (dict): a dict representing a page object
    :param prefix: (str) if set, prefix the url with this value
    :param override: (str) if set, set the url to this value
    :returns: (str) the full url path
    :rtype: str
    """

    if override:
        return override
    elif prefix:
        return f"{prefix}/{d_page['url']}"
    elif d_page['url'] == 'latest':
        # This is a little confusing
        # In the special case where url is latest,
        # We want the path to be: latest/1
        # The idea is, we might want the second most recent post at latest/2 and so on
        return 'latest/1'
    elif d_page['specialpage']:
        return d_page['url']
    elif d_page['type'] in ['sectionvisual', 'sectionarticle']:
        return d_page['url']
    elif d_page['type'] in ['img', 'video', 'article']:
        return f"post/{d_page['url']}"

def createcategorydict(mycontentjson, verbose=False):
    """
    Restructure content json from a json-like list of dicts
    to a dict whose keys are categories. So it starts looking like this:

        [
            {
                "name": "Post1",
                "category": "travel"
            },
            {
                "name": "Post2",
                "category": "travel,food"
            }
        ]

    But ends looking like this:

        {
            "travel": [
                {
                    "name": "Post1",
                    "category": "travel"
                },
                {
                    "name": "Post2",
                    "category": "travel,food"
                }
            ],
            "food": [
                {
                    "name": "Post2",
                    "category": "travel,food"
                }
            ]
        }

    Note: if post is missing category, it gets thrown out.
    Note: if post is special page, it gets thrown out.

    :param mycontentjson: (list of dicts) A json representing visual (img, video) posts
    :param verbose: (bool) If True, print stuff
    :returns: (dict)
        A dict whose keys are categories and whose values are
        jsons (lists of dicts) representing the visual posts for that category
    :rtype: dict
    """

    res = dict()

    for i in mycontentjson:
        if i['specialpage']:
            continue
        if not i['category']:
            continue
        # Create category keys
        for mycategory in i['category']:
            # Initialize category if not yet seen
            if not mycategory in res:
                res[mycategory] = []
            res[mycategory].append(i)

    if verbose:
        print('content dict:')
        print(json.dumps(res, indent=4))

    return res

def createfeed(l_posts, numposts, verbose=False):
    """
    Update the content dict to add feed,
    which is simply the top NUMPOSTSFEED most recent posts

    :param l_all (list of dicts): a json - i.e., a list of post object dicts
    :param numposts (int): number of posts
    :param verbose: (bool) If True, print stuff
    :returns: (list of dicts) A list of the NUMPOSTSFEED most recent post
    :rtype: list
    """

    if not l_posts:
        return []

    # Filter out special pages and pages with no date
    l_filter = [i for i in l_posts if i['date'] and not i['specialpage']]

    # Find newest posts by sorting by date
    # Throw out objs with no date
    sortedbydate = sorted(
        l_filter,
        key=lambda d: datetime.datetime.strptime(d['date'], "%Y-%m-%d"),
        # key=lambda d: int(''.join(d['date'].split('-'))),
        reverse=True
    )

    return sortedbydate[0:numposts]

def createnavarrowsbysection(d_category2posts, verbose=False):
    """
    Create material the HTML for navigation arrows: << < > >>
    The point of this is so the user can click through the content from the post view.
    However, this function, unlike createnavarrows, restricts navigation to category.
    I.e., from one page you can only get to pages of the same category.
    This function returns a dict like this:

        {
            "url1":
                {
                    "first": "url_a",
                    "prev": "url_b",
                    "next": "url_c",
                    "last": "url_d",
                },
            "url2":
                {
                    "first": "url_a",
                    "prev": "url_x",
                    "next": "url_y",
                    "last": "url_d",
                }
        }

    :param d_category2posts (dict):
        A dict whose keys are categories and whose values are
        jsons (lists of dicts) representing the posts for that category
    :param verbose: (bool) If true, print stuff
    :returns: (dict)
        A dict whose keys are urls and whose values are
        dicts with the keys "first", "prev", "next", "last"
        and values corresponding to that url
    :rtype: dict
    """

    if verbose:
        print('Create nav dict')

    d_nav = dict()

    #print('dict for nav')
    #print(json.dumps(d_category2posts, indent=4))

    # This gets muddled when things are in two categories
    # everything starts to break
    # To fix this, remove duplicates
    # Practically, this means the first category will prevail
    # the secondary categories will be ignored
    d_category2posts_noduplicates = dict()
    already_seen = set()
    for mykey, mycontentjson in d_category2posts.items():

        for i in mycontentjson:
            if i['url'] in already_seen:
                continue
            else:
                if not mykey in d_category2posts_noduplicates:
                    d_category2posts_noduplicates[mykey] = []
                d_category2posts_noduplicates[mykey].append(i)
                already_seen.add(i['url'])

    #print('duplicates removed')
    #print(json.dumps(d_category2posts_noduplicates, indent=4))

    for mykey, mycontentjson in d_category2posts_noduplicates.items():

        #print('mykey')
        #print(mykey)

        # Sort by category, before creating navigating arrows
        # (via https://stackoverflow.com/questions/72899/how-to-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary-in-python )
        # Importantly, the argument to sorted is left untouched
        mycontentjsonsorted = sorted(mycontentjson, key=lambda d: d['category'])

        #print('mycontentjsonsorted')
        #print(mycontentjsonsorted)

        for i,j in enumerate(mycontentjsonsorted):
            d_nav[j['url']] = {
                "first": mycontentjsonsorted[0]['urlpath'],
                "prev": "",
                "next": "",
                "last": mycontentjsonsorted[-1]['urlpath']
            }
            # Get the previous URL
            if i == 0:
                d_nav[j['url']]['prev'] = mycontentjsonsorted[0]['urlpath']
            else:
                d_nav[j['url']]['prev'] = mycontentjsonsorted[i - 1]['urlpath']
            # Get the next URL
            if i == len(mycontentjsonsorted) - 1:
                d_nav[j['url']]['next'] = mycontentjsonsorted[-1]['urlpath']
            else:
                d_nav[j['url']]['next'] = mycontentjsonsorted[i + 1]['urlpath']

        #print(f'nav dict updated:')
        #print(json.dumps(d_nav, indent=4))

    if verbose:
        print('nav dict final:')
        print(json.dumps(d_nav, indent=4))

    return d_nav

def checkcategories(mycategories, mycontentjson, d_category2posts, verbose=False):
    """
    Raise warning if content json has unknown category or
    if category empty. Do not consider special pages

    :param mycategories: (list) A list of categories
    :param mycontentjson: (list of dicts) A json representing posts
    :param d_category2posts (dict):
        A dict whose keys are categories and whose values are
        jsons (lists of dicts) representing the posts for that category
    :param verbose: (bool) If true, print stuff
    """

    for i in mycontentjson:
        if i['specialpage']:
            continue
        # If no category, warn then ignore
        if not i['category']:
            color.warnprint(f"WARNING: post {i['url']} has no category")
            continue
        if len(i['category']) > 1:
            color.warnprint(f"WARNING: post {i['url']} has multiple categories - this will create problems when using nav arrows")
        # If unknown category, warn
        for j in i['category']:
            if not j in mycategories:
                color.warnprint(f"WARNING: post {i['url']} has unknown category ({j})")

    for i in mycategories:
        if not i in d_category2posts:
            color.warnprint(f"WARNING: There are no posts for category: {i}")

def create404(
        d_props,
        templatepath,
        outputdir,
        verbose=False
    ):
    """
    Build the main landing page, creating the index.html file
    in the output directory. Also create error.html for 404 errors

    :param d_props (dict): The common props dict
    :param templatepath: (str) Path to the directory containing templates
    :param outputdir: (str) Path to the output directory
    :param verbose: (bool) If True, print stuff
    """

    # Get Jinja2 env
    env = getenv(templatepath)

    # Create error page
    d_props_error_page = d_props.copy()
    template = env.get_template(d_TYPE2TEMPLATE['error'])
    # Overwrite these keys
    d_props_error_page['title'] = f"{d_props['title']} | 404: Page Not Found"
    d_props_error_page['keywords'] = 'error'
    mypage = removeemptylines(template.render(props = d_props_error_page))
    print(mypage, file=open(f"{outputdir}/error.html", 'w'))

def mkpagedir(
        mydirectory,
        myname,
        mypagetype,
        mymarker,
        myurl
    ):
    """
    Make directory for page

    :param mydirectory: (str) The directory
    :param myname: (str) Page name
    :param mypagetype: (str) Page type
    :param mymarker: (str) the kind of page being created
    :param myurl: (str) a url string to echo to console
    """

    print(f'Create {mypagetype} page [{mymarker}]: {myname} at url = /{myurl}')

    # mkdir
    try:
        os.makedirs(mydirectory)
    except:
        pass

def readarticlecontent(
        datadir,
        name,
        url,
        strict=True
    ):
    """
    Read article content

    :param datadir: (str) path to the data directory
    :param name: (str) post name
    :param url: (str) url
    :param verbose: (bool) if True, print stuff
    :param strict: (bool) if True, throw errors
    :returns: (str) the article content
    :rtype: str
    """

    res = ''

    # Expected location
    articlepath = f'{datadir}/published/article/{url}/html/content.html'

    try:
        with open(articlepath, 'r') as g:
            for contentline in g:
                res += contentline
    except:
        color.warnprint(f'WARNING: Cannot read content.html for: {name}')
        if strict:
            assert False, f"Error: content.html not found for: {url}"

    return res

def createpage(
        d_page,
        d_props,
        d_nav,
        templatepath,
        datadir,
        outputdir,
        addjs=[],
        addcss=[],
        xtemplate='',
        marker='post',
        verbose=False,
        strict=True
    ):
    """
    From a page object, create an actual page - i.e.,
    a folder with an index.html file inside it

    :param d_page (dict): a dict representing a post
    :param d_props (dict): the common props dict
    :param d_nav (dict):
        a dict whose keys are urls and whose values are
        dicts with the keys "first", "prev", "next", "last"
        and values corresponding to that url
    :param templatepath: (str) path to the directory containing templates
    :param datadir: (str) path to the data directory
    :param outputdir: (str) path to the output directory
    :param addjs: (list) a list of additional js files
    :param addcss: (list) a list of additional css files
    :param xtemplate: (str) the (external) template
        If provided, this overrides the template determined by page type
    :param marker: (str) the kind of page being created (default: post)
    :param verbose: (bool) if True, print stuff
    :param strict: (bool) if True, throw errors
    """

    # Get Jinja env
    env = getenv(templatepath)

    # Copy the common props shared by every post (so as not to modify the argument)
    d_props_page = d_props.copy()

    # Add CSS
    d_props_page['css'] = d_props_page['css'] + addcss
    # Note: this: d_props_page['css'].extend(addcss) leads
    # to a bug where it's modifying the reference, not the copy

    # Add JS
    d_props_page['js'] = d_props_page['js'] + addjs

    # Copy the page object so as not to modify the argument
    mypage = d_page.copy()

    mydirectory = f"{outputdir}/{mypage['urlpath']}"

    if mypage['ishomepage']:
        marker = 'homepage'
        d_props_page['ishomepage'] = 1

    mkpagedir(
        mydirectory,
        mypage['name'],
        mypage['type'],
        marker,
        mypage['urlpath']
    )

    # Set template
    template = None
    try:
        # This can fail for special pages
        template = env.get_template(d_TYPE2TEMPLATE[mypage['type']])
    except:
        pass
    # If url key specific template, override page type specific template
    if xtemplate:
        template = env.get_template(xtemplate)

    if not template:
        color.warnprint(f"ERROR: template not fouund: {mypage['url']}")
        assert False, 'No template'

    # If article, read HTML contents
    if mypage['type'] == 'article':
        # Note: use mypage['url'] bc it's possible mypage['urlpath'] == ''
        # which won't work for readarticlecontent()
        d_props_page['articlebody'] = readarticlecontent(
            datadir,
            mypage['name'],
            mypage['url'],
            strict=strict
        )

    # Create index.html page
    d_props_page['content'] = mypage

    if d_nav:
        d_props_page['nav'] = d_nav.get(mypage['url'])

    if mypage['url'] == DEBUG:
        print('*** debug ***')
        print(f"props for url: {mypage['url']}")
        print(json.dumps(d_props_page, indent=4))
        print()

    # Using global vars does not follow best practices,
    # but it's convenient. Otherwise, have to return a list
    # and keep track of it through many function calls
    global l_log_global
    l_log_global.append({
        'name': mypage['name'],
        'urlpath': f"/{mypage['urlpath']}",
        'urlkey': mypage['url'],
        'type': mypage['type'],
        'marker': marker,
        'template': os.path.basename(template.filename),
        'directory': mydirectory,
        'css': ','.join(d_props_page['css']),
        'js': ','.join(d_props_page['js'])
    })

    finalpage = removeemptylines(template.render(props = d_props_page))
    print(finalpage, file=open(f"{mydirectory}/index.html", 'w'))

def getmarker(ishomepage, specialpage, other):
    """
    Quick function to get the marker (a message echoed to console)

    :param ishomepage: (bool) if True, return 'homepage'
    :param special (int): if 1 (True), return 'specialpage'
    :param other: (str) if not ishomepage or specialpage, return this
    :returns: the marker
    :rtype: str
    """

    if ishomepage:
        return 'homepage'
    elif specialpage:
        return 'specialpage'
    else:
        return other

def createpagewrapper(
        d_page_input,
        d_common_props,
        d_vis_category2posts,
        d_article_category2posts,
        d_nav_vis,
        d_nav_article,
        l_feed_vis,
        l_feed_article,
        l_selected_vis,
        l_selected_article,
        templatepath,
        datadir,
        outputdir,
        verbose=False,
        strict=True
    ):
    """
    This is a wrapper over the function createpage().
    It tweaks the page object and the props dict
    before passing them to createpage(). It also
    handles some special pages, such as 'latest'

    :param d_page_input (dict): a dict representing a page
    :param d_common_props (dict): the common props dict
    :param d_vis_category2posts (dict): dict with categories as keys and jsons as values (for visual posts)
    :param d_article_category2posts (dict): ditto for article posts
    :param d_nav_vis (dict):
        a dict whose keys are urls and whose values are
        dicts with the keys "first", "prev", "next", "last"
        and values corresponding to that url (for visual posts)
    :param d_nav_article (dict): ditto for article posts
    :param l_feed_vis (list): visual post feed
    :param l_feed_article (list): article post feed
    :param l_selected_vis (list): selected visual posts
    :param l_selected_article (list): selected article posts
    :param templatepath: (str) path to the directory containing templates
    :param datadir: (str) path to the data directory
    :param outputdir: (str) path to the output directory
    :param verbose: (bool) if True, print stuff
    :param strict: (bool) if True, throw errors
    """

    # Copy dicts, so as not to modify the function arguments
    d_props = d_common_props.copy()
    d_page = d_page_input.copy()

    ## Get posts for section type pages

    l_posts = []

    # Set l_posts
    if d_page['url'] == 'selected':
        # 'selected' is a special page
        # (assumed to be a section type page (todo: check?))
        l_posts = l_selected_vis
    elif d_page['url'] == 'feed':
        # 'feed' is a special page
        # (assumed to be a section type page (todo: check?))
        l_posts = l_feed_vis
    elif d_page['type'] == 'sectionvisual':
        # todo: error checking should have already happened at this point (fix)
        if len(d_page['category']) > 0:
            l_posts = d_vis_category2posts.get(d_page['category'][0], [])
        else:
            color.warnprint(f"WARNING: no category for section page: {i['url']}")
    elif d_page['type'] == 'sectionarticle':
        if len(d_page['category']) > 0:
            l_posts = d_article_category2posts.get(d_page['category'][0], [])
        else:
            color.warnprint(f"WARNING: no category for section page: {i['url']}")

    d_props['posts'] = l_posts

    ## Get nav dict for post type pages

    # Pointer to nav dict
    d_nav = dict()
    if d_page['url'] == 'cover':
        # 'cover' is a special page: turn off navigation arrows
        pass
    elif d_page['url'] == 'latest':
        # 'latest' is a special page: turn off navigation arrows
        pass
    elif d_page['type'] == 'article':
        d_nav = d_nav_article
    elif d_page['type'] == 'img' or d_page['type'] == 'video':
        d_nav = d_nav_vis

    ## Latest is a special case

    if d_page['url'] == 'latest':

        # Modify d_page
        # Instead of using the d_page dict, use a copy of the latest visual post
        d_page = l_feed_vis[0].copy()
        # Turn this on
        d_page['showdate'] = 1
        # This is tricky:
        # We've switched the page to the most recent visual post
        # However, we need to preserve attributes from d_page_input
        # For example, if HOMEPAGE == 'latest', we need to make sure
        # this is honored regardless of the 'ishomepage' attribute of the most recent post
        d_page['ishomepage'] = d_page_input['ishomepage']
        # Ditto: the urlpath attr needs to be updated to that of d_page_input (latest/1)
        d_page['urlpath'] = d_page_input['urlpath']
        # This is a hack
        # In the case the lastest post is the homepage
        # and the Latest Feed is active with at least 2 posts
        # we want to navigate from the homepage to the lastest
        # feed with arrows. This accomplishes that in an awkward way,
        # taking us from the homepage to the second elt of the feed
        # todo: figure out a more elegant way to do this
        if d_page['ishomepage'] and LATESTFEED and NUMPOSTSFEED > 1:
            d_page['hackurl'] = 'latest/2'

    ## Finally, create page

    if d_page['url'] == DEBUG:
        print('*** debug ***')
        print(f"input to createpage() for url: {d_page['url']}")
        print(json.dumps(d_page, indent=4))
        print()

    createpage(
        d_page,
        d_props,
        d_nav,
        templatepath,
        datadir,
        outputdir,
        addjs = d_TYPE2JS.get(d_page['type'], []) + d_URL2JS.get(d_page['url'], []),
        addcss = d_TYPE2CSS.get(d_page['type'], []) + d_URL2CSS.get(d_page['url'], []),
        xtemplate = d_page.get('template', ''),
        marker = getmarker(d_page['ishomepage'], d_page['specialpage'], d_page['type']),
        verbose = verbose,
        strict = strict
    )

#-------------------------------------------------------------------------------
#   Main
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    ### Generate pages with Jinja

    args = getarg()

    # Path to templates directory
    templatepath = args.templates
    # Path to data directory
    datadir = args.data
    # Path to output directory
    outputdir = args.outputdir
    # strict
    strict = not args.nostrict

    # Import constants, found in datadir/dataconfig.py
    sys.path.append(datadir)
    from dataconfig import SITETITLE
    from dataconfig import DOMAIN
    from dataconfig import SITEWORDS
    from dataconfig import SITEAUTHOR
    from dataconfig import EMAIL
    from dataconfig import HOMEPAGE
    from dataconfig import HOMELINK
    from dataconfig import SIDEBAR
    from dataconfig import d_SOCIALMEDIA
    from dataconfig import FAVICON
    from dataconfig import AVATAR
    from dataconfig import NUMPOSTSFEED
    from dataconfig import SHOWNEWS
    from dataconfig import DUPLICATEHOME
    from dataconfig import LATESTFEED
    from dataconfig import BASE_JS
    from dataconfig import d_TYPE2JS
    from dataconfig import d_URL2JS
    from dataconfig import BASE_CSS
    from dataconfig import d_TYPE2CSS
    from dataconfig import d_URL2CSS
    from dataconfig import d_CSS
    from dataconfig import d_TYPE2TEMPLATE
    from dataconfig import l_SPECIAL_PAGES

    ## Read data

    sectionsjson = []
    contentvisjson = []
    contentarticlejson = []

    # Get sections
    with open(f'{datadir}/content.sections.json', 'r') as f:
        contentsectionjson = json.load(f)

    # Get visual posts (imgs and video)
    with open(f'{datadir}/content.visual.json', 'r') as f:
        contentvisjson = json.load(f)

    # Get article posts
    with open(f'{datadir}/content.article.json', 'r') as f:
        contentarticlejson = json.load(f)

    ## Check for errors

    for j in [i['url'] for i in contentsectionjson + contentvisjson + contentarticlejson]:
        assert j not in RESERVED, f'Clash with reserved url for page object: {j}'

    # Check for category uniqueness
    errorcheckuniqcategory(contentsectionjson)

    # Check for url uniqueness
    errorcheckuniq(
        l_SPECIAL_PAGES + contentsectionjson + contentvisjson + contentarticlejson,
        attr = 'url',
        verbose = args.verbose
    )

    # Misc errors
    for i in d_SOCIALMEDIA.keys():
        assert i in ALLOWED_SOCIAL, f'Found unrecognized social media type: {i}'

    ## Create various data structures

    # Create a big dict of everything, with urls as keys
    d_all = {
        i['url']:i for i in l_SPECIAL_PAGES + contentsectionjson + contentvisjson + contentarticlejson
    }

    # Filter out unpublished, tweak, add urlpath attribute
    specialjson_pub = filterandtweakjson(l_SPECIAL_PAGES, HOMEPAGE)
    sectionsjson_pub = filterandtweakjson(contentsectionjson, HOMEPAGE)
    postvisjson_pub = filterandtweakjson(contentvisjson, HOMEPAGE)
    postarticlejson_pub = filterandtweakjson(contentarticlejson, HOMEPAGE)

    # Concat
    l_all_pub = specialjson_pub + sectionsjson_pub + postvisjson_pub + postarticlejson_pub

    # Dict for all published stuff
    d_all_pub = {i['url']:i for i in l_all_pub}

    # List of all published section urls
    l_section_url_pub = [i['url'] for i in sectionsjson_pub]

    # Get feeds (i.e., most recent posts)
    l_feed_vis = createfeed(postvisjson_pub, NUMPOSTSFEED)
    l_feed_article = createfeed(postarticlejson_pub, NUMPOSTSFEED)

    # Get selected posts
    l_selected_vis = [i for i in postvisjson_pub if i['selected']]
    l_selected_article = [i for i in postarticlejson_pub if i['selected']]

    # Create category dicts (mapping the categories to their associated posts)
    d_vis_category2posts = createcategorydict(postvisjson_pub, verbose = args.verbose)
    d_article_category2posts = createcategorydict(postarticlejson_pub, verbose = args.verbose)

    # Get category lists for article flavor and visual flavor
    l_category_vis = []
    l_category_article = []
    for i in sectionsjson_pub:
        if i['type'] == 'sectionvisual':
            l_category_vis.extend(i['category'])
        elif i['type'] == 'sectionarticle':
            l_category_article.extend(i['category'])

    # Create navigation dicts
    d_nav_vis = createnavarrowsbysection(d_vis_category2posts)
    d_nav_article = createnavarrowsbysection(d_article_category2posts)

    ## More error checking

    # Check for urlpath uniqueness
    errorcheckuniq(l_all_pub, attr = 'urlpath', verbose = args.verbose)

    # Check for existence of img files, in both data directory and output directory
    # See: https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
    checkpath(f'{datadir}/published/img', [i['thumbnail'] for i in postvisjson_pub])
    checkpath(f'{datadir}/published/img', sum([i['files'] for i in postvisjson_pub if i['type'] == 'img'], []))
    checkpath(f'{datadir}/published/video', sum([i['files'] for i in postvisjson_pub if i['type'] == 'video'], []))
    checkpath(f'{outputdir}/static/img', [i['thumbnail'] for i in postvisjson_pub])
    checkpath(f'{outputdir}/static/img', sum([i['files'] for i in postvisjson_pub if i['type'] == 'img'], []))
    checkpath(f'{outputdir}/static/video', sum([i['files'] for i in postvisjson_pub if i['type'] == 'video'], []))
    # Check for templates
    checkpath(templatepath, list(d_TYPE2TEMPLATE.values()))
    checkpath(templatepath, [i['template'] for i in l_all_pub if i.get('template')])

    # todo: make this section- and post-specific (now they're jumbled together)
    for i in d_all.values():
        assert i['type'], f'Missing type for page object: {i}'
        assert i['type'] in ALLOWED_TYPES, f'Unknown type for page object: {i}'

    assert HOMEPAGE, f'Homepage not found'
    assert SIDEBAR, f'Sidebar not found'
    assert HOMEPAGE in d_all_pub.keys(), f'Homepage url: {HOMEPAGE} not found'
    if HOMELINK:
        assert HOMELINK in d_all_pub.keys(), f'Homelink url: {HOMELINK} not found'
    for i in SIDEBAR:
        assert i in d_all_pub.keys(), f'Sidebar url: {i} not found'

    # todo: implement feed for articles as well
    if HOMEPAGE == 'latest' or 'feed' in d_all_pub.keys():
        assert len(l_feed_vis) > 0, 'Feed is empty'

    # Check for existence of CSS and JS files
    cssfiles = [i for i in list(d_TYPE2CSS.values()) + list(d_URL2CSS.values())]
    cssfiles.append(BASE_CSS)
    cssfiles = sum(cssfiles, [])
    # print(cssfiles)
    jsfiles = [i for i in list(d_TYPE2JS.values()) + list(d_URL2JS.values())]
    jsfiles.append(BASE_JS)
    jsfiles = sum(jsfiles, [])
    # print(jsfiles)
    checkpath(outputdir, cssfiles, verbose=args.verbose)
    checkpath(outputdir, jsfiles, verbose=args.verbose)
    if AVATAR:
        if not os.path.isfile(f'{outputdir}/{AVATAR}'):
            color.warnprint(f'WARNING: file not found: {outputdir}/{AVATAR}')
    if FAVICON:
        if not os.path.isfile(f'{outputdir}/{FAVICON}'):
            color.warnprint(f'WARNING: file not found: {outputdir}/{FAVICON}')
    else:
        color.warnprint(f'WARNING: No favicon')

    # Check all keys exist
    errorchecksectionfields(sectionsjson_pub, strict=strict)
    errorcheckpostfields(postvisjson_pub, strict=strict)
    errorcheckpostfields(postarticlejson_pub, strict=strict)

    # Check categories for visual and articleposts
    checkcategories(l_category_vis, postvisjson_pub, d_vis_category2posts)
    checkcategories(l_category_article, postarticlejson_pub, d_article_category2posts)

    ## Print stuff

    print(f'Site title: {SITETITLE}')
    print(f'Site domain: {DOMAIN}')
    print(f'Homepage: {HOMEPAGE}')
    print(f'Homelink: {HOMELINK}')
    print(f'Duplicate homepage: {DUPLICATEHOME}')
    print(f'keywords: {SITEWORDS}')
    print(f'email: {EMAIL}')
    print(f'Visual post categories: {l_category_vis}')
    print(f'Article post categories: {l_category_article}')
    print(f"Special pages: {[i['url'] for i in specialjson_pub]}")
    print(f'Feed length: {NUMPOSTSFEED}')
    print(f'Create Latest Feed: {LATESTFEED}')
    print(f"All pages: {[i['url'] for i in l_all_pub]}")
    print(f"Visual feed: {[i['url'] for i in l_feed_vis]}")
    print(f"Article feed: {[i['url'] for i in l_feed_article]}")
    print(f'Sidebar: {SIDEBAR}')
    print(f'Favicon: {FAVICON}')
    print(f'Avatar: {AVATAR}')
    print(f'Base CSS: {BASE_CSS}')
    print('Page type specific CSS:')
    print(json.dumps(d_TYPE2CSS, indent=4))
    print('url key specific CSS:')
    print(json.dumps(d_URL2CSS, indent=4))
    print('CSS Options:')
    print(json.dumps(d_CSS, indent=4))
    print(f'Base JS: {BASE_JS}')
    print('Page type specific JS:')
    print(json.dumps(d_TYPE2JS, indent=4))
    print('url key specific JS:')
    print(json.dumps(d_URL2JS, indent=4))
    print('Post type to template dict:')
    print(json.dumps(d_TYPE2TEMPLATE, indent=4))
    print('Socials:')
    print(json.dumps(d_SOCIALMEDIA, indent=4))
    print()

    ## Build pages

    # Create sidebar
    l_sidebar = createsidebar(d_all_pub, SIDEBAR)

    # Create the common props dict shared by all pages
    myhomelink = ''
    if HOMELINK:
        myhomelink = d_all_pub[HOMELINK]['urlpath']
    d_common_props = getcommonprops(
        datadir,
        SITETITLE,
        DOMAIN,
        VERSION,
        FAVICON,
        AVATAR,
        SITEWORDS,
        SITEAUTHOR,
        EMAIL,
        BASE_CSS,
        BASE_JS,
        d_SOCIALMEDIA,
        l_sidebar,
        d_CSS,
        SHOWNEWS,
        homelink = myhomelink,
        verbose = args.verbose
    )

    # Build all pages
    for i in l_all_pub:

        if i['url'] == DEBUG:
            print('*** debug ***')
            print(f"Page object: {i['url']}")
            print(i)
            print()

        createpagewrapper(
            i,
            d_common_props,
            d_vis_category2posts,
            d_article_category2posts,
            d_nav_vis,
            d_nav_article,
            l_feed_vis,
            l_feed_article,
            l_selected_vis,
            l_selected_article,
            templatepath,
            datadir,
            outputdir,
            verbose=args.verbose,
            strict=strict
        )

    # If DUPLICATEHOME, duplicate the homepage so it exists
    # both at the root url path as well as at the location
    # at its url attr
    if DUPLICATEHOME:
        print('Duplicating homepage...')
        # Copy the page object and create it at its ordinary url path
        d_page = d_all_pub[HOMEPAGE]
        mypage = d_page.copy()
        mypage['ishomepage'] = False
        # Hack to ensure page not created at root URL path
        mypage['urlpath'] = mypage['urlpathnonempty']

        createpagewrapper(
            mypage,
            d_common_props,
            d_vis_category2posts,
            d_article_category2posts,
            d_nav_vis,
            d_nav_article,
            l_feed_vis,
            l_feed_article,
            l_selected_vis,
            l_selected_article,
            templatepath,
            datadir,
            outputdir,
            verbose=args.verbose,
            strict=strict
        )

    # Generate error page
    create404(
        d_common_props,
        templatepath,
        outputdir,
        verbose = args.verbose
    )

    # Build a set of Latest Feed pages
    if LATESTFEED:
        print('Creating latest feed...')
        l_latest = []
        for idx, i in enumerate(l_feed_vis):
            j = i.copy()
            # Remap urlpath to lastest/1, latest/2, latest/3, etc.
            j['urlpath'] = f'latest/{str(idx + 1)}'
            j['showdate'] = 1
            j['ishomepage'] = False
            l_latest.append(j)

        # Create nav dict
        d_nav_latest = createnavarrowsbysection({'latest': l_latest})

        for i in l_latest:
            createpage(
                i,
                d_common_props,
                d_nav_latest,
                templatepath,
                datadir,
                outputdir,
                addjs = d_TYPE2JS.get(i['type'], []) + d_URL2JS.get(i['url'], []),
                addcss = d_TYPE2CSS.get(i['type'], []) + d_URL2CSS.get(i['url'], []),
                xtemplate = i.get('template', ''),
                marker = 'specialpage',
                verbose = args.verbose,
                strict=strict
            )

    # Logging
    if args.logfile:
        df = pd.DataFrame(data=l_log_global)
        df.to_csv(args.logfile, sep="\t", index=False)
