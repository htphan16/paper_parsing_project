from scrape_gs_serpapi import *
from sys import argv

def main(function, y_start, y_end):
    if argv[1] == "scrape_gs":
        function = scrape_gs
    elif argv[1] == "download_pdfs":
        function = download_pdfs
    elif argv[1] == "list_downloaded_pdfs":
        function = list_downloaded_pdfs
    elif argv[1] == "list_not_downloaded_pdfs":
        function = list_downloaded_pdfs
    print(function(argv[2], argv[3]))

if __name__ == '__main__':
    main(argv[1], argv[2], argv[3])
    # try:
    #     main(argv[1], argv[2], argv[3])
    # except TypeError:
    #     print("Please enter the available function names: scrape_gs, download_pdfs, list_not_downloaded_pdfs, list_downloaded_pdfs\n") 