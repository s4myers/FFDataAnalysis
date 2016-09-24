import csv
import os
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle
from numbers import Number

CSV_DIR = "../CSV_data/"
#CSV_DIR = "C:/Users/justin/Documents/GitHub/FFDataAnalysis/CSV_data/"
PICKLE_DIR = "../pickle_files/"

           
YEAR_LIST = [2010,2011,2012,2013,2014,2015,2016]

WEEK_LIST = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]

POS_LIST = ["QB","RB","WR","TE","K"]

# Load all available pickle files
try:
    SALARIES = pickle.load(open(os.path.join(
                        PICKLE_DIR,"dksalaries.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED = pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowed.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED_HALF = pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowedHalfPoint.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED_FULL = pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowedFullPoint.p"),"rb"))
except IOError:
    pass

try:
    CURR_POINTS_ALLOWED = pickle.load(open(os.path.join(
                        PICKLE_DIR,"CurrentPointsAllowed.p"),"rb"))
except IOError:
    pass

try:
    CURR_POINTS_ALLOWED_HALF = pickle.load(open(os.path.join(
                        PICKLE_DIR,"CurrentPointsAllowedHalfPoint.p"),"rb"))
except IOError:
    pass

try:
    CURR_POINTS_ALLOWED_FULL = pickle.load(open(os.path.join(
                        PICKLE_DIR,"CurrentPointsAllowedFullPoint.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED_ROOKIES= pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowedRookies.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED_ROOKIES_HALF = pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowedRookiesHalfPoint.p"),"rb"))
except IOError:
    pass

try:
    PAST_POINTS_ALLOWED_ROOKIES_FULL = pickle.load(open(os.path.join(
                        PICKLE_DIR,"PastPointsAllowedRookiesFullPoint.p"),"rb"))
except IOError:
    pass

try:
    ROOKIE_AVERAGE = pickle.load(open(os.path.join(
                        PICKLE_DIR,"RookieAverage.p"),"rb"))
except IOError:
    pass

try:
    ROOKIE_AVERAGE_HALF = pickle.load(open(os.path.join(
                        PICKLE_DIR,"RookieAverageHalfPoint.p"),"rb"))
except IOError:
    pass

try:
    ROOKIE_AVERAGE_FULL = pickle.load(open(os.path.join(
                        PICKLE_DIR,"RookieAverageFullPoint.p"),"rb"))
except IOError:
    pass

try:
    ROOKIES = pickle.load(open(os.path.join(
                        PICKLE_DIR,"RookieDict.p"),"rb"))
except IOError:
    pass

try:
    TEAM_NAME_CONV = pickle.load(open(os.path.join(
                                PICKLE_DIR,"CityConversion.p"),"rb"))
except IOError:
    pass

try:
    TEAM_LIST = pickle.load(open(os.path.join(
                        PICKLE_DIR,"TeamList.p"),"rb"))
except IOError:
    pass

#Global Functions
def generate_class_list(pos,player_list):
    """
    Create a class list of all avaiable players at a desired position.

    Parameters

    ----------
    pos : string
        The position of the player, e.g. "QB", "RB", etc.
    player_list : list
        A list containing the name of players.



    Returns
    -------
    class_list : list
        A list of Player classes formed by the names in the 
        player_list.  

    """
    if pos == "QB":
        class_list = [QuarterBack(player) for player in player_list]
    elif pos == "RB":
        class_list = [RunningBack(player) for player in player_list]    
    elif pos == "WR":
        class_list = [WideReceiver(player) for player in player_list]
    elif pos == "TE":
        class_list = [TightEnd(player) for player in player_list]
    elif pos == "K":
        class_list = [Kicker(player) for player in player_list]  
    elif pos == "DEF":
        class_list = [Defense(player) for player in player_list]
    else:
        return "Not a proper posistion"
    return class_list

