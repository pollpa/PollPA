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

matches = re.compile("[a-z0-9]+@andover\.edu").findall(text)

f = open('names.txt', 'w')
for match in matches:
    f.write(match + "\n")

f.close()
