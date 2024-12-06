import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.request
import subprocess
import os
import serpapi
import ast

def scrape_gs(y_start, y_end):
    list_articles = []
    for start in range(0, 1000, 20):
        try:
            params = {
            "engine": "google_scholar",
            "q": "",
            "cites": "648428232262261720",
            "as_ylo": y_start,
            "as_yhi": y_end,
            "start": str(start),
            "num": 20,
            "api_key": "8bb2db4e42860236712cb3cae5ead7b916eb57e7ec1477b364eccc9ffa1f9218"
            }
            search = serpapi.search(params)
            organic_results = search["organic_results"]
            for result in organic_results:
                list_articles.append(result)
        except KeyError:
            pass
    # print(list_articles)
    # with open("test.json", "w") as f:
    with open("all_ggsch_results_" + str(y_start) + "to" + str(y_end) + ".json", "w") as f:
        f.write(str(list_articles))
        f.close()
        print("Scraping done!")

def read_json_file(y_start, y_end):
    json_file = "all_ggsch_results_" + str(y_start) + "to" + str(y_end) + ".json"
    with open(json_file) as user_file:
        file_contents = user_file.read()
    # print(file_contents)
    parsed_json = str(file_contents)
    my_dict = ast.literal_eval(parsed_json)
    return my_dict

def download_pdfs(y_start, y_end):
    number = 1
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    json_file = "all_ggsch_results_" + str(y_start) + "to" + str(y_end) + ".json"
    folder_name = "all_pdfs_" + str(y_start) + "to" + str(y_end)
    my_dict = read_json_file(y_start, y_end)
    for result in my_dict:
        try:
            for i in result["resources"]:
                # print(i["file_format"], i["link"])
                url = i["link"]
                if i["file_format"] == "PDF":
                    response_url = requests.get(url, headers=headers, stream = True)
                    file_path = folder_name + "/file_" + str(number) + ".pdf"
                    # urllib.request.urlretrieve(url, file_path)
                    if response_url.status_code == 200:
                        print(file_path)
                        with open(file_path, 'wb') as file:
                            file.write(response_url.content)
                            print('File downloaded successfully')
            number = number + 1
        except Exception as e:
            number = number + 1

def list_downloaded_pdfs(y_start, y_end):
    num = []
    folder_name = "all_pdfs_" + str(y_start) + "to" + str(y_end)
    my_dict = read_json_file(y_start, y_end)
    for i in os.listdir(folder_name):
        try:
            num.append(int(i.strip("_file.pdf")))
        except ValueError:
            pass
    list_yes = []
    for k in range(1, len(my_dict)+1, 1):
        if k in set(num):
            list_yes.append(k-1)
    file_name = "list_1.tsv"
    # file_name = "downloaded_" + str(y_start) + "to" + str(y_end) + ".tsv"
    pdfs_info(list_yes, file_name, y_start, y_end)

def list_not_downloaded_pdfs(y_start, y_end):
    num = []
    folder_name = "all_pdfs_" + str(y_start) + "to" + str(y_end)
    my_dict = read_json_file(y_start, y_end)
    for i in os.listdir(folder_name):
        try:
            num.append(int(i.strip("_file.pdf")))
        except ValueError:
            pass
    list_not = []
    for k in range(1, len(my_dict)+1, 1):
        if k not in set(num):
            list_not.append(k-1)
    file_name = "not_downloaded_" + str(y_start) + "to" + str(y_end) + ".tsv"     
    pdfs_info(list_not, file_name, y_start, y_end)

def pdfs_info(list_pdfs, file_name, y_start, y_end):
    my_dict = read_json_file(y_start, y_end)
    with open(file_name, "w") as f:
        line = str("Title \t Journal link" + "\t" + "First Author \t Last Author" + "\t" "Format" + "\t" + "PDF or HTML link" + "\t" + "Comment" + "\t" + "File name \t Year\n")
        f.write(line)
        for i in list_pdfs:
            file_name = "file_" + str(int(i)+1) + ".pdf"
            try:
                first_author = (my_dict[int(i)]["publication_info"]["summary"]).split(",")[0]
                last_author = my_dict[int(i)]["publication_info"]["authors"][-1]["name"]
            except KeyError:
                first_author = (my_dict[int(i)]["publication_info"]["summary"]).split(",")[0]
                last_author = "N/A"
            try:
                j = my_dict[int(i)]["resources"][0]
                url = j["link"]
                if j["file_format"] == "PDF":
                    line = my_dict[int(i)]["title"] + "\t" + my_dict[int(i)]["link"] + "\t" + first_author + "\t" + last_author + "\t" + j["file_format"] + "\t" + j["link"] + "\t" + "PDF download is available" + "\t" + file_name + "\t" + y_start + "-" + y_end + "\n"
                    f.write(line)
                else:
                    line = my_dict[int(i)]["title"] + "\t" + my_dict[int(i)]["link"] + "\t" + first_author + "\t" + last_author + "\t" + j["file_format"] + "\t" + j["link"] + "\t" + "Only HTML link is available" + "\t" + file_name + "\t" + y_start + "-" + y_end + "\n"
                    f.write(line)
            except Exception as e:
                title = my_dict[int(i)]["title"]
                try:
                    link = my_dict[int(i)]["link"]
                    line = title + "\t" + link + "\t" + first_author + "\t" + last_author + "\t" + "N/A" + "\t" + "N/A" + "\t" + "no PDF or HTML link available" + "\t" + file_name + "\t" + y_start + "-" + y_end + "\n"
                    f.write(line)
                except Exception as e:
                    line = title + "\t" + "no journal link" + "\t" + first_author + "\t" + last_author + "\t" + "N/A" + "\t" + "N/A" + "\t" + "no PDF or HTML link available" + "\t" + file_name + "\t" + y_start + "-" + y_end + "\n"
                    f.write(line)
        f.close()


