import selenium
from selenium import webdriver # used to open chromedriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options # options for chromedriver
from selenium.webdriver.common.by import By # used to find element/elements by XPATH, CLASS_NAME, TAG_NAME,...
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # sets conditions on elements of a page
# from selenium.webdriver.common.keys import Keys

import os # working with paths
import time # calculates running time
import json # saving, loading
import ast # converts string representation of lists to list
import pandas as pd # processes tables


# Hyperparameters
PRODUCTS_PER_CATEGORY = 100 # For example, 100
COMMENTS_STARS_PER_PRODUCT = 10 # For example, 10
DRIVER_PATH = './chromedriver' # for using local chromedriver

# class MasterCrawler():
#     def __init__(self, headless) -> None:
#         self.category = CategoryCrawler(headless_option=headless)
#         self.product = ProductCrawler(headless_option=headless)
#         self.comment_star = CommentStarCrawler(headless_option=headless)
    
#     def run(self):
#         start = time.time()
#         print('RUNNING CategoryCrawler')
#         self.category.get_categories()
#         end = time.time()
#         print('Time: {} minutes'.format((end - start) / 60))

#         start = time.time()
#         print('RUNNING ProductCrawler')
#         self.product.get_products()
#         end = time.time()
#         print('Time: {} minutes'.format((end - start) / 60))

#         start = time.time()
#         print('RUNNING CommentStarCrawler')
#         self.comment_star.get_stars_comments()
#         end = time.time()
#         print('Time: {} minutes'.format((end - start) / 60))

class CategoryCrawler():
    """
        Collecting URLs of categories from the Shopee homepage. Saving them for later uses.
    """
    MAX_WAITING_TIME = 30 # seconds
    categories_urls_dict = {} # contains URLs of categories

    def __init__(self, home_page, headless_option=True) -> None:
        """
            Initializing CategoryCrawler.
            Args:
                home_page (str): Homepage URL.
                headless_option (bool): True if you want to implicitly run chromedriver, otherwise the 
                chromedriver's GUI is displayed.
        """
        self.home_page = home_page
        self.headless_option = headless_option
        self.__categories_real_names = [] # private attribute, can't be accessed outside the class
        self.succeeded = False # checks whether loading a page is succeeded
    
    @property # prevents from accessing outside the class
    def categories_real_names(self):
        return self.__categories_real_names

    def __load_page(self, driver_options):
        """
            Loading the home page.
            Args:
                driver_options (Option): Options for chromedriver.
        """
        self.driver = webdriver.Chrome(options=driver_options, executable_path=DRIVER_PATH) # initialize a driver controlling Chrome
        self.driver.set_page_load_timeout(CategoryCrawler.MAX_WAITING_TIME) # timeout for loading a page
        self.driver.get(self.home_page) # opens the URL (home page)

    def __scroll_down(self):
        """
            Scrolling down one time (like pressing PAGE DOWN key once).
        """
        scroll_script = "window.scrollBy(0, 1000);"
        self.driver.execute_script(scroll_script)
    
    def __close_popup(self):
        """
            Closing the pop-up appearing when loading a new home page.
        """
        try:
            notification_xpath = '//*[@id="stardust-popover1"]/div'
            # Wait until the 'Thông Báo' button is loaded
            WebDriverWait(self.driver, CategoryCrawler.MAX_WAITING_TIME).until(EC.element_to_be_clickable((By.XPATH, notification_xpath)))

            close_button_script = 'return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")'
            popup_close_button = self.driver.execute_script(close_button_script)
            popup_close_button.click()
            print('Close pop-up successfully.')
        except Exception as e:
            print(f'Exception "{e}" occurs when trying to click the pop-up close button. Program stopped!')
            

    def __find_categories_names(self):
        """
            Finding names (text) of categories, adding them to __categories_real_names
        """
        categories_names_xpath = "//div[@class='section-category-list']//li/div/a/div/div[2]/div"
        categories_names = self.driver.find_elements(by=By.XPATH, value=categories_names_xpath)
        for name in categories_names:
            if name.text:
                self.__categories_real_names.append(name.text)
        
        categories_right_button_xpath = "//div[@class='section-category-list']//div[3]"
        categories_right_button = self.driver.find_element(by=By.XPATH, value=categories_right_button_xpath)
        if categories_right_button.is_displayed():
            categories_right_button.click()
            time.sleep(3) # sleeping for 3 seconds, waiting for elements to be loaded
            categories_names = self.driver.find_elements(by=By.XPATH, value=categories_names_xpath)
            for name in categories_names:
                if name.text and (name.text not in self.__categories_real_names):
                    self.__categories_real_names.append(name.text)
        
        

    def __find_categories_urls(self):
        """
            Finding URLS of categories, adding them to categories_urls_dict
        """
        categories_urls_xpath = "//div[@class='section-category-list']//li/div/a"
        categories_urls = self.driver.find_elements(by=By.XPATH, value=categories_urls_xpath)
        for category_name, category_url in zip(self.__categories_real_names, categories_urls):
            CategoryCrawler.categories_urls_dict[category_name] = category_url.get_attribute('href')

    def __save(self, filename):
        """
            Saving categories_urls_dict to url_files directory.
            Args:
                filename (str): Name of the file.
        """
        saving_path = os.path.join(os.getcwd(), 'url_files', filename)
        with open(saving_path, 'w') as f:
            f.write(json.dumps(CategoryCrawler.categories_urls_dict))
        

    def get_categories(self):
        """
            Getting URLs of categories, then saving them to categories_urls_dict
        """
        print('CategoryCrawler IS GETTING CATEGORIES... ')
        options = Options()
        options.headless = self.headless_option # change that to True in production, the chrome driver will run implicitly and be less error-prone
        options.add_argument("--window-size=1920,1200")
        try:
            self.__load_page(driver_options=options)

            # Try closing the popup
            self.__close_popup()

            # Scrolling down 
            self.__scroll_down()
            time.sleep(5) # sleeping for 5 seconds

            # Find all names of categories
            self.__find_categories_names()
        
            # Find urls of all categories from the home page. Prepare for other crawlers
            self.__find_categories_urls()
            
            self.__save(filename='categories_urls.json')

            print('CategoryCrawler DONE!')
            self.succeeded = True

        except Exception as e:
            print(f'Exception "{e}" occurs when getting categories.')
            raise
        finally:
            self.driver.quit() # Closing the Chrome window

    def load_urls(self, filename):
        """
            Loading a JSON file to see what's inside.
        """
        path = os.path.join(os.getcwd(), 'url_files', filename)
        with open(path) as f:
            categories_urls = json.load(f)
        return categories_urls