def generate_player_list(pos,active = False):
    """
    Create a list of players at a desired position.

    Parameters

    ----------
    pos : string
        The position of the player, e.g. "QB", "RB", etc.
    active : bool, optional
        Default is `False`.  If `active=True`, then the player list
        is formed by only the active players in the NFL; otherwise,
        it utilizes incorporates retired players as well.



    Returns

    -------
    name_list : list
        A list of player names corresponding to the desired position.

    """

    if active == True:
        csv_file = "ActivePlayerList.csv"
    else:
        csv_file = "AllPlayers.csv"    
    name_list =[]
    csv_path = os.path.join(CSV_DIR,csv_file)
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file,skipinitialspace=True)
        for row in reader:
            if row[0]==pos and row[1] not in name_list:
                name_list.append(row[1])
            else:
                continue
    return name_list
                
class Player(object):
    """
    An active roster player to research for your fantasy lineup.

    Parameters

    ----------
    name : string
        The name of the player.


    """
    
    abbr = ""
    field_names = []
    scoring_field_names = []
    csv_file_name = ""
    fantasy_point_multipliers = {"PassYds":0.04,"PassTD":4.0,"RecYds":0.1,
                                "RecTD":6.0,"Rec":0.0,"RushYds":0.1,
                                "RushTD":6.0,"FGM":3.0,"XPM":1.0,"Int":-2.0,"Lost":-2.0}

    def __init__(self,name):
        self.name = name
        self.csv_path = os.path.join(CSV_DIR,self.csv_file_name)
        self.pickle_file_name = self.name+".p"
        self.pickle_path = os.path.join(PICKLE_DIR,self.abbr,self.pickle_file_name)
        try:
            csvtime = os.path.getmtime(self.csv_path)
            pickletime = os.path.getmtime(self.pickle_path)
            delta = csvtime-pickletime
            if delta > 0:   #checks to see if the csv data has been recently modified
                raise IOError
            else:    
                self.stats = pickle.load(open(self.pickle_path,"rb"))
        except (IOError, OSError):
            self.stats = {year:{week:{} for week in WEEK_LIST} for year in YEAR_LIST}
            with open(self.csv_path) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if row["Player"]==self.name:
                        week = int(row["WK"])
                        year = int(row["Year"])
                        #trying to get away from strings
                        row_keys = row.keys()
                        new_row = {}
                        for k in row_keys:
                            if (k == 'G' or 
                                k == 'GS' or
                                k == "Year" or
                                k == "WK"):
                                try:
                                    new_row[k]=int(row[k])
                                except ValueError:
                                    new_row[k]=row[k]
                            elif k=='Opp' and row[k]!='':
                                try:
                                    opponent = TEAM_NAME_CONV[row[k]]
                                except KeyError:
                                    opponent = TEAM_NAME_CONV[row[k][1:]]
                                    opponent = '@'+opponent
                                new_row[k]=opponent    
                            else:
                                try:
                                    new_row[k]=float(row[k])
                                except ValueError:
                                    if row[k]=='--':
                                        new_row[k]=0.0
                                    else:    
                                        new_row[k]=row[k]
                        self.stats[year][week]=new_row
            # removes years and weeks without data
            for year in YEAR_LIST:
                for week in WEEK_LIST:
                    if self.stats[year][week] == {}:
                        del self.stats[year][week]
                if self.stats[year] == {}:
                    del self.stats[year]

            pickle.dump(self.stats,open(self.pickle_path,"wb"))



    def games_played(self,year):
        """
        Gives the games played in a year.

        Parameters

        ----------
        year : int
            The four digit year.


        Returns

        -------
        games : int
            The number of games played throughout the course of a year.

        """
        games = 0
        for week in WEEK_LIST:
            if self.name in TEAM_LIST:
                if self.stats[year][week]["Home"]!=[]:
                    games+=1
            else:
                try:
                    if (self.stats[year][week]["Game Date"]=="Bye" or 
                        self.stats[year][week]["G"]==0):
                        continue
                    else:
                        games+=1
                except KeyError:
                    return games        
        if games == 0: #for division by zero
            games = 1
        return games
            

    def generate_array_stats(self,field,year):
        """
        Creates an array of float values of a particular field for a 
        requested year.

        Parameters

        ----------
        field : string
            The field, e.g. "PassTD","REC", etc.
        year : int 
            The four digit year



        Returns

        -------
        a : array_like
            This is an array of float values. Byes and games where the 
            player did not participate are not included in the array. 

        """

        if year not in self.stats.keys():
            return "No Data"
        if self.name not in TEAM_LIST:
            temp_list = []
            for week in self.stats[year].keys():
                if (self.stats[year][week]["G"] == 0 or 
                    self.stats[year][week]["Game Date"] == "Bye"):
                    continue 
                else:
                    temp_list += [self.stats[year][week][field]]
        else:
            temp_list = []
            for week in self.stats[year].keys():
                if self.stats[year][week]["Home"] == []:
                    continue 
                else:
                    temp_list += [self.stats[year][week][field]]       
        a = np.array(temp_list)
        return a

    def total(self,field,year,weeks=["all_weeks"]):
        """ 
        Totals the value of a field by week or by entire year.
        
        Parameters

        ----------
        field : string
            The field to be totaled, e.g. "PassTD","REC", etc.
        year : int
            The four digit year
        weeks : list, optional
            By default the entire year will be totaled. If a different week
            list is supplied, only the those weeks will be totaled.



        Returns

        -------
        tot : float
            The total of a field in the self.stats dictionary.

        """
        tot = 0.0
        try:
            self.stats[year]
        except KeyError:
            return "No Data this year"    
        if field not in self.field_names:
            print ("Not a valid field.")
            return
        elif type(weeks)!=list or [type(item)!=str for item in weeks]==[True for i in range(len(weeks))]:
            print "Not a valid argument for weeks"
            return
        elif weeks == ["all_weeks"]:
            tot = np.sum(self.generate_array_stats(field,year))
            return tot
        else:
            week_list = weeks
            try:
                for week in week_list:  
                    if self.stats[year][week][field] == "":
                        tot += 0.0
                    else:
                        tot += self.stats[year][week][field]
                return tot
            except KeyError:
                print "No data available for this year or invalid weeks"        
                return

    def field_average(self,field,year):
        """
        Returns the weekly average of a field for the particular year.

        Parameters

        ----------
        field : string
            The field to average, e.g. "PassTD","REC", etc.
        year : int
            The four digit year.



        Returns

        -------
        avg : float
            The average of field for a particular year.

        """
        if year not in self.stats.keys():
            return "No Data"

        ary = self.generate_array_stats(field,year)
        avg = np.average(ary)
        if np.isnan(avg):
            return 0.0
        else:   
            return avg

    def field_std(self,field,year):
        """
        Returns the weekly standard deviation of a field 
        for the particular year.

        Parameters

        ----------
        field : string
            The field to find the standard deviation, 
            e.g. "PassTD","REC", etc.
        year : int
            The four digit year.



        Returns

        -------
        avg : float
            The average of field for a particular year.

        """
        if year not in self.stats.keys():
            return "No Data"

        ary = self.generate_array_stats(field,year)
        std = np.std(ary)
        if np.isnan(std):
            return 0.0
        else:   
            return std


    def outlier_games(self,year,threshold,ppr=0.0):
        """
        Returns a list of games that a player outperformed their average.

        Parameters

        ----------
        year : int
            The four digit year.
        threshold : float 
            the percent difference from average.
        ppr : float, optional
            Default is `0.0`. Scoring parameter for points per reception.



        Returns

        -------
        outlier_games : list
            A list of weeks where a player satisifies the threshold 
            requirements for the percentage difference from average.

        """
        ppg_avg = self.ppg_average(year,ppr)
        print "Average PPG: " + str(ppg_avg)
        outlier_games = []
        for week in range(1,18):
            points = self.week_points(week,year,ppr)
            try:
                diff = (points - ppg_avg)/ppg_avg
            except TypeError:
                continue
            if diff < 0 and diff < threshold and threshold < 0:
                print str(week) + " " + str(points)
                outlier_games.append(str(week))
            elif diff > 0 and diff > threshold and threshold > 0:
                print str(week) + " " + str(points)
                outlier_games.append(week)

        return outlier_games


    def week_points(self,week,year,ppr=0.0):
        """
        The fantasy points scored during a week and particular year.

        Parameters

        ----------
        week : int
            The week to evaluate.
        year : int
            The four digit year.
        ppr : float, optional
            Default is `0.0`. Scoring parameter for points per reception.



        Returns

        -------
        points : float
            The fantasy point totals for a Player class object for a
            week and particular year. If the class object is a DST,
            then defensive touchdowns are not included in the week 
            points.

        """
        self.fantasy_point_multipliers["Rec"]=ppr
        if year not in self.stats.keys():
            return "No Data"
        # Check for bye week
        try:
            if self.name not in TEAM_LIST:    
                if self.stats[year][week]["Game Date"]=="Bye":
                    return "Bye"
            else:
                if self.stats[year][week]["Home"]==[]:
                    return "Bye"        
        except KeyError:
            return "No Data"

        #scoring currently doesn't include kick returns or defensive TDs
        #Find week points scored by a defense
        if self.name in TEAM_LIST:
            score = self.stats[year][week]["Score"]
            opp_score = float(score.split("-")[1])
            TD = self.stats[year][week]["PassTD"] + self.stats[year][week]["RushTD"]
            FGM = self.stats[year][week]["FGM"]
            FGB = self.stats[year][week]["FGBlk"]
            XPM = self.stats[year][week]["XPM"]
            XPB = self.stats[year][week]["XPBlk"]
            sacks = self.stats[year][week]["Sck"]

            points_from_offense = 6*TD + 3*FGM +XPM

            if points_from_offense == 0:
                base_points = 10.0
            elif points_from_offense < 7:
                base_points = 7.0
            elif points_from_offense < 14:
                base_points = 4.0
            elif points_from_offense < 21:
                base_points = 1.0
            elif points_from_offense < 28:
                base_points = 0.0
            elif points_from_offense < 35:
                base_points = -1.0
            else:
                base_points = -4.0

            turnovers = 0.0
            turnover_fields = ["Int","Lost"]
            for x in turnover_fields:
                turnovers+=self.stats[year][week][x]
            #p = [i for i in self.stats[year][week]["Players"]]
            #for (player,pos) in p:
            #    a = generate_class_list(pos,[player])[0]
            #    for b in turnover_fields:
            #        try:
            #            turnovers += float(a.stats[year][week][b])
            #        except (KeyError, ValueError):
            #            continue
            
            blocks = XPB + FGB
            points = base_points + 2*blocks + sacks + 2*turnovers
            return points
        #Find the week points scored by a player
        else:
            points = 0.0
            for field in self.scoring_field_names:
                points += (self.stats[year][week][field]*
                           self.fantasy_point_multipliers[field])
            return points

    
    def total_points(self,year,ppr=0.0):
        """
        Total points scored for a year.

        Parameters

        ----------
        year : int
            The four digit year.
        ppr : float, optional
            Default is `0.0`. Scoring parameter for points per reception.

        

        Returns

        -------
        tot : float
            The total fantasy points scored during the course of a year.
        
        """
        week_totals = []
        tot = 0.0
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            # did not play this year
            return tot

        for week in week_list:
            if self.name not in TEAM_LIST:
                if (self.stats[year][week]["Game Date"] == "Bye" or
                    self.stats[year][week]['G']==0):
                    continue
                else:
                    week_totals += [self.week_points(week,year,ppr)]
            else:
                if self.stats[year][week]["Home"]==[]:
                    continue
                else:
                    week_totals += [self.week_points(week,year,ppr)]
        if week_totals == []:
            return tot
        else:
            tot = np.sum(week_totals)
            return tot  
    

    def ppg_average(self,year,ppr=0.0):
        """
        Returns the average points per game for a given year.

        Parameters

        ----------
        year : int
            The four digit year.
        ppr : float, optional
            Default is `0.0`. Scoring parameter for points per reception.



        Returns

        -------
        avg : float
            The average points per game for a particular year.

        """
        week_totals = []
        avg = 0.0
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            # did not play this year
            return avg

        for week in week_list:
            if self.name not in TEAM_LIST:
                if (self.stats[year][week]["Game Date"] == "Bye" or
                    self.stats[year][week]['G']==0):
                    continue
                else:
                    week_totals += [self.week_points(week,year,ppr)]
            else:
                if self.stats[year][week]["Home"]==[]:
                    continue
                else:
                    week_totals += [self.week_points(week,year,ppr)]
        if week_totals == []:
            return avg
        else:
            avg = np.round(np.average(week_totals),2)
            return avg

    def ppg_var(self,year,ppr=0.0):
        """
        Returns the variance per game for a given year.

        Parameters

        ----------
        year : string
            The four digit year.
        ppr : float, optional
            Default is `0.0`. Scoring parameter for points per reception.



        Returns

        -------
        var : float
            The statistical variance in fantasy points scored for 
            a particular year.

        """
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            return "No Data"#the player didn't play this year
        
        average = self.ppg_average(year,ppr)
        week_variance = []
        for week in week_list:
            if self.name not in TEAM_LIST:
                if (self.stats[year][week]["Game Date"] == "Bye" or
                    self.stats[year][week]['G']==0):
                    continue
                else:
                    week_variance += [(self.week_points(week,year,ppr) - average)**2]
            else:
                if self.stats[year][week]["Home"]==[]:
                    continue
                else:
                    week_variance += [(self.week_points(week,year,ppr) - average)**2]
        if week_variance == []:
            return "Empty List"
        else:
            var = np.average(week_variance)
            return var

    def field_ratio(self,field1,field2,year,weeks=["all_weeks"]):
        """
        Returns the ratio of two stats for a particular week, weeks, or the year

        Parameters

        ----------
        field1 : string 
            The first field.
        field2 : string 
            The second field.
        year : string
            The four digit year.
        weeks : list, optional
            By default the entire year will be used for field totals. If a 
            different week list is supplied, only the those weeks will 
            be totaled.



        Returns

        -------
        ratio : float
            The ratio of field 1 and field 2 totals with field 1 as the 
            numerator.

        """
        ratio = 0
        field1_total = self.total(field1,year,weeks)
        field2_total = self.total(field2,year,weeks)

        if type(field1_total) == str or type(field1_total) == str:
            print "no data this year"
            return ratio
        else:
            ratio = np.round(field1_total/field2_total,2)
            return ratio

