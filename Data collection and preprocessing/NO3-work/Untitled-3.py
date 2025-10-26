# 模拟爬取云果网站
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()

options.add_experimental_option('detach', True)

driver = webdriver.Chrome(options=options)

driver.get('https://www.gaoyuanyunguo.com/home/article/newslists.html')


titles = driver.find_elements(By.CLASS_NAME, 'line-clamp-1')
for title in titles:
    print(title.text)
print(len(titles))
