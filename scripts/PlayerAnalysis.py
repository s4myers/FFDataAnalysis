import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle
from numbers import Number

CSV_DIR = "../CSV_data/"
#CSV_DIR = "C:/Users/justin/Documents/GitHub/FFDataAnalysis/CSV_data/"
PICKLE_DIR = "../pickle_files/"

TEAM_LIST =["BUF","MIA","NE","NYJ","BAL","CIN","CLE","PIT","HOU","IND","JAC",
            "TEN","DEN","KC","OAK","SD","DAL","NYG","PHI","WAS","CHI","DET",
            "GB","MIN","ATL","CAR","NO","TB","ARI","STL","SF","SEA"]
           
YEAR_LIST = ["2010","2011","2012","2013","2014","2015"]

WEEK_LIST = ["1","2","3","4","5","6","7","8","9","10",
             "11","12","13","14","15","16","17"]

POS_LIST = ["QB","RB","WR","TE","K"]
                





class Player(object):
    """
    An active roster player to research for your fantasy lineup.

    Attributes:
        name: The name of the player as a string
    """
    #currently turned of .5 PPR
    abbr = ""
    field_names = []
    scoring_field_names = []
    csv_file_name = ""
    fantasy_point_multiplers = {"PassYds":0.04,"PassTD":4.0,"RecYds":0.1,
                                "RecTD":6.0,"Rec":0.0,"RushYds":0.1,
                                "RushTD":6.0,"FGM":3.0,"XPM":1.0,"Int":-2.0,"Lost":-2.0}

    def __init__(self,name):
        self.name = name
        self.csv_path = os.path.join(CSV_DIR,self.csv_file_name)
        self.pickle_file_name = self.name+".p"
        self.pickle_path = os.path.join(PICKLE_DIR,self.abbr,self.pickle_file_name)
        try:
            self.stats = pickle.load(open(self.pickle_path,"rb"))
        except IOError:
            self.stats = {year:{week:{} for week in WEEK_LIST} for year in YEAR_LIST}
            with open(self.csv_path) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if row["Player"]==self.name:
                        week = row["WK"]
                        year = row["Year"]
                        self.stats[year][week]=row
            # removes years and weeks without data
            for year in YEAR_LIST:
                for week in WEEK_LIST:
                    if self.stats[year][week] == {}:
                        del self.stats[year][week]
                if self.stats[year] == {}:
                    del self.stats[year]

            pickle.dump(self.stats,open(self.pickle_path,"wb"))




    def generate_array_stats(self,field,year):
        """
        Creates an array of float values of a particular field for a requested year.
        Each item is the value for a given week.
        Byes and games where the player did not participate are not included. 

        Keyword Arguments:
        field - The field as a string
        year - The year as a string

        """
        temp_list = []
        for week in self.stats[year].keys():
            if (self.stats[year][week]["G"] == "0" or 
               self.stats[year][week]["Game Date"] == "Bye"):
                continue 
            elif self.stats[year][week][field] == "--":
                temp_list += [0.0]
            else:
                temp_list += [float(self.stats[year][week][field])]
        return np.array(temp_list)


    def total(self,field,year,weeks=["all_weeks"]):
        """ 
        Totals the value of a given field by week or by entire year
        
        Keyword Arguments:
        field - The field as a string
        year - the year of as a string
        weeks - optional, a list of strings, e.g: ["14","15","16"]

        """
        tot = 0.0
        try:
            self.stats[year]
        except KeyError:
            return "No Data this year"    
        if field not in self.field_names:
            print ("Not a valid field. Please choice from: \n%s"
                   % self.field_names)
            return
        elif type(weeks)!=list or [type(item)!=str for item in weeks]==[True for i in range(len(weeks))]:
            print "Not a valid argument for weeks"
            return
        elif weeks == ["all_weeks"]:
            week_list = self.stats[year].keys()
        else:
            week_list = weeks
        try:
            for week in week_list:  
                if (self.stats[year][week][field] == "--" 
                    or self.stats[year][week][field] == ""):
                    tot += 0.0
                else:
                    tot += float(self.stats[year][week][field])
            return tot
        except KeyError:
            print "No data available for this year or invalid weeks"        
            return

    def field_average(self,field,year):
        """
        Returns the weekly average of a stat for the the season

        Keyword Arguments:
        field - The field to total as a string
        year - the year of interest as a string

        """
        try:
            week_dict = self.stats[year][week]
        except KeyError:
            return "No Data"
        ary = self.generate_array_stats(field,year)
        avg = np.average(ary)
        if np.isnan(avg):
            return 0.0
        else:   
            return avg

    def field_std(self,field,year):
        """
        Returns the weekly the standard deviation of a stat for the season

        Keyword Arguments:
        field - The field to total as a string
        year - the year of interest as a string
        
        """
        try:
            week_dict = self.stats[year][week]
        except KeyError:
            return "No Data"
        ary = self.generate_array_stats(field,year)
        std = np.std(ary)
        if np.isnan(std):
            return 0.0
        else:   
            return std

    def breakout_games(self, year, multiplier):
        """
        Returns a list of games that a player outperformed their average.

        Keyword Arguments:
        year - the year of interest as a string
        multiplier - threshold for 'breakout' games
            i.e. 1.5 = 50% more than their average
                 2.0 = 2x their average
        """
        ppg_avg = self.ppg_average(year)
        print "Average PPG: " + str(ppg_avg)
        breakout_games = []
        for week in range(1,18):
            points = self.week_points(str(week), year)
            if isinstance(points, Number) & (points > ppg_avg * multiplier):
                print str(week) + " " + str(points)
                breakout_games.append(str(week))
        return breakout_games


    def week_points(self,week,year):
        try:
            week_dict = self.stats[year][week]
        except KeyError:
            return "No Data"
        try:      
            if self.stats[year][week]["Game Date"]=="Bye":
                return "Bye"
        except KeyError:
            return "No Data"        

        points = 0.0
        for field in self.scoring_field_names:
            if self.stats[year][week][field] != "--":
                points += (float(self.stats[year][week][field])*
                           self.fantasy_point_multiplers[field])
            else:
                continue
        return points

    
    def total_points(self,year):
        """
        Total points scored for a given year

        Keyword Arguments:
        year - the year as a string
        
        """
        week_totals = []
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            # did not play this year
            return 0.0

        for week in week_list:
            if self.stats[year][week]["Game Date"] == "Bye":
                continue
            elif self.stats[year][week]['G'] != '1':
                continue
            else:
                week_totals += [self.week_points(week,year)]
        if week_totals == []:
            return 0.00
        else:   
            return np.sum(week_totals)   
    

    def ppg_average(self,year):
        """
        Returns the average points per game for a given year

        Keyword Arguments:
        year - the year as a string
        
        """
        week_totals = []
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            # did not play this year
            return 0.0

        for week in week_list:
            if self.stats[year][week]["Game Date"] == "Bye":
                continue
            elif self.stats[year][week]['G'] != '1':
                continue
            else:
                week_totals += [self.week_points(week,year)]
        if week_totals == []:
            return 0.00
        else:   
            return np.round(np.average(week_totals),2)      

    def ppg_var(self,year):
        """
        Returns a tuple of the variance in weekly points per game for a given year
        and also the weeks of games played

        Keyword Arguments:
        year - the year as a string

        """
        try:
            week_list = self.stats[year].keys()
        except KeyError:
            return ("Did Not Play in {}".format(year),0) #the player didn't play this year
        
        average = self.ppg_average(year)
        week_variance = []
        for week in week_list:
            if self.stats[year][week]["Game Date"] == "Bye":
                continue
            elif self.stats[year][week]["G"] != '1':
                continue
            else:
                week_variance += [(self.week_points(week,year) - average)**2]
        if week_variance == []:
            return ("Empty List",0)
        else:
            return (np.average(week_variance),len(week_variance))

    def field_ratio(self,field1,field2,year,weeks=["all_weeks"]):
        """
        Returns the ratio of two stats for a particular week, weeks, or the year
        Keyword Arguments:
        field1 - the first field name as a string
        field2 - the second field name as a string
        year - the year as a string
        weeks - list of weeks as a string 

        """
        field1_total = self.total(field1,year,weeks)
        field2_total = self.total(field2,year,weeks)

        if type(field1_total) == str or type(field1_total) == str:
            return "no data this year"
        else:
            return np.round(field1_total/field2_total,2)

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
    field_names =["G","GS","RushAtt","RushYds","Avg","RushLng","RushTD","Rec",
                  "RecYds","Avg","RecLng","RecTD","FUM","Lost"]
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
    field_names = ["Players","RushAtt","RushYds","RushTD","PassAtt",
                   "PassYds","PassTD","FGBlk","FGAtt","FGM","Home","Won","Score"]

    def __init__(self,name):
        self.name = name
        self.pickle_file_name = self.name+".p"
        self.pickle_path = os.path.join(PICKLE_DIR,self.abbr,self.pickle_file_name)
        try:
            self.stats = pickle.load(open(self.pickle_path,"rb"))
        except IOError:
            self.stats = {year:{week:{"Players":[],"Home":[],"Won":[],"Score":[],
                          "RushAtt":0.0,"RushYds":0.0,"RushTD":0.0,
                          "PassAtt":0.0,"PassYds":0.0,"PassTD":0.0,
                          "FGBlk":0.0,"FGAtt":0.0,"FGM":0.0}
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
                        if self.name in opponent and opponent != "":
                            year = row["Year"]
                            week = row["WK"]
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