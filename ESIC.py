inputFile = open("esi-doc.txt")

# Looping through the file line by line
#line = inputFile.readline()
# print(line)
# Flag Variables
contributionHistoryFlag = "N"
firstTableFlag = "N"
secondTableFlag = "N"
readingFirstTable = "N"
readingSecondTable = "N"
secondTableDataIgnore = "Y"


# Generic Variables
fileLine = ""
lineNumber = 0
firstTableLineOffset = 0
secondTableLineOffset = 0
secondTableDataIgnore = "Y"

#########################################################################

########################################################################
# Function for reading contribution history
#######################################################################


def contributionHistory(fileLine):
    #    print("line Number" + str(lineNumber))
    if("Contribution History Of" in fileLine):
        print("in the Contribution history for line number" + str(lineNumber))
# Changing the flag so that the code only runs once
        global contributionHistoryFlag
        contributionHistoryFlag = "Y"
#        print(fileLine)

        accountNumber = fileLine[24:38]
        month = fileLine[45:55]
        print("account Number" + str(accountNumber))
        print("month" + str(month))


#############################################################################
# ideally a database call should end the function
##############################################################################

##############################################################################
# Start of firsttable data function
##############################################################################
def firstTableData(fileLine):
    global firstTableLineOffset
    if("Total IP Contribution" in fileLine):
        print("starting First Table data" + str(lineNumber))
        global readingFirstTable
        readingFirstTable = "Y"
    if(readingFirstTable == "Y"):
        firstTableLineOffset = firstTableLineOffset+1
        if(firstTableLineOffset == 6):
            print("Total Ip Contribution" + str(fileLine[0:10]))
        elif(firstTableLineOffset == 7):
            print("Total employer Contribution" + str(fileLine[0:10]))
        elif(firstTableLineOffset == 10):
            print(fileLine)
            global firstTableFlag
            firstTableFlag = "Y"
            readingFirstTable = "N"


############################################################################
# reading data for second table
# ######################################################################
def secondTableData(fileLine):
    #    print(" In second table")
    global secondTableLineOffset
    global readingSecondTable
    global secondTableDataIgnore
#    print(str(secondTableLineOffset) + readingSecondTable)
    if("SNo." in fileLine):
        print("starting second Table data" + str(lineNumber))
        readingSecondTable = "Y"
    if(readingSecondTable == "Y"):
     #       print(" in the Y if")
        secondTableLineOffset = secondTableLineOffset+1
        if(secondTableLineOffset == 11):
            secondTableLineOffset = 0
            secondTableDataIgnore = "N"
            print("Start")
        if(secondTableLineOffset == 1 and secondTableDataIgnore == "N"):
            print("S.no" + fileLine)
        elif(secondTableLineOffset == 4 and secondTableDataIgnore == "N"):
            print("Name" + fileLine)
        elif(secondTableLineOffset == 8 and secondTableDataIgnore == "N"):
            print("End")
            secondTableLineOffset = 0


for fileLine in inputFile:
    lineNumber = lineNumber+1

    # Calling the function for Contribution History
    if(contributionHistoryFlag == "N"):
        contributionHistory(fileLine)
    elif(firstTableFlag == "N"):
        firstTableData(fileLine)
    elif(secondTableFlag == "N"):
        secondTableData(fileLine)
