import argparse
from selenium import webdriver
from scrapfile import LICLIENT
import time



def parse_command_line_args():
    parser = argparse.ArgumentParser(description="""
        parse LinkedIn search parameters
        """)
    parser.add_argument('--username', type=str, required=True, 
        help="""
        enter LI username
        """)
    parser.add_argument('--password', type=str, required=True, 
        help="""
        enter LI password
        """)
    parser.add_argument('--jobname',nargs='*', 
        help="""
        enter search keys separated by a single space. If the keyword is more
        than one word, wrap the keyword in double quotes.
        """)

    parser.add_argument('--location',  nargs='*', 
        help="""
        enter search keys separated by a single space. If the keyword is more
        than one word, wrap the keyword in double quotes.
        """)
    
    
    parser.add_argument('--filename', type=str, nargs='?', 
        help="""
        specify a filename to which data will be written. 
        
        """)
    return vars(parser.parse_args())
if __name__ == "__main__":

    search_keys = parse_command_line_args()
    driver = webdriver.Chrome(r"chromedriver.exe")
    # Logging into LinkedIn
    driver.get("https://linkedin.com/uas/login")
    time.sleep(5)
    liclient = LICLIENT(driver,**search_keys)
    liclient.login()
    

    for jobname in search_keys["jobname"]:
        for location in search_keys["location"]:
            liclient.jobname = jobname
            liclient.location = location
            liclient.enter_search_keys()
            liclient.navigate_search_results()


    liclient.driver_quit()