class ProductCrawler():
    """
        Grabbing URLs of products of each category due to the limit PRODUCTS_PER_CATEGORY
    """
    MAX_WAITING_TIME = 10 # seconds
    
    def __init__(self, headless_option=True) -> None:
        """
            Initializing ProductCrawler.
            Args:
                headless_option (bool): True if you want to implicitly run chromedriver, otherwise the 
                chromedriver's GUI is displayed.
        """
        self.headless_option = headless_option
        self.product_urls = {} # contains URLs of products, saved to url_files directory
    
    def __load_urls_from_json(self, filename):
        """
            Loading categories URLS from file.
            Args:
                filename (str): Name of a file
        """
        path = os.path.join(os.getcwd(), 'url_files', filename)
        with open(path) as f:
            self.urls = json.load(f) # self.urls contains URLs of categories loaded from file

    def __load_page(self, url, driver_options):
        """
            Loading a URL of a product.
            Args:
                url (str): URL of a product.
                driver_options (Option): options setting for the driver instance.
        """
        self.driver = webdriver.Chrome(options=driver_options, executable_path=DRIVER_PATH) # initialize a driver instance
        self.driver.set_page_load_timeout(ProductCrawler.MAX_WAITING_TIME) # if timeout is exceeded, the page loading is failed.
        self.driver.get(url) # opens a URL
    
            

    def __scroll_down(self, n_times=10):
        """
            Scrolling down to the bottom of a page.
            Args:
                n_times (int): Number of times to scroll down.
        """
        for _ in range(n_times):
            scroll_script = "window.scrollBy(0, 1000);"
            self.driver.execute_script(scroll_script)
            time.sleep(0.1) # wait some time to load elements

    def __find_products_urls(self):
        """
            Finding URLs of products with the limit PRODUCTS_PER_CATEGORY.
            Returns:
                urls (list): URLs of products of each category.
        """
        self.__scroll_down()

        products_xpath = "//div[@class='row shopee-search-item-result__items']/div/a"
        urls = [] # consists of URLs of products from each category

        while len(urls) < PRODUCTS_PER_CATEGORY:
            products = self.driver.find_elements(by=By.XPATH, value=products_xpath)
            for product in products:
                urls.append(product.get_attribute('href'))
                if len(urls) == PRODUCTS_PER_CATEGORY:
                    break
            self.__click_next_button()
            self.__scroll_down()
            
        return urls


    def __click_next_button(self):
        """
            Clicking the next button of a products page.
        """
        try:
            next_button_xpath = "//button[@class='shopee-icon-button shopee-icon-button--right ']"
            next_button = self.driver.find_element(by=By.XPATH, value=next_button_xpath)
            next_button.click()
        except Exception as e:
            print(f'Exception "{e}" occurs while trying to click the next button.')


    def __save(self, df, filename):
        """
            Saving URLs of products per category to a file.
            Args:
                df (pd.DataFrame): Products per category, columns = ['category_name', 'products'].
                filename (str): Name of a file.
        """
        saving_path = os.path.join(os.getcwd(), 'url_files', filename) # saved to url_files directory
        df.to_csv(saving_path, index=False) # save file, take away the index of the dataframe

    def __load_log_timeout(self, log_file):
        """
            Loading log_timeout.json file only if this file is not empty.
            Args:
                log_file (str): The JSON log file.
            Returns:
                logs (dict): A dictionary including failed-to-load URLs.
        """
        path = os.path.join(os.getcwd(), 'logs', log_file)
        with open(path) as f:
            logs = json.load(f)
        return logs
    
    def __save_log_timeout(self, logs, log_file):
        """
            Saving the log file named log_timeout.json
            Args:
                logs (dict): A new logs including new failed-to-load URLs.
                log_file (str): Name of the log file.
        """
        saving_path = os.path.join(os.getcwd(), 'logs', log_file)
        with open(saving_path, 'w') as f:
            f.write(json.dumps(logs))

    def __run_logs(self, driver_options):
        """
            Running the log file after iterating over all URLs of products.
            Args:
                driver_options (Option): Options for setting up driver. 
        """
        logs = self.__load_log_timeout(log_file='log_timeout.json')
        new_logs = {} # contains all URLs that failed to load when running the log file.
        for category_name, url in logs.items():
            try:
                # Loading a url
                self.__load_page(url, driver_options=driver_options)
            except selenium.common.exceptions.TimeoutException:
                print('Timeout Exception occurs.')
                new_logs[category_name] = url
                self.driver.quit() # closes the driver window
                continue

            # Get all urls of products
            urls = self.__find_products_urls()
            self.product_urls[category_name] = urls # Add found urls to dictionary product_urls

        self.__save_log_timeout(new_logs, log_file='log_timeout.json')
        


    def get_products(self):
        """
            Getting all URLs of products.
        """
        options = Options()
        options.headless = self.headless_option # change that to True in production, the chrome driver will run implicitly and be less error-prone
        options.add_argument("--window-size=1920,1200") # modify window size of the driver

        try:
            print('ProductCrawler IS STARTING TO GET PRODUCTS...')
            self.__load_urls_from_json(filename='categories_urls.json')
            self.product_urls = self.urls # assign URLs of all categories (self.urls) to self.product_urls (to contain products URLs)
            df = pd.DataFrame(self.product_urls.keys(), columns=['category_name']) # create a dataframe consisting of category_name column
            logs = {} # create a new logs to save faied URLs when loading a page
            for category_name, url in self.urls.items(): # categories URLs
                try:
                    # Loading a url
                    self.__load_page(url, driver_options=options)
                except selenium.common.exceptions.TimeoutException:
                    print('Timeout Exception occurs.')
                    logs[category_name] = url
                    self.driver.quit()
                    continue

                # Get all urls of products
                urls = self.__find_products_urls()
                self.product_urls[category_name] = urls # override categories URLs to products URLs found above
            self.__save_log_timeout(logs, log_file='log_timeout.json')
            
            # Dealing with Timeout Exception
            while True:
                logs = self.__load_log_timeout(log_file='log_timeout.json')
                if logs: # if logs is not empty
                    print('Running log file.')
                    self.__run_logs(driver_options=options)
                else:
                    break


            df['products'] = self.product_urls.values() # save products URLs
            self.__save(df, filename='products_per_category.csv')

            print('GETTING PRODUCTS, DONE!')


        except Exception as e:
            print(f'Exception "{e}" occurs during the products scraping process.')
            raise
        finally:
            self.driver.quit() # closes the driver window



