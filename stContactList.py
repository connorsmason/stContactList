# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 15:46:22 2020

@author: Connor

@homepage: github.com/connorsmason/stContactList
"""

import pandas as pd
from lxml import html
from lxml import etree
import requests
import os

def getBCMBStudents():
    print('Getting JHU BCMB students\n')
    mainPage = requests.get('https://bcmb.bs.jhmi.edu/students')
    stringDoc = html.fromstring(mainPage.text)
    # create a Tuple for every link on the page (element, attribute, link, pos)
    linkList = list(stringDoc.iterlinks())
    studentLinks = []  # List where we'll store links to student pages
    for x, y, z, h in linkList:
        # Add student links to list
        if y == 'href' and 'edu/people/students/' in z:
            studentLinks.append(z)
    return studentLinks
def getBCMBStudentInfo(stLink):
    # Selectors for relevant information on student page
    nameXPath = "//div[@class='details']/h2"
    emailXPath = "//div[contains(@class, 'field-name-field-email')]/div/div/a"
    labXPath = "//div[contains(@class, 'field-name-field-current-lab')]/div/div"
    advisorXPath = "//div[contains(@class, 'field-name-field-associated-faculty')]/div/div/a"
    advisorBackupXPath = "//div[contains(@class, 'field-name-field-alumni-pi')]/div/div"
    yearXPath = "//div[contains(@class, 'field-name-field-start-year')]/div/div"

    # Navigate to student page
    stPage = requests.get(stLink)
    root = etree.HTML(stPage.text)
    tree = etree.ElementTree(root)

    # Get relevant information from page
    stName = tree.xpath(nameXPath)[0].text
    stName = stName.split(' ', 1)
    stFirstName = stName[0]
    stLastName = stName[1]
    try:
        stEmail = tree.xpath(emailXPath)[0].text
    except IndexError:
        stEmail = '' # Some students don't have an email listed. These should be students who have recently joined
    stLab = tree.xpath(labXPath)[0].text
    try:
        stAdvisor = tree.xpath(advisorXPath)[0].text
    except IndexError:
        try: # In some cases, advisor is listed under 'PI' instead of 'Associated Faculty'
            stAdvisor = tree.xpath(advisorBackupXPath)[0].text
        except IndexError:
            stAdvisor = '' # In others, they don't have an advisor listed
    stYear = tree.xpath(yearXPath)[0].text

    # Return data as dictionary
    stDict = {"firstName": stFirstName,
              "lastName": stLastName,
              "email": stEmail,
              "lab": stLab,
              "advisor": stAdvisor,
              "Matriculation_year": stYear}

    return stDict

def getSts():
    # Get links to BCMB student pages
    studentLinks = getBCMBStudents()
    stDataList = [] # List of dicts, each containing student data we want
    totalNumber = len(studentLinks)
    count = 0
    # Go to each student's page, get data
    for x in studentLinks:
        count+=1
        print('{} / {}'.format(count, totalNumber), end='\r', flush=True)
        stDict = getBCMBStudentInfo(x)
        stDataList.append(stDict)
    # Output list of dicts to CSV in current working directory
    df = pd.DataFrame(stDataList)
    cwd = os.getcwd()
    df.to_csv(cwd + '/stContactList.csv', index=False)
    print(f'Done. Output sent to {cwd}/stContactList.csv')

if __name__ == '__main__':
    getSts()
