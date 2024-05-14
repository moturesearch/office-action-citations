'''
Notes
.find returns None if nothing found.
'''

import re
import requests


def get_title(bibl_struct):

    title_di = {}
    levels = ["a", "m"]
    for level in levels:
        title_di[f'title_main_{level}'] = bibl_struct.find("title", {"level": level, "type": "main"})
        title_di[f'title_{level}'] = bibl_struct.find("title", {"level": level})

    title = next((value for value in title_di.values() if value is not None), None)
    # This will return the first non none value (if all values are none it will return none)

    if title != None:

        title = title.get_text()

        title = re.sub(r'&Amp;|&Amp|&', ' ', title)
        title = re.sub(r'\\n', ' ', title)
        title = title.encode("ascii", "ignore").decode("utf-8")
        title = re.sub("[^A-Za-z0-9]", " ", title)
        title = re.sub(r'\s+', '%20', title.strip())

        if len(title) == 0:
            title = None

    return title


def get_author_id(bibl_struct):

    first_author = bibl_struct.find('author')

    if first_author == None:
        author_id = None

    else:

        firstname = first_author.find('forename', {'type':'first'})
        middlename = first_author.find('forename', {'type':'middle'})
        lastname = first_author.find('surname')

        author = ''
        parts = [firstname, middlename, lastname]
        for item in parts:

            if item != None:

                item_text = item.get_text()
                if item_text not in ['Et', 'et', 'Al', 'al', None]:
                    # seems that [Et et Al al] appear by themselves (eg <surname>Et</surname>) rather than 'name et'
                    author = author + item_text + ' '

        author = re.sub(r' $', '', author)
        # author - will be an empty string if 'author' not found or if all parts are Et et Al al

        # GET AUTHOR ID
        if len(author) != 0:
            author_id = get_id(location='authors', field=author)
        else:
            author_id = None

    return author_id


def get_year(bibl_struct):

    try:
        year = bibl_struct.find("date", {"type": "published"})['when']
    except:
        year = ''

    if len(year) > 4:
        year = year[:4]  # gets first 4 chars from string

    if ((year.isnumeric() == False) or (len(year) != 4) or (len(year) == 0)):
        year = None

    # year - will be None if year not found or if not numeric etc
    return year


def get_journal_id(bibl_struct):

    try:
        journal = bibl_struct.find("title", {"level": "j"}).get_text()
        journal_id = get_id(location='sources', field=journal)
    except:
        journal_id = None

    return journal_id


def get_id(location, field):

    # location='authors', field=author
    # location='sources', field=journal

    field = re.sub(r'\s+', '%20', field.strip())
    r_field = requests.get(f"https://api.openalex.org/{location}?search={field}&per-page=1&mailto=xx@gmail.com")

    try:
        id_field = r_field.json()["results"][0]["id"]
        id_field = re.sub("https://openalex.org/", "", id_field)
    except:
        id_field = None

    return id_field


def get_val(bibl_struct, val_name):

    # val_name: "volume", "issue"

    val = bibl_struct.find("biblScope", {"unit": val_name})

    if val != None:
        val = val.get_text()

    return val


def get_page(bibl_struct, position):

    # position: "from", "to" (gives first page & last page)

    try:
        page = bibl_struct.find("biblScope", {"unit": "page"})[position]

        page = re.sub(r'[^0-9]', '', page)  # only keep numbers.
        if len(page) == 0:
            page = None
    except:
        page = None

    return page


def get_extra_info(bibl_struct):

    volume = get_val(bibl_struct=bibl_struct, val_name="volume")
    issue = get_val(bibl_struct=bibl_struct, val_name="issue")
    first_page = get_page(bibl_struct=bibl_struct, position="from")
    last_page = get_page(bibl_struct=bibl_struct, position="to")

    extra_info_val = [volume, issue, first_page, last_page]

    for i, extra_info in enumerate(extra_info_val):
        if extra_info != None:
            if extra_info.isnumeric() == False:
                extra_info_val[i] = None

    return extra_info_val


def get_extra_link(perm):

    volume, issue, first_page, last_page = perm

    vol_li = f"biblio.volume:{volume}"
    iss_li = f"biblio.issue:{issue}"
    first_pg_li = f"biblio.first_page:{first_page}"
    last_pg_li = f"biblio.last_page:{last_page}"

    extra_info_val = [volume, issue, first_page, last_page]
    extra_info_link = [vol_li, iss_li, first_pg_li, last_pg_li]

    extra_link = ''
    for i, j in zip(extra_info_val, extra_info_link):
        if i != None:
            extra_link = extra_link + j + ','

    extra_link = re.sub(",$", "", extra_link)

    # If first_page greater than last_page
    if (first_page != None) and (last_page != None):
        if int(first_page) > int(last_page):
            extra_link = None

    return extra_link


def search_with_title(title):

    try:
        r = requests.get(f"https://api.openalex.org/works?search={title}&per-page=1&mailto=xx@gmail.com")
        result = r.json()["results"][0]  # "list is by default sorted in descending order of relevance_score"

    except:
        result = {}

    return result  # dict (if match found), otherwise {}


def search_with_meta(author_id, year, journal_id, extra_link):

    link = (f"https://api.openalex.org/works?filter=author.id:{author_id},publication_year:{year},primary_location.source.id:{journal_id},"
            f"{extra_link}"
            f"&per-page=1&mailto=xx@gmail.com")

    try:
        r = requests.get(link)
        result = r.json()["results"][0]
    except:
        result = {}

    return result  # dict (if match found), otherwise {}
