import requests as rq
from bs4 import BeautifulSoup
import csv


def create_soup(url):
    page = rq.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def img_download(url, title):
    """ Download an image and save it as its title book"""
    url_img = (rq.get(url)).content
    with open(f"Imgs/{title}.jpg", 'wb') as f:
        f.write(url_img)
    print(f"Image downloaded as {title}.jpg")


def replace_multiple(incorrect, to_be_replaces, new_string):
    for element in to_be_replaces:
        if element in incorrect:
            incorrect = incorrect.replace(element, new_string)
    return incorrect


def get_information_book(url_book):
    """ Pick up information from url_book and extract information."""
    soup = create_soup(url_book)

    # pick up all information of the web site
    # pick up title
    incorrect = soup.find("h1").text
    title = replace_multiple(incorrect, [':', '/', ';', '*', '"', '>', '<', '?', "\n", '(', ')', '‽'], '')
    # pick up upc, prices, review rating, number available
    table_tags = soup.find_all("td")
    table_content = []
    for contenu in table_tags:
        table_content.append(contenu.string)
    upc = table_content[0]
    price_excluding_tax = table_content[2]
    price_excluding_tax = float(price_excluding_tax[1:])
    price_including_tax = table_content[3]
    price_including_tax = float(price_including_tax[1:])
    review_rating = int(table_content[6])
    number_available_text = table_content[5]
    number_available = int(number_available_text.replace("In stock (", "").replace(" available)", ""))
    # pick up product description
    p_tags = soup.find_all("p")
    product_description = (p_tags[3]).string
    # product_description = product_description.replace("NBSP", " ")
    # pick up image url and category
    a_tags = soup.find_all("a")
    category = (a_tags[3]).string
    img_url = soup.img.get('src')
    img_url = (img_url.replace("../..", "http://books.toscrape.com"))

    # save all information in a dictionnary
    information_product = dict()
    information_product["product_page_url"] = url_book
    information_product["upc"] = upc
    information_product["title"] = title
    information_product["price_including_tax"] = price_including_tax
    information_product["price_excluding_tax"] = price_excluding_tax
    information_product["number_available"] = number_available
    information_product['product_description'] = product_description
    information_product['category'] = category
    information_product['review_rating'] = review_rating
    information_product["img_url"] = img_url
    img_download(img_url, title)
    return information_product


def create_file_csv(filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'img_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def save_file_csv(filename, dicttosave):
    """ Save in filename.csv a dictionnary named dicttosave"""
    with open(filename, 'a', encoding='utf-8') as csvfile:
        fieldnames = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax',
                      'number_available', 'product_description', 'category', 'review_rating', 'img_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(dicttosave)


def get_all_pages(category_url):
    """ Return a list of all pages for one category"""
    url_list_in_one_category = [category_url]
    link_page = category_url
    print(str(link_page))
    while link_page:  # we iterate while link_page is defined
        soup = create_soup(link_page)
        soup_next_url = soup.select_one(".next > a")
        print(str(soup_next_url) + " = next")
        if soup_next_url:
            link_page = f'{category_url.replace("index.html","")}{soup_next_url.get("href")}'  # other f-string
            print(str(link_page) + " = link_page")
            url_list_in_one_category.append(link_page)
        else:
            link_page = ""
            print(str(link_page) + " = link_page")
    print(str(url_list_in_one_category) + " = url_list_in_one_category")
    return url_list_in_one_category


def get_urls_books(category_url):
    """ Return a list of url of all the books for url_category"""
    url_page_of_category = get_all_pages(category_url)
    url_list_book = []
    for url in url_page_of_category:
        soup = create_soup(url)
        list_img = soup.find_all("img", class_="thumbnail")
        for img in list_img:
            parent_tag = img.parent
            if parent_tag.name == "a":
                book_url = parent_tag.get('href')
                book_url = book_url[9:]  # remove ../../../
                book_url = f"http://books.toscrape.com/catalogue/{book_url}"  # f-string
                url_list_book.append(book_url)
    return url_list_book


def get_url_category():  # executed once, first time
    """ Return a list of all url category of the site http://books.toscrape.com/"""
    soup = create_soup('http://books.toscrape.com/')
    sidebar_category = soup.find("div", class_="side_categories")
    links_url_category = sidebar_category.find_all("a")
    categories_url_name = []
    for link in links_url_category:
        category_name = replace_multiple(link.string, [':', '/', ';', '*', '"', '>', '<', '?', "\n", '‽', ' '], '')
        url_and_name = (f"http://books.toscrape.com/{link.get('href')}", category_name)  # Warning ! Tuple !, f-string
        categories_url_name.append(url_and_name)
    del categories_url_name[0]  # delete Books category in (url, name) list
    return categories_url_name


def save_informations_all_books(categories_url_name):
    """ For each url_category, save all information book in one file for one category"""
    # return list of url for each book of the category
    categories_url_name = categories_url_name
    for item in categories_url_name:  # Warning ! item is a tuple !!
        print(str(item[0]) + " = item[0]")
        urls_books = get_urls_books(item[0])
        # go to get_url_book function, with item[0] = category_url save all books urls in an array
        category = item[1]  # find category name in item tuple
        # return a list of all dictionary of information for one book
        list_informations_books = []
        for url in urls_books:
            info_book = get_information_book(url)
            list_informations_books.append(info_book)
        category = f"CSV/{category}.csv"  # f-string
        create_file_csv(category)
        for book in list_informations_books:
            save_file_csv(category, book)


def scraper():
    """ Scrapping of the site "https://books.toscrape.com :
        - get all url of categories of the site,
        - get all url of all books for each category
        - scrap each book and save in file.csv : product_page_url, upc, title, price_including_tax,
        price_excluding tax, number available, product_description, category, review_rating,
        img_url
        - download image for each book.
        At the end of the scrapping, you must have 2 new directories named "CSV/" and "Imgs/"
        "CSV/" contents one file.csv for each category and all images.
        """
    categories_url_name = get_url_category()
    save_informations_all_books(categories_url_name)
