from scrapers import get_booklist_from_query, get_reviews_from_book

MAX_BOOK = 20
MAX_REVIEWS = 500
header = {'user-agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
          'accept-language':'en-GB,en;q=0.9',}

HOMEPAGE_AZ = "https://www.amazon.com/"

query = input("input your search for books: ")

book_names, book_links, book_plots= get_booklist_from_query(query,header=header,max_book=MAX_BOOK)

print(book_plots)