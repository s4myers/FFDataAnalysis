import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from numbers import Number

#CSV_DIR = "../CSV_data/"
CSV_DIR = "C:/Users/justin/Documents/GitHub/FFDataAnalysis/CSV_data/"

TEAM_LIST =["BUF","MIA","NE","NYJ","BAL","CIN","CLE","PIT","HOU","IND","JAC",
            "TEN","DEN","KC","OAK","SD","DAL","NYG","PHI","WAS","CHI","DET",
            "GB","MIN","ATL","CAR","NO","TB","ARI","STL","SF","SEA"]
           
YEAR_LIST = ["2010","2011","2012","2013","2014"]

WEEK_LIST = ["1","2","3","4","5","6","7","8","9","10",
             "11","12","13","14","15","16","17"]

POS_LIST = ["QB","RB","WR","TE","K"]


def find_opponents(team,week,year):
    """
    Find all the players who participated in a game. Returns a tuple
    of the players name and position.

    Keyword Arguments:
    team - city abbreviation as a string
    week - the week as a string
    year - the year as a string

    """
    opponent_list = []
    for pos in POS_LIST:
        csv_file_name = pos+"Stats.csv"
        csv_path = os.path.join(CSV_DIR,csv_file_name)
        with open(csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if (row["Year"]==year and row["WK"]==week and team in row["Opp"]):
                    opponent_list +=[(row["Player"],pos)]

    return opponent_list                


def generate_player_list(pos):
    """
    Create a list of all avaiable players at a desired position

    Keyword Arguments:
    pos - the position enter as a string; e.g. "QB", "RB", etc.

    """
    name_list =[]
    csv_path = os.path.join(CSV_DIR,"AllPlayers.csv")
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0]==pos and row[1] not in name_list:
                name_list+=[row[1]]
            else:
                continue
    return name_list