class QuarterBack(Player):
    """ Quarter back position """

    abbr = "QB"
    field_names = ["G","GS","Comp","PassAtt","Pct","PassYds","PassTD","Int",
                   "Sck","Rate","RushAtt","RushYds","RushTD","FUM","Lost"]
    scoring_field_names = ["PassYds","PassTD","RushYds","RushTD","Int","Lost"]
    csv_file_name ="QBStats.csv"

class RunningBack(Player):
    """ Running back position """

    abbr = "RB"
    field_names =["G","GS","RushAtt","RushYds","RushAvg","RushLng","RushTD","Rec",
                  "RecYds","RecAvg","RecLng","RecTD","FUM","Lost"]
    scoring_field_names = ["RushYds","RushTD","Rec","RecYds","RecTD","Lost"]
    csv_file_name = "RBStats.csv"

class WideReceiver(Player):
    """ Wide receiver position """

    abbr = "WR"
    field_names =["G","GS","RushAtt","RushYds","RushAvg","RushLng","RushTD",
                  "Rec","RecYds","RecAvg","RecLng","RecTD","FUM","Lost"]
    scoring_field_names = ["RushYds","RushTD","Rec","RecYds","RecTD","Lost"]
    csv_file_name = "WRStats.csv"

class TightEnd(Player):
    """ Tight end position """

    abbr = "TE"
    field_names =["G","GS","RushAtt","RushYds","RushAvg","RushLng","RushTD",
                  "Rec","RecYds","RecAvg","RecLng","RecTD","FUM","Lost"]
    scoring_field_names = ["RushYds","RushTD","Rec","RecYds","RecTD","Lost"]
    csv_file_name = "TEStats.csv"

