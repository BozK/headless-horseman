import os
import sys
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import mammoth
from cryptography.fernet import Fernet

PUBCOUNT = len(sys.argv) - 1

with open("credentials.txt", "rb") as f:
    ENC_PASS = f.read(1024)
F_CRYPT = Fernet(b'R5JsYEQ9uPZbp-F_PWDXsePlrNJaXDZKtg6ahakP86w=')


def convDocxToHtml(filename):
    with open(filename, "rb") as doc:
        html = mammoth.convert_to_html(doc).value

    li = html.split("</p><p>")
    HEAD = li[0].replace("<p>", "")
    BYLI = li[1]
    
    BODY = "<p>" + "</p><p>".join(li[2:])

    return (HEAD, BYLI, BODY)

def publish(filename):
    driver = webdriver.Firefox(executable_path="C:\Program Files\Geckodriver\geckodriver.exe")
    driver.get("https://admin-newyork1.bloxcms.com/desktop/#/technicianonline.com/editorial-asset")

    #Login
    usernameField = driver.find_element_by_name("email")  
    usernameField.send_keys("news@technicianonline.com")

    passwordField = driver.find_element_by_name("password")
    p = str(F_CRYPT.decrypt(ENC_PASS), 'utf-8')
    passwordField.send_keys(p)

    btn = driver.find_element_by_css_selector(".v-btn.theme--light.primary")
    btn.click()

    #Inside iframe page
    #Need time to let it load
    driver.implicitly_wait(10)
    time.sleep(2)

    ifr1 = driver.find_element_by_tag_name("iframe")
    driver.switch_to.frame(ifr1)

    # ---- ---- ---- ---- INSIDE IFRAME ---- ---- ---- ---- #

    #closes the default page thing if it pops up
    closeDraftBtn = driver.find_elements_by_class_name("x-tool-close")
    if (len(closeDraftBtn) == 2):
        closeDraftBtn[1].click()

    #Getting the New asset button
    b = driver.find_element_by_css_selector(".x-btn-mc .x-btn-arrow .x-btn-text")
    b.click()

    #Need to wait for the one dropdown to open
    time.sleep(0.5)

    #Article button
    b = driver.find_element_by_link_text("Article")
    b.click()

    articleTuple = convDocxToHtml(filename)
    HEADLINE = articleTuple[0]
    BYLINE = articleTuple[1]
    ARTICLE = articleTuple[2]

    #this is so scuffed LOL
    headlineInput = driver.find_element_by_css_selector(".x-box-inner .x-panel.x-panel-noborder.x-form-label-top.x-box-item .x-panel-bwrap .x-panel-body .x-form-item .x-form-element .x-form-text.x-form-field")
    headlineInput.send_keys(HEADLINE)

    bylineInput = driver.find_element_by_class_name("x-form-textarea")
    bylineInput.send_keys(BYLINE)

    time.sleep(2)
    #reaching into the HTML bc that's the easiest way to preserve hyperlinks
    b = driver.find_element_by_css_selector(".x-btn-mc .x-btn-arrow .tncms-icons-settings")
    b.click()
    b = driver.find_element_by_link_text("Edit HTML source")
    b.click()
    b = driver.find_element_by_name("source")
    b.click()
    b.send_keys(ARTICLE)
    #There's probably a better way to do this
    b = b.find_element_by_xpath("..")
    b = b.find_element_by_xpath("..")
    b = b.find_element_by_xpath("..")
    b = b.find_element_by_xpath("..")
    b = b.find_element_by_xpath("..")
    b = b.find_element_by_class_name("x-window-bl")
    #This should be the update button, [1] is the Cancel button
    b = b.find_elements_by_css_selector(".x-btn")[0]
    b.click()

    tagsSection = driver.find_element_by_css_selector(".x-tab-panel.x-tab-panel-noborder.x-border-panel .x-tab-panel-bwrap")
    tagsSubsection = tagsSection.find_elements_by_css_selector(".x-panel-body-noheader")[0]

    #"SECTION" section" 
    tagsSubsection.find_elements_by_css_selector(".x-panel")[0].find_element_by_class_name("x-btn-text-icon").click()
    #all list elements contained by this element
    sections = driver.find_element_by_css_selector(".x-window.x-window-noborder.x-resizable-pinned .x-window-bwrap .x-window-mc .x-tree-root-ct.x-tree-lines .x-tree-root-node").find_elements_by_tag_name("li")
    #news is index 8
    sections[8].find_element_by_tag_name("input").click()
    #clicking the add section button
    driver.find_elements_by_css_selector(".x-window.x-window-noborder.x-resizable-pinned")[1].find_elements_by_css_selector(".x-btn.x-btn-noicon")[0].click()

    #LMAO REMEMBER WHEN THIS WAS ABOUT GENERATING KEYWORDS

for i in range(i, PUBCOUNT + 1):
    t = threading.Thread(target=publish, args=(sys.argv[i]))
    t.start()
    t.join()