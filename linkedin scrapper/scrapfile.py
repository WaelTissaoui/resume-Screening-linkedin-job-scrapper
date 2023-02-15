from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.common.keys import Keys
# pip install xml 
TAG_RE = re.compile(r'<[^>]+>')
import json
# Creating an instance
#Options = webdriver.ChromeOptions()
#Options.add_argument('headless')
#driver = webdriver.Chrome(r"C:\Users\TUNEZ-1\Desktop\rec resume project\Scrap\chromedriver",options = Options)
  

  




  
#driver.get(profile_url)        # this will open the link


def remove_tags(text):
    """ remove tags from text using regex module"""
    return TAG_RE.sub('', text)

def xpath_soup(element):
    """ get xpath from beautifull soup element"""
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def get_page_src(driver):
    try :
        src = driver.page_source
        soup = BeautifulSoup(src,'lxml')
    except Exception as e :
        print("soup error")
        print(e)
    print("this is get page src soup ")
    return soup

def refresh_src(driver):
    driver.refresh()
    return get_page_src(driver)

def scroll_down_wait_for_element(driver,element):
    attempts=1
    
    while(True):
        try :
            print("checking element")
            #driver.execute_script ("window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);")
            html = driver.find_element(By.TAG_NAME,'html')
            html.send_keys(Keys.END)
            soup = get_page_src(driver)

            if element == "job":
                print("checking job")
                check_e = xpath_soup(soup.find("div",{"class":"jobs-box__html-content jobs-description-content__text t-14 t-normal jobs-description-content__text--stretch"}))
                WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,check_e)))
            else:
                print("checking buttons")
                #check_e = xpath_soup(soup.find("ul",{"class":"artdeco-pagination__pages artdeco-pagination__pages--number"}))
                check_e = xpath_soup(soup.find("li",{"class":"artdeco-pagination__indicator artdeco-pagination__indicator--number active selected ember-view"}))
                WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,check_e)))
            

        except Exception as e :
            attempts +=1
            print("failed to locate element",attempts)
            time.sleep(0.5)
            if attempts > 100:
                print("failed to locate element")
                break
        else:
            print("\n \n element located succefully")
            break
            
    return soup 

def find_job_links(driver,current_page,lastpage):
    # there is 25 job offer per page
    # last page can have less than 25
    job_class = "disabled ember-view job-card-container__link job-card-list__title"
    while(True):
        soup = scroll_down_wait_for_element(driver,"buttons")
        links = soup.find_all("a", {"class":job_class})
        number_of_jobs = soup.find("small",{"class":"jobs-search-results-list__text display-flex t-12 t-black--light t-normal"}).get_text()
        number_of_jobs = [int(x) for x in number_of_jobs.split() if x.isdigit()]
        print(len(links))
        if (len(links)==25 and current_page < lastpage) or (len(links) == ( number_of_jobs[0] -  25*(lastpage-1) )  and current_page == lastpage):
            print("all links are available",current_page,lastpage,len(links))
            break
        else:
            driver.refresh()
            time.sleep(5)
            scroll_down_wait_for_element(driver,"buttons")
    
        
    print(number_of_jobs)
    
    



        
    return links

def find_pages(driver):
    page_class= "artdeco-pagination__indicator artdeco-pagination__indicator--number ember-view"
    soup = scroll_down_wait_for_element(driver,"buttons")
    buttons = soup.find_all("li",{"class":page_class})
    active_button = soup.find("li",{"class":"artdeco-pagination__indicator artdeco-pagination__indicator--number active selected ember-view"})#first button has different class 
    buttons =[xpath_soup(active_button)]+[xpath_soup(B) for B in buttons]
    return buttons
    
def find_search_box(driver):
    pass

def scrabpage(driver,jobs):
    L = []
    for j in jobs:
        one_link ='https://www.linkedin.com'+j['href']
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(one_link)
        data = scrabjob(driver)
        L.append(data)
        driver.close() 
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[0])
    return L     
        
def scrabjob(driver):
    data = {}
    soup = scroll_down_wait_for_element(driver,"job")
    company = soup.find("div",{"class":"jobs-unified-top-card__primary-description"}).get_text()
    description = soup.find_all("div", {"class":"jobs-box__html-content jobs-description-content__text t-14 t-normal jobs-description-content__text--stretch"})

    data["title"]  = soup.find("h1",{"class":"t-24 t-bold jobs-unified-top-card__job-title"}).get_text()
    data["company"] = ' '.join(company.split()[0:5])
    data["description"] = remove_tags(str(description))
    print(data["description"])
    

    return data

def save_data_file(filename,data):
    with open(filename,"a+",encoding="utf-8") as f :
        json.dump(data,f,ensure_ascii=False,indent=2)

def wait_for_search(driver):
    attempts = 1 
    job_search_xpath = "/html/body/div[6]/header/div/div/div/div[2]/div[2]/div/div/input[1]"
    location_search_xpath = "/html/body/div[6]/header/div/div/div/div[2]/div[3]/div/div/input[1]"
    while(True):
        try:
            print("waiting for search and location")
            WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,job_search_xpath)))
            time.sleep(1)
            WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,location_search_xpath)))
            

        except Exception as e :
            attempts += 1 
            print("search and location not found attempts N°",attempts)
            time.sleep(1)
            if attempts>100:
                print("search and location not found / failed ")
        

        else:
            print("search and location has found succefully ")
            page_jobname = driver.find_element(By.XPATH,job_search_xpath)
            page_location =driver.find_element(By.XPATH,location_search_xpath)
            break

    return page_jobname,page_location



        

           
            
"""
   1 - iterates over number of buttons (number of pages to scrab)
   2 - extract all links from the webpage
   3 - open every job offer link in a new tab , extract information , close it  
   
"""



class LICLIENT(object):
    def __init__(self,driver,**kwargs):
        self.driver         =  driver
        self.username       =  kwargs["username"]
        self.password       =  kwargs["password"]
        self.filename       =  kwargs["filename"]
        self.jobname        =  kwargs["jobname"]
        self.location       =  kwargs["location"]
    
    def driver_quit(self):
        self.driver.quit()
    
    def login(self):
        username = self.driver.find_element("id","username")
        username.send_keys(self.username)  # Enter Your Email Address
        pwd = self.driver.find_element("id","password")
        pwd.send_keys(self.password) 
        self.driver.find_element("xpath","//button[@type='submit']").click()
        print("login succefully")

    def navigate_search_results(self):
        """
        scrape postings for all pages in search results
        """
        print("now i'm searching the specified job and location")
        buttons = find_pages(self.driver)
        print(buttons)
        i = 0
        for B in buttons:
            button=self.driver.find_element(By.XPATH,B+"/button")
            button.click()
            i+=1
            print("scrapinng page \n")
            jobs = find_job_links(self.driver,i,len(buttons))

            save_data_file(self.filename,scrabpage(self.driver,jobs))
            
        print(buttons)
    
    def enter_search_keys(self):
        self.driver.get("https://www.linkedin.com/jobs/")
        page_jobname,page_location = wait_for_search(self.driver)
        page_jobname.send_keys(self.jobname)
        time.sleep(1)
        page_location.send_keys(self.location)
        time.sleep(1)
        page_location.send_keys(Keys.ENTER)





