# Code by Justin McMillan for the purpose of pulling a list of all NFL active players
# as well as the corresponding links to their game log pages for the 2014 season

from bs4 import BeautifulSoup, SoupStrainer
import urllib2 as ul
from string import printable
import re, os
import fileinput

abbr = {'quarterback': 'QB', 'runningback': 'RB', 'widereceiver': 'WR', 'tightend': 'TE', 'kicker': 'K'}
new_qb_fields = "WK,Game Date,Opp,Result,G,GS,Comp,PassAtt,Pct,PassYds,PassAvg,PassTD,Int,Sck,SckY,Rate,RushAtt,RushYds,RushAvg,RushTD,FUM,Lost,Player,Year,Team"
qb_fields = "WK,Game Date,Opp,Result,G,GS,Comp,PassAtt,Pct,PassYds,PassAvg,PassTD,Int,Sck,SckY,Rate,RushAtt,RushYds,RushAvg,RushTD,FUM,Lost,Player,Year"
rb_fields = "WK,Game Date,Opp,Result,G,GS,RushAtt,RushYds,RushAvg,RushLng,RushTD,Rec,RecYds,RecAvg,RecLng,RecTD,FUM,Lost,Player,Year"
wr_fields = "WK,Game Date,Opp,Result,G,GS,Rec,RecYds,RecAvg,RecLng,RecTD,RushAtt,RushYds,RushAvg,RushLng,RushTD,FUM,Lost,Player,Year"
te_fields = "WK,Game Date,Opp,Result,G,GS,Rec,RecYds,RecAvg,RecLng,RecTD,RushAtt,RushYds,RushAvg,RushLng,RushTD,FUM,Lost,Player,Year"
k_fields = "WK,Game Date,Opp,Result,G,GS,FGBlk,FGLng,FGAtt,FGM,FGPct,XPM,XPAtt,XPPct,XPBlk,KO,KOAvg,TB,Ret,RetAvg,Player,Year"
pos_fields_dict = {'QB': qb_fields, 'RB': rb_fields, 'WR': wr_fields, 'TE': te_fields, 'K': k_fields}
titlesPulled = False


def main():
    positions = ["quarterback", "runningback", "widereceiver", "tightend", "kicker"]
    #scrape_current_players(positions)
    rem_dups()

def rem_dups():

    with open('C:\Users\justin\Documents\GitHub\FFDataAnalysis\CSV_data\CombinedPlayerList.csv','r') as in_file, open('C:\Users\justin\Documents\GitHub\FFDataAnalysis\CSV_data\CombinedPlayerList2.csv','w') as out_file:
        seen = set() # set for fast O(1) amortized lookup
        for line in in_file:
            if line in seen: continue # skip duplicate

            seen.add(line)
            out_file.write(line)

def scrape_current_players(positions):
    """
    This function visits the 'Current Players' pages and pulls a list of all Currently Active Players with their
    position abbreviation and player profile URL.

    :param positions: a list containing the 5 offensive positions
    :return: data is written to ActivePlayerList.csv
    """
    for i in range(len(positions)):
        for page in range(6):
            position = positions[i]
            url = "http://www.nfl.com/players/search?category=position&playerType=current&conference=ALL&d-447263-p=%s&filter=%s&conferenceAbbr=null" % (page+1, position)
            try:
                soup = BeautifulSoup(ul.urlopen(url).read(), "html.parser")
                links = soup.findAll('a', href=re.compile('^/player/'))
                for j in range(len(links)):
                    nameFirstLast = str(links[j]).split('"')[2].lstrip('>').rstrip('</a>').split(',')[1].lstrip() + " " + str(links[j]).split('"')[2].lstrip('>').rstrip('</a>').split(',')[0]
                    link = "http://www.nfl.com" + str(links[j]).split('"')[1].rstrip('profile') + "gamelogs?season="
                    outputLine = abbr[position], ',', nameFirstLast, ',', link, '\n'
                    with open("../CSV_data/ActivePlayerList.csv", "a") as text_file:
                        text_file.writelines(outputLine)
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

