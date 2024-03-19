import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import re


custom_header = {'user-agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                'accept-language':'en-GB,en;q=0.9',}

MAX_BOOK = 250

MAX_REVIEWS = 500

HOMEPAGE_AZ = "https://www.amazon.com/"


# Define a function to fetch and parse HTML content of a given URL
def get_soup_from_url(url, header):
    """
        Fetches the HTML content of a webpage and parses it into a BeautifulSoup object.
        Parameters:
            url (str): The URL of the webpage to fetch.
            header (dict): HTTP headers to use for the request.
        Returns:
            BeautifulSoup: A BeautifulSoup object containing the parsed HTML of the page.
    """

    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text,"html.parser")

    return soup

    
     
    

def get_bookname_from_tag(booktag):
    return booktag.find(name="span",class_="a-size-medium a-color-base a-text-normal").getText()

def get_booklink_from_tag(booktag):
    return HOMEPAGE_AZ + booktag.find(name="a",class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal").get("href")


def get_plot_summary_from_tag(booktag,header):
    link = get_booklink_from_tag(booktag)
    soup = get_soup_from_url(link,header)

    plot_summary = soup.find(name="div",id="bookDescription_feature_div").getText().strip("\n")

    return plot_summary
    



def get_booklist_from_query(query,header,max_book):

    #Construct full url with user input query
    query_full = HOMEPAGE_AZ + "s?k=" + "+".join(query.split(" ")) + "&i=stripbooks" #restrict search to only books
    book_tags = []

    page_no = 1

    keep_scraping = True
    # Collect book tags from Amazon pages until reaching MAX_BOOK
    while keep_scraping:

        url_page = query_full + "&page=" + str(page_no)

        print(url_page)
        soup = get_soup_from_url(url_page, header)

        soup_tags = soup.find_all(name="h2",class_="a-size-mini a-spacing-none a-color-base s-line-clamp-2")

        for book_tag in soup_tags:
            book_tags.append(book_tag)
            if len(book_tags) == max_book:
                keep_scraping = False
                break
        

        print(len(book_tags))
        
        page_no+=1

        time.sleep(1)
    
    book_names = []
    book_links = []
    book_plots = []

    for booktag in book_tags:
        book_names.append(get_bookname_from_tag(booktag))
        book_links.append(get_booklink_from_tag(booktag))
        book_plots.append(get_plot_summary_from_tag(booktag,header=header))


    return (book_names,book_links,book_plots)

    



def pagerize_review_url(review_link_raw):

    pattern = r".*product-reviews/[A-Z\d]+"

    #grab part of url up until product number, to be later appended with page number for navigation
    match = re.search(pattern, review_link_raw)

    # Extract the matched part
    if match:
        matched_part = match.group(0)
    else:
        raise ValueError("No match found!")

    

    return matched_part



def get_review_features_from_review(review_tag):
    review_title = review_tag.select(selector="a.a-size-base.a-link-normal.review-title.a-color-base.review-title-content.a-text-bold span")[2].getText().strip("\n")
    review_rating = float(review_tag.find(name="span",class_="a-icon-alt").getText().split(" ")[0])
    review_content = review_tag.find(name="div",class_="a-row a-spacing-small review-data").getText().strip("\n")

    return (review_title,review_rating,review_content)
    

def get_reviews_from_book(booklink,custom_header,max_reviews=MAX_REVIEWS):
    
    soup_book = get_soup_from_url(booklink,custom_header)

    #get plot summary from book's main page
    #plot_summary = soup_book.find(name="div",id="bookDescription_feature_div").getText().strip("\n")
    # get plot summary from book's main page
    plot_summary = soup_book.find(name="div", id="bookDescription_feature_div").getText().strip("\n")
    book_name = soup_book.find(name="span", id="productTitle").getText().strip("\n")

    #number of reviews available on page
    print("globalratings")
    n_global_ratings = int(soup_book.find(name="span", id="acrCustomerReviewText").getText().split(" ")[0].replace(",",""))
    print(n_global_ratings)

    #get link for 'all_reviews' for the book chose
    link_all_reviews = HOMEPAGE_AZ + soup_book.find(name="a",class_="a-link-emphasis a-text-bold").get("href")


    #reconstruct review url to incorporate page number, allowing for page navigation
    link_review_paged = pagerize_review_url(link_all_reviews)

    

    #initialize page number
    page_no = 1

    keep_scraping = True

    reviews = []

    while keep_scraping:
        #construc review link the page to scrape from
        link_review_current = link_review_paged + "/ref=cm_cr_getr_d_paging_btm_next_" + str(page_no) + "?pageNumber=" + str(page_no)
        print(link_review_current)

        #get soup object from review link
        soup_all_reviews = get_soup_from_url(link_review_current,custom_header)

        #retrieve all review tags on current page
        review_tags = soup_all_reviews.find_all(name="div",class_="a-section celwidget")
        print(len(review_tags))

        if len(review_tags)==0:
            break


        #keep adding to `reviews` list until it hits maximum or when the current page is not available
        for review_tag in review_tags:

            review_title,review_rating,review_content = get_review_features_from_review(review_tag)

            reviews.append(
                {
                "book_name": book_name,
                "plot_summary": plot_summary,
                "review_title":review_title,
                "review_rating":review_rating,
                "review_content":review_content
                }
            )

            if len(reviews) == max_reviews:
                keep_scraping = False
                break

        #increment the page number
        page_no+=1

        print(len(reviews))

        time.sleep(1)



    return (plot_summary,pd.DataFrame(reviews))
        

    