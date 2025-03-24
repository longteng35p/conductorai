from pypdf import PdfReader
import re
from nltk.tokenize import word_tokenize

path = "FY25 Air Force Working Capital Fund.pdf"
reader = PdfReader(path)

regexMax = float("-inf")
parsedMax = float("-inf")
contextMax = float("-inf")

### helpers
# parses a single word into the first number found
# $2.14m -> 2140000.0
# returns None if no number is found
def parse_num(text):
    i = 0
    while i < len(text):
        parsedNum = ""
        isDecimal = False
        # start when first digit is found
        if (text[i].isdigit()):
            while i < len(text) and (text[i].isdigit() or text[i] == "," or text[i] == "."):
                # stop parsing if second decimal found
                if text[i] == ".":
                    if isDecimal:
                        break
                    isDecimal = True
                parsedNum += text[i]
                i += 1

        if parsedNum:
            rawNum = float(parsedNum.replace(",", ""))
            if i == (len(text) - 1):
                if text[i].lower() == "k":
                    rawNum *= 1000
                elif text[i].lower() == "m":
                    rawNum *= 1000000
                # elif text[i].lower() == "b":
                #     rawNum *= 1000000000
                elif text[i].lower() == "t":
                    rawNum *= 1000000000000
            return rawNum
        i += 1
    return None

# calculates jaccard index between two strings
def jaccard(str1, str2):
    set1 = set(str1)
    set2 = set(str2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0:
        return 0.0
    return intersection / union

### main
pageNumber = 0
maxPage = -1
for page in reader.pages:
    text = page.extract_text()

    # parse using regex
    regexNums = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+|\d+", text)
    for num in regexNums:
        formattedNum = num.replace(",", "")
        regexMax = max(regexMax, float(formattedNum))

    # parse without regex
    i = 0
    while i < len(text):
        parsedNum = ""
        isDecimal = False # ran into issue with section codes: 1.5.14.9
        if (text[i].isdigit()): # ran into issue with table of contents: .....1
            while i < len(text) and (text[i].isdigit() or text[i] == "," or text[i] == "."):
                if text[i] == ".":
                    if isDecimal:
                        break
                    isDecimal = True
                parsedNum += text[i]
                i += 1

        if parsedNum:
            formattedNum = parsedNum.replace(",", "")
            parsedMax = max(parsedMax, float(formattedNum))
        i += 1

    # using nltk to tokenize
    tokens = word_tokenize(text)
    i = 0
    while i < len(tokens):
        num = parse_num(tokens[i])
        if num:
            if (i + 1) < len(tokens):
                # if (jaccard("hundred", tokens[i + 1].lower()) > 0.8) or ("Dollars in Hundreds" in text):
                #     num *= 100
                # elif (jaccard("thousand", tokens[i + 1].lower()) > 0.8) or ("Dollars in Thousands" in text):
                #     num *= 1000
                # elif (jaccard("million", tokens[i + 1].lower()) > 0.8) or ("Dollars in Millions" in text):
                #     num *= 1000000
                # elif (jaccard("billion", tokens[i + 1].lower()) > 0.8) or ("Dollars in Billions" in text):
                #     num *= 1000000000
                # elif (jaccard("trillion", tokens[i + 1].lower()) > 0.8) or ("Dollars in Trillions" in text):
                #     num *= 1000000000000
                if (jaccard("hundred", tokens[i + 1].lower()) > 0.8):
                    num *= 100
                elif (jaccard("thousand", tokens[i + 1].lower()) > 0.8):
                    num *= 1000
                elif (jaccard("million", tokens[i + 1].lower()) > 0.8):
                    num *= 1000000
                elif (jaccard("billion", tokens[i + 1].lower()) > 0.8):
                    num *= 1000000000
                elif (jaccard("trillion", tokens[i + 1].lower()) > 0.8):
                    num *= 1000000000000
            if num > contextMax:
                maxPage = pageNumber
                contextMax = num
        i += 1
    
    pageNumber += 1

print("Maximum number found using regex match with no context: " + str(regexMax))
print("Maximum number found using string parsing with no context: " + str(parsedMax))
print("Maximum number found with context: " + str(contextMax))
# print(maxPage)