def pull_game_stats2(url, player_name, firstYear, lastYear, pos):
    """
    This function is accessed by the generate_url_list() function.
    It iterates through Game Log pages, pulls stats, and writes to csv file.

    :param url: URL to 'Game Log'
    :param player_name: player name
    :param yearTemp: year
    :param pos:
    :return: writes to output csv files
    """
    try:
        readPage = ul.urlopen(url).read()
        soup = BeautifulSoup(readPage, "html.parser")
        file_path = "../CSV_data/Temp/" + pos + "Stats.csv"

        # assign field names
        fieldNames = soup.find("tr", {"class" : "player-table-key"}).findAll("td")
        numColumns = len(fieldNames)
        global titlesPulled
        if (titlesPulled == False):
            outputLine = pos_fields_dict[pos]
            #for i in range(len(fieldNames)):
            #    outputLine = fieldNames[i].text, ", "
            with open(file_path, "a") as text_file:
                text_file.writelines(outputLine)
            text_file.close()
            titlesPulled = True

        # pull the statistics
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

        # write statistics to csv
        for j in range(len(rowsList)):
            tempRow = rowsList[j]
            cells = tempRow.findAll("td")
            output = "\n"
            for i in range(numColumns): # for each field, append to output string
                tempCell = str(cells[i]).lstrip("<td>").rstrip("</td>").replace('\t', "").replace('\r', "").replace('\n', "").replace(" ", "")
                cell = re.sub('<[^>]+>', '', tempCell)
                cell = re.sub("[^{}]+".format(printable), "", cell)
                output = output + cell + ","
                if (tempCell == 'Bye'):
                    for i in range(numColumns-2):
                        output = output + ","
                    break
            output = output + player_name + "," + str(yearTemp)
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

def pull_game_stats(url, player_name, yearTemp, pos):
    """
    This function is accessed by the generate_url_list() function.
    It iterates through Game Log pages, pulls stats, and writes to csv file.

    :param url: URL to 'Game Log'
    :param player_name: player name
    :param yearTemp: year
    :param pos:
    :return: writes to output csv files
    """
    try:
        readPage = ul.urlopen(url).read()
        soup = BeautifulSoup(readPage, "html.parser")
        file_path = "../CSV_data/" + pos + "Stats.csv"

        # pull Field names
        statTitle = soup.find("tr", {"class" : "player-table-key"}).findAll("td")
        numColumns = len(statTitle)
        global titlesPulled
        if (titlesPulled == False):
            outputLine = pos_fields_dict[pos]
            #for i in range(len(statTitle)):
            #    outputLine = statTitle[i].text, ", "
            with open(file_path, "a") as text_file:
                text_file.writelines(outputLine)
            text_file.close()
            titlesPulled = True

        # pull the statistics
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

        # write statistics to csv
        for j in range(len(rowsList)):
            tempRow = rowsList[j]
            cells = tempRow.findAll("td")
            output = "\n"
            for i in range(numColumns): # for each field, append to output string
                tempCell = str(cells[i]).lstrip("<td>").rstrip("</td>").replace('\t', "").replace('\r', "").replace('\n', "").replace(" ", "")
                cell = re.sub('<[^>]+>', '', tempCell)
                cell = re.sub("[^{}]+".format(printable), "", cell)
                output = output + cell + ","
                if (tempCell == 'Bye'):
                    for i in range(numColumns-2):
                        output = output + ","
                    break
            output = output + player_name + "," + str(yearTemp)
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

def generate_url_list(position, pgNum, pos):
    """
    This function visits the 'Current Players' pages and pulls a list of all Currently Active Players.

    :param url: URL to 'Game Log'
    :param player_name: player name
    :param yearTemp: year
    :param pos:
    :return: writes to output csv files
    """
    url = "http://www.nfl.com/players/search?category=position&playerType=current&conference=ALL&d-447263-p=%s&filter=%s&conferenceAbbr=null" % (pgNum, position)
    print url
    try:
        readPage = ul.urlopen(url).read()
        soup = BeautifulSoup(readPage, "html.parser")
        links = soup.findAll('a', href=re.compile('^/player/'))

        for i in range(len(links)):
            url_tag = str(links[i])
            splitText = url_tag.split('"')
            year = 2015
            numYears = 6
            for j in range(numYears):
                yearTemp = year - j
                link = "http://www.nfl.com" + splitText[1].rstrip('profile') + "gamelogs?season=%s" % str(yearTemp)
                nameLastFirst = splitText[2].lstrip('>').rstrip('</a>')
                names = nameLastFirst.split(',')
                nameFirstLast = names[1].lstrip() + " " + names[0]
                outputLine = abbr[position], ',', nameFirstLast, ',', link, '\n'
                print "Player/Year to search for: " + nameFirstLast + " " + str(yearTemp)
                with open("../CSV_data/UrlList.csv", "a") as text_file:
                    text_file.writelines(outputLine)
                text_file.close()
 #               pull_game_stats(link, nameFirstLast, yearTemp, pos)

    except IOError, e:
        print 'Failed to open url'
        print '-------------------------------------'
        if hasattr(e, 'code'):
            print 'We failed with error code - %s.' % e.code
        elif hasattr(e, 'reason'):
            print "The error object has the following 'reason' attribute :"
            print e.reason
            return False


if __name__ == "__main__":
    main()