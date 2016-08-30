import sys
sys.path.append("~/Projects/FFDataAnalysis/scripts/")
from Player_Analysis import *
import scipy.stats as stats



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


def past_points_allowed():
    """
    Generate a nested dictionary of all the for past points allowed to positions by team.
    """
    pickle_path = os.path.join(PICKLE_DIR,"PastPointsAllowed.p")
    try:
        temp_dict = pickle.load(open(pickle_path,"rb"))
    except IOError:
        temp_dict = {year:{pos:{team:0.0 for team in TEAM_LIST}
                       for pos in POS_LIST}
                for year in YEAR_LIST}
        #print temp_dict

        for pos in POS_LIST:
            
            player_list = generate_player_list(pos)

            class_list = generate_class_list(pos,player_list)

            for year in YEAR_LIST:
                for player in class_list:
                    for week in WEEK_LIST:
                        points = player.week_points(week,year)
                        if points == "Bye" or points == "No Data":
                            continue    
                        else:
                            team = player.stats[year][week]["Opp"]    
                        
                            if '@' in team:
                                team = team[1:]
                            temp_dict[year][pos][team] += points
        pickle.dump(temp_dict,open(pickle_path,"wb"))

    return temp_dict


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
    elif pos == "DEF":
        class_list = [Defense(player) for player in player_list]
    else:
        return "Not a proper posistion"
    return class_list


def generate_rookies(pos_list):
    """
    Find all the rookies by position and year.  Using
    these players we create and the average rookie profile
    
    Keyword Arguments:
    pos_list - a list of positions
    """
    Rookies = {pos:{year:[] for year in YEAR_LIST[1:]} for pos in pos_list}
    base_year = YEAR_LIST[0]
    for pos in pos_list:
        csv_name = pos+"Stats.csv"
        csv_path = os.path.join(CSV_DIR,csv_name)
        old_name = ''
        old_year = ''
        with open(csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                new_name = row["Player"]
                new_year = row["Year"]
                if new_name == old_name and new_year == old_year:
                    continue
                elif new_name == old_name and new_year != old_year:
                    old_year = row["Year"]
                elif new_name != old_name and old_year == base_year:
                    old_name = row["Player"]
                    old_year = row["Year"]
                    continue
                elif old_name == '':
                    old_name = row["Player"]
                    old_year = row["Year"]
                else:
                    Rookies[pos][old_year].append(old_name)
                    old_name = row["Player"]
                    old_year = row["Year"]
    return Rookies


def generate_player_list(pos):
    """
    Create a list of all avaiable players at a desired position

    Keyword Arguments:
    pos - the position enter as a string; e.g. "QB", "RB", etc.

    """
    name_list =[]
    csv_path = os.path.join(CSV_DIR,"AllPlayers.csv")
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file,skipinitialspace=True)
        for row in reader:
            if row[0]==pos and row[1] not in name_list:
                name_list.append(row[1])
            else:
                continue
    return name_list