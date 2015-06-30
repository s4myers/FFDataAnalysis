# Code by Justin McMillan for the purpose of pulling a list of all NFL active players
# as well as the corresponding links to their game log pages for the 2014 season

from bs4 import BeautifulSoup, SoupStrainer
import urllib2 as ul
import re

abbr = {'quarterback': 'QB', 'runningback': 'RB', 'widereceiver': 'WR', 'tightend': 'TE', 'kicker': 'K'}
titlesPulled = False
def main():

    positions = ["quarterback", "runningback", "widereceiver", "tightend", "kicker"]
    for i in range(len(positions)):
        for j in range(6):
            pullList(positions[i], j+1, abbr[positions[i]])

def pullList(tempPosition, tempPage, tempPositionAbbr):

    urlTemp = "http://www.nfl.com/players/search?category=position&playerType=current&conference=ALL&d-447263-p=%s&filter=%s&conferenceAbbr=null" % (tempPage, tempPosition)

    try:
        readPage = ul.urlopen(urlTemp).read()
        soup = BeautifulSoup(readPage, "html")
        links = soup.findAll('a', href=re.compile('^/player/'))

        for i in range(len(links)):
            textLine = str(links[i])
            splitText1 = textLine.split('"')
            year = 2014
            numYears = 5
            for j in range(numYears):
                yearTemp = year - j
                link = "http://www.nfl.com" + splitText1[1].rstrip('profile') + "gamelogs?season=%s" % str(yearTemp)
                nameLastFirst = splitText1[2].lstrip('>').rstrip('</a>')
                names = nameLastFirst.split(',')
                nameFirstLast = names[1] + " " + names[0]
                outputLine = abbr[tempPosition], ',', nameFirstLast, ',', link, '\n'
                with open("./Output/PlayerList.csv", "a") as text_file:
                    text_file.writelines(outputLine)
                text_file.close()
                pullStats(link, nameFirstLast, yearTemp, tempPositionAbbr)

    except IOError, e:
        print 'Failed to open url'
        print '-------------------------------------'
        if hasattr(e, 'code'):
            print 'We failed with error code - %s.' % e.code
        elif hasattr(e, 'reason'):
            print "The error object has the following 'reason' attribute :"
            print e.reason
            return False

def pullStats(urlTemp, nameTemp, yearTemp, tempPositionAbbr):
    try:
        print tempPositionAbbr
        readPage = ul.urlopen(urlTemp).read()
        soup = BeautifulSoup(readPage, "html")
        file_path = "./Output/" + tempPositionAbbr + "Stats.csv"

        # pull the stat titles
        statTitle = soup.find("tr", {"class" : "player-table-key"}).findAll("td")
        numColumns = len(statTitle)
        global titlesPulled
        if (titlesPulled == False):
            for i in range(len(statTitle)):
                outputLine = statTitle[i].text, ", "
                with open(file_path, "a") as text_file:
                    text_file.writelines(outputLine)
                text_file.close()
        titlesPulled = True

        # pull the stats
        table = soup.findAll("table", {"class":"data-table1"})
        regularSeason = table[1]
        for i in range(len(regularSeason)):
            body = regularSeason.findAll("tbody")
        body1 = body[0]
        rows = body1.findAll("tr")
        rowsList = []

        for i in range(len(rows)):
            if len(rows[i]) > 2:
                rowsList.append(rows[i])
        del rowsList[len(rowsList)-1]

        for j in range(len(rowsList)):
            tempRow = rowsList[j]
            cells = tempRow.findAll("td")

            output = "\n"
            for i in range(numColumns):
                tempCell = str(cells[i]).lstrip("<td>").rstrip("</td>").replace('\t', "").replace('\r', "").replace('\n', "").replace(" ", "")
                output = output + re.sub('<[^>]+>', '', tempCell) + ","
                if (tempCell == 'Bye'):
                    for i in range(numColumns-2):
                        output = output + ","
                    break
            output = output + nameTemp + "," + str(yearTemp)
            print output
            with open(file_path, "a") as text_file:
                text_file.writelines(output)
            text_file.close()

    except IOError, e:
        print 'Failed to open url'
        print '-------------------------------------'
        if hasattr(e, 'code'):
            print 'We failed with error code - %s.' % e.code
        elif hasattr(e, 'reason'):
            print "The error object has the following 'reason' attribute :"
            print e.reason
            return False

    except IndexError:
        print 'No regular season data.'
        return False

    except AttributeError:
        print 'No regular season data.'
        return False

main()
