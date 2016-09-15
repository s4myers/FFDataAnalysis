import sys
sys.path.append("~/Projects/FFDataAnalysis/scripts/")
from PlayerAnalysis import *


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

def cost_filter(pos,low,high):
    """
    Filters players according Draft Kings salary list
    
    Keyword Arguments:
    pos - the position to filter as a string, e.g. "QB","RB",etc.
    low - the lower threshold of player cost as a integer
    high - the upper  threshold of player cost as a integer
    """
    player_list = [name for name in SALARIES[pos].keys()
                   if (SALARIES[pos][name][0] > low and 
                       SALARIES[pos][name][0] < high)]
    return player_list

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

def join_combinations(combos_list):
    """
    Combines the player combinations to return a lineup of classes.
    
    Keyword Arguments:
    combos_list - a list of player_combos list
    """
    joined = []
    if len(combos_list) == 2:
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                joined.append(item1+item2)
    elif len(combos_list) == 3:
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    joined.append(item1+item2+item3)
    elif len(combos_list) == 4:
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    for item4 in combos_list[3]:
                        joined.append(item1+item2+item3+item4)
    elif len(combos_list) == 5:
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    for item4 in combos_list[3]:
                        for item5 in combos_list[4]:
                            joined.append(item1+item2+item3+item4+item5)
    else:
        print "Invalid len of list"
        return
    return joined

def lineup_cost(lineup):
    """
    The cost of the lineup according to DraftKings.com
    
    Keyword Arguments:
    lineup = a list of player classes
    """
    price = 0
    for player in lineup:
        pos = player.abbr
        price+=SALARIES[pos][player.name][0]
    return price

def matchup_history(player,opp):
    """
    Returns matchup history against particular a particular team. Returns
    the Average points scored, standard deviation, max, min, and
    last game points.
    
    Keyword Arguments:
    player - Player class object
    opp - opponent as the city, e.g. CHI, IND, etc.
    """
    ppg_total = []
    prev_games = []
    for year in player.stats.keys():
        for week in player.stats[year].keys():
            opp_check = player.stats[year][week]["Opp"]
            played = player.stats[year][week]["G"]
            if '@' in opp_check:
                opp_check = opp_check[1:]
                
            if opp_check==opp and played == '1':
                points = player.week_points(week,year)
                ppg_total.append(points)
                prev_games.append((week,year))
            else:
                continue
    ppg_total = np.array(ppg_total)            
    average = np.average(ppg_total)
    std = np.std(ppg_total)
    high = np.max(ppg_total)
    low = np.min(ppg_total)
    games_played = len(ppg_total)
    
    return average,std,high,low,games_played,ppg_total[0],prev_games[0]

def points_allowed(ppr = 0.0, past = True,rookies = False):
    """
    Generate a nested dictionary of all the for past points allowed to positions by team.
    """
    csv_path = os.path.join(CSV_DIR,"QBStats.csv")
    if ppr == 0.0:
        suffix = ".p"
    elif ppr == 0.5:
        suffix = "HalfPoint.p"
    elif ppr == 1.0:
        suffix = "FullPoint.p"
    else:
        print "Invalid PPR value"
        return
        
    if past == True:
        years = [y for y in YEAR_LIST[:-1]]
        rookie_file = "PastPointsAllowedRookies" + suffix
        vet_file = "PastPointsAllowed" + suffix
    else:
        years = [YEAR_LIST[-1]]
        rookie_file = "CurrentPointsAllowedRookies" + suffix
        vet_file = "CurrentPointsAllowed" + suffix
    if rookies:
        pickle_path = os.path.join(PICKLE_DIR,rookie_file)
        rookie_dict = pickle.load(open(os.path.join(PICKLE_DIR,"RookieDict.p"),"rb"))
    else:    
        pickle_path = os.path.join(PICKLE_DIR,vet_file)
    try:
        if past != True:
            csvtime = os.path.getmtime(csv_path)
            pickletime = os.path.getmtime(pickle_path)
            delta = csvtime-pickletime
            if delta > 0:   #checks to see if the csv data has been recently modified
                raise IOError
        else:        
            temp_dict = pickle.load(open(pickle_path,"rb"))
    except IOError:
        temp_dict = {year:{pos:{team:0.0 for team in TEAM_LIST}
                       for pos in POS_LIST}
                       for year in years}

        for pos in POS_LIST:
            if rookies:
                player_list = []
                for y in rookie_dict[pos].keys():
                    player_list+=rookie_dict[pos][y]
                class_list = generate_class_list(pos,player_list)
            else:    
                player_list = generate_player_list(pos)
                class_list = generate_class_list(pos,player_list)
        
            for year in years:
                for player in class_list:
                    player.fantasy_point_multipliers["Rec"] = ppr
                    for week in WEEK_LIST:
                        points = player.week_points(week,year,ppr)
                        if points == "Bye" or points == "No Data":
                            continue    
                        else:
                            team = player.stats[year][week]["Opp"]    
                    
                            if '@' in team:
                                team = team[1:]
                            
                            if team == "JAX":
                                team = "JAC"

                            if team == "LA":
                                team = "STL"

                                
                            temp_dict[year][pos][team] += points
                
                # average the total points
                for team in TEAM_LIST:
                    d = Defense(team)
                    tot_games = d.games_played(year)
                    p = float(temp_dict[year][pos][team])
                    temp_dict[year][pos][team]=p/tot_games
            
            pickle.dump(temp_dict,open(pickle_path,"wb"))

    return temp_dict