class CommentStarCrawler():
    """
        Scraping comments, stars in the comment section (if any). Only taking the comment and
        star that are both exist.
    """
    MAX_WAITING_TIME = 10

    def __init__(self, headless_option) -> None:
        """
            Initializing CommentStarCrawler.
            Args:
                headless_option (bool): True if you want the window to be hidden when the driver 
                is running, otherwise the driver window will be opened.
        """
        self.headless_option = headless_option
        self.comments = [] # a place for comments
        self.stars = [] # a place for stars

    def __load_products_list_from_dataframe(self, filename):
        """
            Loading a list of products URLs from a dataframe.
            Args:
                filename (str): Name of a file.
        """
        path = os.path.join(os.getcwd(), 'url_files', filename)
        df = pd.read_csv(path)
        df['products_list'] = df['products'].apply(lambda x: ast.literal_eval(x)) # convert string representation of lists to list
        return df
    
    def __scroll_down(self, n_times=10):
        """
            Scrolling down to the bottom of a page.
            Args:
                n_times (int): The number of times to scroll down.
        """
        for _ in range(n_times):
            scroll_script = "window.scrollBy(0, 1000);"
            self.driver.execute_script(scroll_script)
            # time.sleep(0.1)

    def __find_login(self):
        """
            Finding the login button
        """
        login_xpath = "//button[contains(text(),'Đăng nhập')]"
        try:
            login = self.driver.find_element(by=By.XPATH, value=login_xpath)
        except:
            login = False
        return login


    def __load_page(self, url, driver_options):
        """
            Loading a URL.
            Args:
                url (str): The URL to be loaded.
                driver_options (Option): Options for setting up the driver.
            Returns:
                True if there is no login button, False otherwise
        """
        self.driver = webdriver.Chrome(options=driver_options, executable_path=DRIVER_PATH) # initialize a driver
        self.driver.set_page_load_timeout(CommentStarCrawler.MAX_WAITING_TIME) # timeout when loading a URL
        try:
            self.driver.get(url) # open the URL
            time.sleep(1) # sleep for 1 second
            login = self.__find_login()
            if login:
                print('The URL needs to be logged in, skipping this URL.')
                return False
        except selenium.common.exceptions.InvalidArgumentException:
            print(url)
            raise
            
        return True

    def __click_next_button(self):
        """
            Clicking the next button.
        """
        try:
            next_button_xpath = "//button[@class='shopee-icon-button shopee-icon-button--right ']"
            # Find the button
            self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, next_button_xpath))))
            # next_button = self.driver.find_element(by=By.XPATH, value=next_button_xpath)
            # next_button.click()
        except Exception as e:
            print(f'Exception "{e}" occurs while trying to click the next button.')
            # print('URL causes this Exception:', self.driver.current_url)
            self.log_urls.append(self.driver.current_url) # add error URLs to log

    def __has_comment_section(self):
        """
            Check if there is a comment section of product URL.
            Returns:
                True if existed, otherwise False.
        """
        try:
            no_comments_xpath = "//div[@class='product-ratings-comments-view__no-data']"
            no_comments = self.driver(by=By.XPATH, value=no_comments_xpath)
            if no_comments.get_attribute('class') == 'product-ratings-comments-view__no-data':
                return False # there is no comment section
        except:
            # print('There are ratings in this page.')
            return True

    def __is_comment_existed(self, section):
        """
            Check if there exists a comment or not
            Args:
                True if a comment exists, False otherwise.
        """
        try:
            section.find_element(by=By.CLASS_NAME, value="_280jKz").find_elements(by=By.TAG_NAME, value='div')[-1]
            return True
        except:
            return False

    def __find_comments_stars(self):
        """
            Grabbing comments and stars.
        """
        self.__scroll_down(n_times=20) # scrolling 20 times
        if not self.__has_comment_section():
            print('There are no ratings in this page.')
            self.driver.quit() # closes the driver window.
            return # do nothing when there is no ratings.

        sections_xpath = "//body/div[@id='main']/div/div/div[@class='_3iHv4f']/div/div[@class='page-product']/div[@role='main']/div[@class='CKGyuW']/div[@class='page-product__content']/div[@class='page-product__content--left']/div/div[@class='product-ratings']/div[@class='product-ratings__list']/div[@class='shopee-product-comment-list']/div/div"
        sections = self.driver.find_elements(by=By.XPATH, value=sections_xpath) # find sections
        for section in sections:
            count_stars = 0
            if self.__is_comment_existed(section):
                comment = section.find_element(by=By.CLASS_NAME, value="_280jKz").find_elements(by=By.TAG_NAME, value='div')[-1].text
                self.comments.append(comment)
                stars = section.find_element(by=By.CLASS_NAME, value="repeat-purchase-con").find_element(by=By.TAG_NAME, value='div').find_elements(by=By.TAG_NAME, value='svg')
                for star in stars:
                    if star.get_attribute('class') == 'shopee-svg-icon icon-rating-solid--active icon-rating-solid':
                        count_stars += 1
                self.stars.append(count_stars) # add stars to a list
        
        # Print to stdout
        print('comments:', len(self.comments))
        print('stars:', len(self.stars))

        self.__click_next_button()
        self.__scroll_down()
        

    def __save(self, filename):
        """
            Putting comments, stars to a dataframe and saving to data directory.
            Args:
                filename (str): Name of a file.
        """
        path = os.path.join(os.getcwd(), 'data', filename)
        data = {'comments': self.comments, 'stars': self.stars}
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)

    def __save_log_urls(self, urls, filename):
        """
            Saving the log file containing failed URLs.
            Args:
                urls (list): A list of failed URLs.
                filename (str): Name of a file.
        """
        path = os.path.join(os.getcwd(), 'logs', filename)
        with open(path, 'w') as f:
            f.write(' '.join(urls))

    def __load_log_urls(self, filename):
        """
            Loading the log file containing failed URLs.
            Args:
                filename (str): Name of a file.
            Returns:
                urls (list): A list of failed URLs.
        """
        path = os.path.join(os.getcwd(), 'logs', filename)
        with open(path, 'r') as f:
            urls = f.read().split()
        return urls
    
    def __run_logs(self, driver_options):
        """
            Running the log file.
            Args:
                driver_options (Option): Options for setting up the driver.
        """
        logs = self.__load_log_urls(filename='log_timeout.txt')
        new_logs = [] # consists of failed URLs.
        for url in logs:
            try:
                # Loading a url
                succeeded = self.__load_page(url, driver_options=driver_options)
                if not succeeded:
                    self.driver.quit() # closes the driver window.
                    continue
            except selenium.common.exceptions.TimeoutException:
                print('Timeout Exception occurs.')
                new_logs.append(url)
                self.driver.quit() # closes the driver window.
                continue

            self.__find_comments_stars()

        self.__save_log_urls(new_logs, filename='log_timeout.txt')


    def get_stars_comments(self):
        """
            Getting comments and stars.
        """
        options = Options()
        options.headless = self.headless_option # change that to True in production, the chrome driver will run implicitly and be less error-prone
        options.add_argument("--window-size=1920,1200")
        print('CommentStarCrawler IS GETTING STARS AND COMMENTS')

        df = self.__load_products_list_from_dataframe(filename='products_per_category.csv')
        self.log_urls = []
        for urls in df.loc[:, 'products_list']:
            for url in urls:
                try:
                    # Loading a url
                    succeeded = self.__load_page(url, driver_options=options)
                    if not succeeded:
                        self.driver.quit()
                        continue
                except selenium.common.exceptions.TimeoutException:
                    print('Timeout Exception occurs.')
                    self.log_urls.append(url)
                    self.driver.quit()
                    continue

                self.__find_comments_stars()

            # Handling timeout exception
            self.__save_log_urls(self.log_urls, filename='log_timeout.txt')

            while True:
                self.log_urls = self.__load_log_urls(filename='log_timeout.txt')
                if self.log_urls:
                    print('Running log file.')
                    self.__run_logs(driver_options=options)
                else:
                    break
            
            # break # For example, running with 1 category

        # Saving data
        self.__save(filename='comments_stars.csv')
        print('CommentStarCrawler, DONE!')
            