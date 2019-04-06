import PyPDF2
import re

pdfFileObj = open('directory.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

text = ""
counter = 0

for i in range(145, 238): # Include only student pages
    page = pdfReader.getPage(i)
    text += page.extractText()
    counter += 1

def get_grade(email):
    end = email.split("@")[0][-2:]

    if end == "20":
        return 2020
    elif end == "21":
        return 2021
    elif end == "22":
        return 2022
    else:
        return 2019

matches = re.compile("[a-z]+[0-9]*@andover\.edu").findall(text)

f = open('names.csv', 'w')
for match in matches:
    f.write(match + "," + str(get_grade(match)) + "\n")

f.close()