def player_combinations(pos,player_list,num):
    """
    Creates a list of player combinations based on the 
    number of slots needed filled. Returns a list of tuples, where
    each tuple contains PlayerClass objects.
    
    Keyword Arguments:
    pos - the player position; e.g. "QB", "RB", etc.
    player_list - a list of player to combine
    num - the number of players to group into pairs,triples,quartets
    """
    player_classes = generate_class_list(pos,player_list)
    player_combos = []
    
    if num == 1:
        player_combos = [[c] for c in player_classes]
    elif num == 2:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    player_combos+=[[player_classes[l],
                                     player_classes[m]]]      
    elif num == 3:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    for n in range(len(player_list)):
                        if n>m:
                            player_combos+=[[player_classes[l],
                                             player_classes[m],
                                             player_classes[n]]]      
    elif num == 4:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    for n in range(len(player_list)):
                        if n>m:
                            for p in range(len(player_list)):
                                if p>n:
                                    player_combos+=[[player_classes[l],
                                                     player_classes[m],
                                                     player_classes[n],
                                                     player_classes[p]]]
    else:
        print "Choose a number from 2-4"
        return 
    
    return player_combos

def player_score(player,ppr=0.0):
    """
    Gives a player a score based on whatever wack-a-do things we think
    are important.
    
    Keyword Arguments:
    player - Player class object
    """
    last_year = YEAR_LIST[-2]
    this_year = YEAR_LIST[-1]
    pos = player.abbr
    name = player.name
    opp = SALARIES[pos][name][1]
    weeks = 1
    curr_ppg = player.ppg_average(this_year,ppr)
    # If the player is a rookie, give them a past_ppg and points allowed
    # according to last year Rookie 
    if name in ROOKIES[pos][this_year]:
        rookie = True
        if ppr == 0.0:
            #past_allowed = PAST_POINTS_ALLOWED_ROOKIES[last_year][pos][opp]/16
            past_ppg = ROOKIE_AVERAGE["PPG"][last_year][pos]
        if ppr == 0.5:
            #past_allowed = PAST_POINTS_ALLOWED_ROOKIES_HALF[last_year][pos][opp]/16
            past_ppg = ROOKIE_AVERAGE_HALF["PPG"][last_year][pos]
        else:
            #past_allowed = PAST_POINTS_ALLOWED_ROOKIES_FULL[last_year][pos][opp]/16
            past_ppg = ROOKIE_AVERAGE_FULL["PPG"][last_year][pos]
    else:
        past_ppg = player.ppg_average(last_year,ppr)
    # Points allowed according to PPR settings
    if ppr == 0.0:
        past_allowed = PAST_POINTS_ALLOWED[last_year][pos][opp]/16
        curr_allowed = CURR_POINTS_ALLOWED[this_year][pos][opp]/weeks
    if ppr == 0.5:
        past_allowed = PAST_POINTS_ALLOWED_HALF[last_year][pos][opp]/16
        curr_allowed = CURR_POINTS_ALLOWED_HALF[this_year][pos][opp]/weeks
    else:
        past_allowed = PAST_POINTS_ALLOWED_FULL[last_year][pos][opp]/16
        curr_allowed = CURR_POINTS_ALLOWED_FULL[this_year][pos][opp]/weeks
    
    scores = np.array([past_ppg,past_allowed,curr_ppg,curr_allowed])
    if rookie:
        weights = np.array([.1,.4,.4,.1])
    else:
        weights = np.array([.4,.4,.1,.1])
    return np.sum(scores*weights)

def score_lineups(lineup_list,ppr=0.0,cost=True):
    """
    Scores each lineup according to player_score() function and then 
    returns a sorted list from High to low

    Keywork Arguments:
    lineup_list - the list of lineups to score
    """
    lineup_scores = []
    for l in lineup_list:
        if cost == True:
            l_cost = lineup_cost(l)
        tot_score = 0
        for p in l:
            tot_score += player_score(p,ppr)
        lineup = [p.name for p in l]
        if cost == True:
            lineup_scores.append((tot_score,l_cost,lineup))
        else:
            lineup_scores.append((tot_score,lineup))
    return sorted(lineup_scores,reverse = True)