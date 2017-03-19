import urllib
from urllib.request import *
import requests
from bs4 import BeautifulSoup
import os
from html.parser import HTMLParser
from urllib import parse
from urllib.request import urlopen
from urllib.parse import urljoin
import time
import pprint
from googleapiclient.discovery import build
from queue import PriorityQueue
import urllib.robotparser
from queue import PriorityQueue
import time
import mimetypes



class Queue:
    def __init__(self):
        self.queue = []
    def dequeue(self):
        return self.queue.pop(0)
    def enqueue(self,element):
        self.queue.append(element)

        

def relavant(link,keyw):
    keyword = keyw.split()
    relavant = []
    relavant_all = 0
    source_code = requests.get(link)
    source_code_string = source_code.text
    source_code_soup = BeautifulSoup(source_code_string,'lxml')
    length = len(source_code_string.split())
    
    for i in range(0,len(keyword)):
        keyword_item = keyword[i]
        a = source_code_string.count(keyword_item) * 100 / length
        relavant_all = relavant_all + a
    
    b= source_code_string.count(keyw) * 400 / length
    relavant_all = relavant_all + b
    relavant_all = float("{0:.2f}".format(relavant_all))
    return relavant_all
        
# change keyword to urllinks
def get_link_from_keyword(keyword):
    keyword_length=len(keyword)
    link="https://www.google.com/webhp?sourceid=chrome-instant&rlz=1C1EJFA_en__695__695&ion=1&espv=2&ie=UTF-8#q="
    if (keyword_length==1):
        link=link + str(keyword)
    else: 
        link=link+str(keyword[0])
        for i in range(1,keyword_length):
            link=link + "%20" + str(keyword[i])
    return link
        
def BFS_crawler(keyword, Max_page, Max_all):
    print("BFS_crawler start")
    
    # create project and files 
    link = get_link_from_keyword(keyword)
    create_project_dir("BFS/" + keyword )
    create_file('BFS/', link)
    crawled_name = "BFS/" + keyword + "/crawled.txt"
    # create crawled list and queue
    global crawled
    crawled = {link}
    global queue
    queue = Queue()
    relavant_queue = Queue()
    global harvest_rate
    harvest_rate = 0    
    global page
    page = 0
    global all_page
    all_page = 0
    all_page = all_page + 1
    print("Keyword: " + keyword)
   
    # begin_time, total_size, number of 404 errors
    begin_time = time.time()
    
    global total_size
    total_size = 0 
    global number_error
    number_error = 0
    
    
    # get google search result
    # search engine id : 002546779376930127031:tu5ldsfgyna
    # api : AIzaSyA0uahgObFqg7aYsorYdAfcmQkOU8hAG1s
    print("google result")
    service = build("customsearch", "v1",
            developerKey="AIzaSyA0uahgObFqg7aYsorYdAfcmQkOU8hAG1s")

    res = service.cse().list(
      q= keyword,
      cx='002546779376930127031:tu5ldsfgyna',
    ).execute()
    for item in res['items']:
        item_href = item['link']
        #re1 = relavant(item_href,keyword)
        queue.enqueue(item_href)
        print(item_href)
    
    # crawling each page
    while(all_page < Max_all):
        for items in queue.queue:
            if items not in crawled:
                if (all_page >= Max_all):
                    break
                #time.sleep(1)  
                try:    
                    source_code = requests.get(items)
                    source_code_string = source_code.text
                    source_code_soup = BeautifulSoup(source_code_string,'lxml')
                    localtime = time.asctime( time.localtime(time.time()) )
                    print("\n")
                    print("Crawling Page" + str(all_page) + " : " + items)
                    crawled.update({items})
                    add_content(crawled_name,items)
                    all_page = all_page + 1
                    
                    # text/html
                    try:
                        if (mimetypes.guess_type(items)[0] != 'text/html'):
                            if (str(mimetypes.guess_type(items)[0]) != 'None'):
                                print('not text/html')
                                break
                        
                    except:
                        pass
            
                    try:
                         # 404 403
                        print("getting return code")
                        a = urllib.request.urlopen(items)
                        if (a.getcode() == 404) or(a.getcode() == 403) or (a.getcode() == 400):
                            print("404 error")
                            number_error = number_error + 1
                            break  
                        print("Time: " + localtime + " Return code: " + str(a.getcode())) 
                    except:
                        break
                    try:            
                        # robot
                        rp = urllib.robotparser.RobotFileParser()
                        rp.set_url(items)
                        rp.read()
                        if not(rp.can_fetch("*", items) ):
                            print("it is robot")
                            break
                    except:
                        break
                    # relavant calculate
                    re = relavant(items,keyword)
                    relavant_queue.enqueue(re)
                    print("Relavant: " + str(re) + "% " )
                    
                    #size of page
                    print('Size of page: ' + str(len(source_code_string.split())) )
                    total_size = total_size + len(source_code_string.split())
                    # download page
                    try:
                        urlretrieve(items,'BFS/' + keyword +'/Page'+ str(all_page) + ".html")
                    except:
                        pass   
                    
                    # harvest_rate
                    harvest_rate = (harvest_rate + re )/ 2
                    harvest_rate = float("{0:.2f}".format(harvest_rate)) 
                    print('harvest_rate: ' + str(harvest_rate))
                            
                    # get new url
                    print('Getting URL ')
                    page = 0 
                    for item_link in source_code_soup.findAll("a"):
                        if(page < Max_page):
                            try:
                                item_title = item_link.string
                                item_href = item_link.get('href')
                                item_href = urljoin(items,item_href)
                                if item_href not in queue.queue:
                                    if item_href not in crawled:
                                        if item_href.find("index") == -1:
                                            if item_href.find("cgi") == -1:
                                                queue.enqueue(item_href)
                                                print(item_href)
                                                page = page + 1

                            except:
                                print("fail to get url")
                except:
                    pass 
    
    print('end of crawling')   
    end_time = time.time()
    dur = begin_time - end_time
    print('Use time:' + str(dur))
    print("\n")
    
    # harvest_rate  & size  & errors
    harvest_rate = 0
    for i in range(0,len(relavant_queue.queue)):
        harvest_rate = harvest_rate  + relavant_queue.queue[i]
    harvest_rate = float("{0:.2f}".format(harvest_rate)) / len(relavant_queue.queue)
    print('Total harvest_rate: ' + str(harvest_rate))
    print('Total page size: ' + str(total_size))
    print('Total 404 errors: ' + str(number_error))
        
# create dir & crawled.txt only to save url

def create_project_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("creating project" + directory)

def write_file(name, data):
    f = open(name, 'w')
    f.write(data)
    f.close
        
def create_file(name, keyword):
    crawled_list = name + '/crawled.txt'
    if not os.path.exists(crawled_list):
        write_file(crawled_list, '')

def add_content(name, data):
    with open(name, 'a') as f: 
        f.write(data + '\n')
    # print("finish adding")
        
def delete_content(name):
    with open(name, 'w') as f:
        pass
     

# main
BFS_crawler("duke flatbush", 10,500)

   
    
    
