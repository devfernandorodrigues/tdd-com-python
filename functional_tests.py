from selenium import webdriver

options = webdriver.FirefoxOptions()
options.binary_location = "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox-bin"
browser = webdriver.Firefox(options=options)
browser.get("http://localhost:8000")

assert 'Django' in browser.title