def generate_class_list(pos,player_list):
    """
    Create a list of all avaiable players at a desired position

    Keyword Arguments:
    pos - the position enter as a string; e.g. "QB", "RB", etc.

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
    else:
        return "Not a proper posistion"
    return class_list    


def correlation(pos,year_list,var1,var2="PPG",plot=False):
    """
    Determines the correlation of the variables var1 and var2 for a given year.
    Currently y is the points per game average as default.

    Keyword Arguments:
    pos - the player position; e.g. "QB", "RB", etc.
    year_list - a list of years to return correlation values
    var1 - variable 1
    var2 - variable 2 (default variable to test is points per game)
    plot - a boolean value of whether or not to plot the data
    """
    r_list = []


    player_list = generate_player_list(pos)

    class_list = generate_class_list(pos,player_list)
    
    #Generate variable list
    for year in year_list:
        if var2 == "PPG":
            xy_list = [(player.field_average(var1,year),player.ppg_average(year)) 
            for player in class_list]
        else:
            xy_list = [(player.field_average(var1,year),player.field_average(var2,year))
            for player in class_list]
            

        #Find Correlation Coefficient 
        N = len(xy_list)
        x = np.array([xy_list[i][0] for i in range(N)])
        y = np.array([xy_list[i][1] for i in range(N)])
        x_sum = np.sum(x)
        y_sum = np.sum(y)
        xx_sum = np.sum(x**2)
        yy_sum = np.sum(y**2)
        xy_sum = np.sum(x*y)

        numerator = N*xy_sum - x_sum*y_sum
        denominator = np.sqrt((N*xx_sum - x_sum**2)*(N*yy_sum-y_sum**2))

        r = numerator/denominator
        r_list +=[r]

        if plot == True:
            fig, ax = plt.subplots()
            plt.scatter(x,y)
            plt.xlabel(var1)
            plt.ylabel(var2)
            plt.title("%s vs %s"%(var1,var2))
            plt.tight_layout()
            plt.show()


    return r_list


def points_against(pos_list):
    """
    Generate a nested dictionary of all the for poinst allowed to positions by team.

    pos_list - the list of positions
    year_list - years to be considered
    """
    temp_dict = {}

    for pos in pos_list:
        
        temp_dict[pos]={}
        
        player_list = generate_player_list(pos)

        class_list = generate_class_list(pos,player_list)

        for year in YEAR_LIST:
            temp_dict[pos][year]={team:0.0 for team in TEAM_LIST}
            for player in class_list:
                for week in WEEK_LIST:
                    points = player.week_points(week,year)
                    if points == "Bye" or points == "No Data":
                        continue    
                    else:
                        team = player.stats[year][week]["Opp"]    
                        
                        if '@' in team:
                            team = team[1:]
                        temp_dict[pos][year][team] += points 

    return temp_dict
                

class Player(object):
    """
    An active roster player to research for your fantasy lineup.

    Attributes:
        name: The name of the player as a string
    """

    abbr = ""
    field_names = []
    scoring_field_names = []
    csv_file_name = ""
    fantasy_point_multiplers = {"PassYds":0.04,"PassTD":4.0,"RecYds":0.1,
                                "RecTD":6.0,"Rec":0.5,"RushYds":0.1,
                                "RushTD":6.0,"Int":-2.0,"Lost":-2.0}

    def __init__(self,name):
        self.name = name
        self.csv_path = os.path.join(CSV_DIR,self.csv_file_name)
        self.stats = {year:{} for year in YEAR_LIST}
        with open(self.csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for year in YEAR_LIST:
                for row in reader:
                    if row["Player"]== self.name:
                        self.stats[row["Year"]][row["WK"]]=row

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
        if field not in self.field_names:
            print ("Not a valid field. Please choice from: \n%s"
                   % self.field_names)
            return
        elif type(weeks)!=list or [type(item)!=str for item in weeks]==[True for i in range(len(weeks))]:
            print "Not a valid argument for weeks, it must be a list of strings or left blank for the entire season"
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
        if self.stats[year][week]["Game Date"]=="Bye":
            return "Bye"

        points = 0.0
        for field in self.scoring_field_names:
            if self.stats[year][week][field] != "--":
                points += (float(self.stats[year][week][field])*
                           self.fantasy_point_multiplers[field])
            else:
                continue
        return points

    def ppg_average(self,year):
        """
        Returns the average points per game for a given year

        Keyword Arguments:
        year - the year as a string
        
        """
        week_list = self.stats[year].keys()
        week_totals = []
        if week_list == []:
            return 0.00
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
        week_list = self.stats[year].keys()
        week_variance = []
        if week_list == []:
            return ("Did Not Play in {}".format(year),0) #the player didn't play this year
        average = self.ppg_average(year)
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
    scoring_field_names = ["FGM"]
    csv_file_name = "KStats.csv"

class Defense(Player):
    """ Defensive Matchup """
    abbr = "DEF"
    field_names = ["Players","RushAtt","RushYds","RushTD","PassAtt",
                   "PassYds","PassTD","FGBlk","FGAtt","FGM","Home","Rival","Score"]

    def __init__(self,name):
        self.name = name
        self.csv_path = os.path.join(CSV_DIR,self.csv_file_name)
        self.stats = {year:{week:{field:0.0 for field in self.field_names} for week in WEEK_LIST} for year in YEAR_LIST}
        for year in YEAR_LIST:
            for week in WEEK_LIST:
                opponent_list = find_opponents(self.name,week,year)
                #this creates a list of player classes of the opponents
                opponent_class_list = []
                
                for (player,pos) in opponent_list:
                    opponent_class_list += generate_class_list(pos,[player])

                for player in opponent_class_list:
                    for field in self.field_names:
                        if field in player.field_names:
                            val = player.stats[year][week][field]
                            if val == "--":
                                continue
                            else:
                                self.stats[year][week][field] += float(val)


                self.stats[year][week]["Players"] = opponent_list
                
                if '@' in player.stats[year][week]["Opp"]:
                    self.stats[year][week]["Home"] = True
                else:
                    self.stats[year][week]["Home"] = False