class Kicker(Player):
    """ Kickers are people too """

    abbr = "K"
    field_names =["FGBlk","FGLng","FGAtt","FGM","XPM","XPAtt","XPBlk","KO",
                  "KOAvg","TB","Ret","RetAvg"]
    scoring_field_names = ["FGM","XPM"]
    csv_file_name = "KStats.csv"

class Defense(Player):
    """ Defensive Matchup """
    abbr = "DEF"
    field_names = ["Players","RushAtt","RushYds","RushTD","PassAtt","Lost","Int"
                   "PassYds","PassTD","FGBlk","FGAtt","FGM","XPM","XPBlk","Sck",
                   "Home","Won","Score"]
    csv_file_name = "QBStats.csv" #uses QBStats.csv to look for updates

    def __init__(self,name):
        self.name = name
        self.pickle_file_name = self.name+".p"
        self.pickle_path = os.path.join(PICKLE_DIR,self.abbr,self.pickle_file_name)
        self.csv_path = os.path.join(CSV_DIR,self.csv_file_name)
        try:
            csvtime = os.path.getmtime(self.csv_path)
            pickletime = os.path.getmtime(self.pickle_path)
            delta = csvtime-pickletime
            if delta > 0:   #checks to see if the csv data has been recently modified
                raise IOError
            else:    
                self.stats = pickle.load(open(self.pickle_path,"rb"))

        except (IOError, OSError):
            self.stats = {year:{week:{"Players":[],"Home":[],"Won":[],"Score":[],
                          "RushAtt":0.0,"RushYds":0.0,"RushTD":0.0,"Lost":0.0,"Int":0.0,
                          "PassAtt":0.0,"PassYds":0.0,"PassTD":0.0,"Sck":0.0,
                          "FGBlk":0.0,"FGAtt":0.0,"FGM":0.0,"XPM":0.0,"XPBlk":0.0}
                            for week in WEEK_LIST} 
                            for year in YEAR_LIST}
            for pos in POS_LIST:
                csv_path = os.path.join(CSV_DIR,pos+"Stats.csv")
                with open(csv_path) as csv_file:
                    reader = csv.DictReader(csv_file)
                    temp_field = reader.fieldnames
                    fields = [x for x in temp_field if x in self.field_names]
                    for row in reader:
                        opponent = row["Opp"]
                        if opponent == '':
                            continue
                        elif '@' in opponent:
                            opponent = TEAM_NAME_CONV[opponent[1:]]
                            opponent = '@'+opponent
                        else:
                            opponent = TEAM_NAME_CONV[opponent]


                        if self.name in opponent:
                            year = int(row["Year"])
                            week = int(row["WK"])
                            player = row["Player"]
                            for field in fields:
                                value = row[field]
                                if value == "--":
                                    continue
                                else:    
                                    self.stats[year][week][field]+=float(value)
            
                            self.stats[year][week]["Players"].append((player,pos))
            
                            if '@' in opponent:
                                self.stats[year][week]["Home"] = True
                            else:
                                self.stats[year][week]["Home"] = False
                        
                            result = row["Result"] 
                
                            if 'L' in result:
                                self.stats[year][week]["Won"] = True
                            else:
                                self.stats[year][week]["Won"] = False

                            score = (result[1:].split('-')[1] +'-'+result[1:].split('-')[0])
                            self.stats[year][week]["Score"] = score
            pickle.dump(self.stats,open(self.pickle_path,"wb"))                