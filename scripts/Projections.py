from __future__ import print_function
import sys
sys.path.append("~/Projects/FFDataAnalysis/scripts/")
from PlayerAnalysis import *


def correlation(pos,year_list,var1,var2="PPG",plot=False):
    """
    Determines the correlation of the variables var1 and var2 for a given year.
    

    Parameters

    ----------
    pos : string
        The player position; e.g. "QB", "RB", etc.
    year_list : list
        a list of int
    var1 : string
        The first field in the correlation
    var2 : string, optional
        Default is `PPG`. The second field to test correlation.
        If `var2="PPG`, then correlation between var1 and PPG is determined.
    plot : bool, optional
        Default is `False`. If `True` it will return a plot of correlation data



    Returns

    -------
    r_list : list
        Return a list of tuples.  With the first element being the r value
        and the second the year

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
        r_list +=[(r,year)]

        if plot == True:
            fig, ax = plt.subplots()
            plt.scatter(x,y)
            plt.xlabel(var1)
            plt.ylabel(var2)
            plt.title("%s vs %s"%(var1,var2))
            plt.tight_layout()
            plt.show()


    return r_list


def weekly_filter(week,pos,low,high,num=10,ppr=0.0,no_touch=[]):
    """
    Filters players according Draft Kings salary list. Then scores the players
    according to the algorithm
    
    Parameters

    ----------
    week : int
        the week of interest
    pos : string
        the position to use as a filter.
    low : int
        the lower threshold of player cost.
    high : int
        the upper threshold of player cost.
    num : int, optional
        Default is `10`. The number of players to return.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.
    no_touch : list, optional
        Default is an empty list. List of players to ignore when filtering



    Returns

    -------
    result : list
        Returns a sorted list of tuples. Each tuple includes (score,name,pos)

    """
    player_list = [name for name in SALARIES[week][pos].keys()
                   if (SALARIES[week][pos][name] > low and 
                       SALARIES[week][pos][name] < high) and name not in no_touch]
    c_list = generate_class_list(pos,player_list)
    score_list = [(player_score(c,ppr),c.name,c.abbr) for c in c_list]
    result = sorted(score_list,reverse = True)[:num]
    
    return result



def score_combinations(combos_list):
    """
    Combines the unque positional combinations into lineups which are then
    scored.
    
    Parameters

    ----------
    combos_list : list 
        A list of postional combinations which are generated by the
        the player_combinations function.



    Returns:

    --------
    joined : list
        Each item in the list is a result from running the score_lineup
        function.

    """
    joined = []
    #numerator = 0.0
    if len(combos_list) == 2:
        #denominator = len(combos_list[0])*len(combos_list[1])
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                joined.append(score_lineup(item1+item2))
                #numerator+=1
                #percent = (numerator/denominator)*100
                #print("{0:.2f}% complete".format(percent),end="\r")
    elif len(combos_list) == 3:
        #denominator = len(combos_list[0])*len(combos_list[1])*len(combos_list[2])
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    joined.append(score_lineup(item1+item2+item3))
                    #numerator+=1
                    #percent = (numerator/denominator)*100
                    #print("{0:.2f}% complete".format(percent),end="\r")
    elif len(combos_list) == 4:
        #denominator = (len(combos_list[0])*len(combos_list[1])*
                       #len(combos_list[2])*len(combos_list[3]))
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    for item4 in combos_list[3]:
                        joined.append(score_lineup(item1+item2+item3+item4))
                        #numerator+=1
                        #percent = (numerator/denominator)*100
                        #print("{} of {} lineups complete".format(numerator,denominator),end="\r")
    elif len(combos_list) == 5:
        #denominator = (len(combos_list[0])*len(combos_list[1])*
                       #len(combos_list[2])*len(combos_list[3])*len(combos_list[4]))
        for item1 in combos_list[0]:
            for item2 in combos_list[1]:
                for item3 in combos_list[2]:
                    for item4 in combos_list[3]:
                        for item5 in combos_list[4]:
                            joined.append(score_lineup(item1+item2+item3+item4+item5))
                            #numerator+=1
                            #percent = (numerator/denominator)*100
                            #print("{0:.2f}% complete".format(percent),end="\r")
    else:
        print("Invalid len of list")
        return
    return joined


def lineup_cost(week,lineup):
    """
    Determine cost of a lineup according to DraftKings.com
    
    Parameters

    ----------
    lineup : list
        A list of tuples `(score,name,pos)`. 



    Returns

    -------
    week : int
        The week of interest.
    price : int
        The total cost of the lineup according to DraftKings.com pricing.

    """
    price = 0
    for score,player,pos in lineup:
        price += SALARIES[week][pos][player]
    return price


def matchup_history(player,opp,ppr=0.0):
    """
    The matchup history against for a player against a particular team.

    
    Parameters

    ----------
    player : class obect
        The Player class object.
    opp : string
        The city designation of the opponent of interest, e.g. CHI, IND, etc.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.



    Returns

    -------
    results : tuple
        Returns a tuple whose item 1 is the average points, item 2 highest 
        point total scored, item 3 is the lowest point total scored, 
        item 4 is the total times played since 2010, and item 5 the last 
        points scored against the opponent.

    """
    ppg_total = []
    prev_games = []
    for year in player.stats.keys():
        for week in player.stats[year].keys():
            opp_check = player.stats[year][week]["Opp"]
            played = player.stats[year][week]["G"]
            if '@' in opp_check:
                opp_check = opp_check[1:]
                
            if opp_check==opp and played:
                points = player.week_points(week,year,ppr)
                ppg_total.append(points)
                prev_games.append((week,year))
            else:
                continue
    games_played = len(ppg_total)
    if games_played == 0:
        return 0,0,0,0,0
    else:    
        ppg_total = np.array(ppg_total)            
        average = np.average(ppg_total)
        high = np.max(ppg_total)
        low = np.min(ppg_total)
        results = (average,high,low,games_played,ppg_total[0])
        return results

def pa_to_pos(this_year,pos,opp,wts,ppr=0.0,rookie=False):
    """
    Find the points allowed to a position by an opponent

    Parameters

    ----------
    this_year : int
        The current four digit year.
    pos : string
        The player position.
    opp : string
        The city designation of the opponent of interest, e.g. CHI, IND, etc.
    wts : array_like
        An array containing the weights for averaging the past and
        current points allowed data.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.
    rookie : bool, optional
        Default is `False`.  If `True` it will return the points allowed 
        specially to rookies at the given position.



    Returns

    -------
    allowed_score : float
        Returns a float value which is the weighted average of both points 
        allowed for last year and the current year.

    """

    last_year = this_year-1
    if rookie:
        if ppr == 0.0:
            past_allowed = PAST_POINTS_ALLOWED_ROOKIES[last_year][pos][opp]
            curr_allowed = CURR_POINTS_ALLOWED[this_year][pos][opp]
        if ppr == 0.5:
            past_allowed = PAST_POINTS_ALLOWED_ROOKIES_HALF[last_year][pos][opp]
            curr_allowed = CURR_POINTS_ALLOWED_HALF[this_year][pos][opp]
        else:
            past_allowed = PAST_POINTS_ALLOWED_ROOKIES_FULL[last_year][pos][opp]
            curr_allowed = CURR_POINTS_ALLOWED_FULL[this_year][pos][opp]
    if ppr == 0.0:
        past_allowed = PAST_POINTS_ALLOWED[last_year][pos][opp]
        curr_allowed = CURR_POINTS_ALLOWED[this_year][pos][opp]
    if ppr == 0.5:
        past_allowed = PAST_POINTS_ALLOWED_HALF[last_year][pos][opp]
        curr_allowed = CURR_POINTS_ALLOWED_HALF[this_year][pos][opp]
    else:
        past_allowed = PAST_POINTS_ALLOWED_FULL[last_year][pos][opp]
        curr_allowed = CURR_POINTS_ALLOWED_FULL[this_year][pos][opp]
    allowed = np.array([past_allowed,curr_allowed])
    allowed_score = np.average(allowed,weights=wts)
    return allowed_score


def points_allowed(ppr = 0.0, past = True,rookies = False):
    """
    Generate a nested dictionary of all the for past points allowed 
    to positions by team.

    Parameters

    ----------
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.
    past : bool, optional
        Default is `True`.  If `past = False`, then it generates the points
        allowed for the current year.
    rookies : bool, optional
        Default is `False`.  If `rookies = True`, then it generates points 
        allowed to only rookies.



    Returns

    -------
    temp_dict : dictionary
        Temp_dict is a nested dictionary for average points allowed. The
        average points allowed is a float value. 
        e.g. temp_dict[year][pos][team] = float

    """
    csv_path = os.path.join(CSV_DIR,"QBStats.csv")
    if ppr == 0.0:
        suffix = ".p"
    elif ppr == 0.5:
        suffix = "HalfPoint.p"
    elif ppr == 1.0:
        suffix = "FullPoint.p"
    else:
        print("Invalid PPR value")
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
        temp_dict = pickle.load(open(pickle_path,"rb"))
    except (IOError,OSError):
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

                            temp_dict[year][pos][team] += points
                
                # average the total points
                for team in TEAM_LIST:
                    d = Defense(team)
                    tot_games = d.games_played(year)
                    p = temp_dict[year][pos][team]
                    temp_dict[year][pos][team]=p/tot_games
        
            pickle.dump(temp_dict,open(pickle_path,"wb"))
    return temp_dict


def player_combinations(pos,player_list,num):
    """
    Creates a list of player combinations based on the 
    number of slots needed filled from a list of players.
    
    Parameters

    ----------
    pos : string
        The player position; e.g. "QB", "RB", etc.
    player_list : list
        A list of players to combine
    num : int
        The group size of `1`,`2`,`3`, or `4`


    Returns

    -------
    player_combos : list
        A nested list of lists. The inner list contains the unique combination
        of players. The outer list contains the total combinations.

    """
    player_combos = []
    
    if num == 1:
        player_combos = [[p] for p in player_list]
    elif num == 2:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    player_combos+=[[player_list[l],
                                     player_list[m]]]      
    elif num == 3:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    for n in range(len(player_list)):
                        if n>m:
                            player_combos+=[[player_list[l],
                                             player_list[m],
                                             player_list[n]]]      
    elif num == 4:
        for l in range(len(player_list)):
            for m in range(len(player_list)):
                if m>l:
                    for n in range(len(player_list)):
                        if n>m:
                            for p in range(len(player_list)):
                                if p>n:
                                    player_combos+=[[player_list[l],
                                                     player_list[m],
                                                     player_list[n],
                                                     player_list[p]]]
    else:
        print("Choose a number from 2-4")
        return 
    
    return player_combos


def player_score(player,week,ppr=0.0,GAME_THRESH=4.0):
    """
    Gives a player a score based on whatever wack-a-do things we think
    are important.
    
    Parameters

    ----------
    player : class object
        The Player class object.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.
    GAME_THRESH : float
        Default is `4.0`. This value is used for determining the weights
        for finding the production and points allowed scored.



    Returns

    -------
    score : float
        The score is the average of the production score 
        and the points allowed score

    """
    
    this_year = YEAR_LIST[-1]
    last_year = this_year-1
    pos = player.abbr
    team = find_team(player,this_year)
    opp,where = SCHEDULE[team][week]
    
    #Determine weights
    gp = player.games_played(week,this_year)
    if gp >= GAME_THRESH:
        weights = np.array([0.0,1.0])
    else:
        w1 = (GAME_THRESH - gp)/GAME_THRESH
        w2 = gp/GAME_THRESH
        weights = np.array([w1,w2])
    
    production = production_score(player,this_year,weights,ppr)
    allowed = pa_to_pos(this_year,pos,opp,weights,ppr)
    m_avg,m_high,m_low,m_gp,m_last = matchup_history(player,opp,ppr)
    #####Lower the influence to points allowed to WR#####
    if player.abbr == "WR":
        temp_weight = np.array([.75,.25])
        score = np.average(np.array([production,allowed]),weights=temp_weight)
    else:
        score = np.average(np.array([production,allowed]))
    return score


def production_score(player,this_year,wts,ppr=0.0):
    """
    Find the points allowed to a position by an opponent

    Parameters

    ----------
    player : class object
        The Player class object
    this_year : int
        The current four digit year.
    wts : array_like
        An array containing the weights for averaging the past and
        current points allowed data.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.


    Returns

    -------
    production_score : float
        Returns a float value which is the weighted average of both average
        points scored for last year and the current year.

    """

    last_year = this_year-1
    pos = player.abbr
    name = player.name
    
    if name in ROOKIES[pos][this_year]:
        past_ppg = rookie_ppg_average(last_year,pos,ppr)
    else:
        past_ppg = player.ppg_average(last_year,ppr)
        if past_ppg == 0.0:
            y = str(int(last_year)-1)
            past_ppg = player.ppg_average(y,ppr)
            if past_ppg == 0.0:
                past_ppg = rookie_ppg_average(last_year,pos,ppr)
    curr_ppg = player.ppg_average(this_year,ppr)            
    
    points = np.array([past_ppg,curr_ppg])
    production_score = np.average(points,weights=wts)

    return production_score



def rookie_ppg_average(last_year,pos,ppr=0.0):
    """
    Gives average points scored by a rookie at a given position. It 
    is used to assign a past points for game for rookies who we have
    no data on.

    Parameters

    ----------
    last_year : string
        This is the previous four digit year.
    pos : string
        The position of the player.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.       

    """
    if ppr == 0.0:
        past_ppg = ROOKIE_AVERAGE["PPG"][last_year][pos]
    if ppr == 0.5:
        past_ppg = ROOKIE_AVERAGE_HALF["PPG"][last_year][pos]
    else:
        past_ppg = ROOKIE_AVERAGE_FULL["PPG"][last_year][pos]
    return past_ppg


def score_lineup(week,lineup,cost_thresh=41200,cost = True):
    """
    Gives a total score for a lineup based on our algorithm.

    Parameters

    ----------
    week : int
        The week of interest.
    lineup : list
        A list of tuples `(score,name,pos)`.
    cost : bool, optional
        Default is `True`. If `True, then cost of the lineup 
        according DraftKings.com is also included; otherwise,
        the lineup cost is omited.



    Returns

    -------
    lineup_score : tuple
        Item 1 is the total score of the lineup.  If `cost=True`,
        then item 2 is the total cost and item 3 is the list of
        player names in the lineup.  If `cost = False`, then
        item 2 is the list of player names in the lineup, and
        there is no third item.

    """
    
    tot_score = 0.0
    tot_cost = 0
    players = []
    for score,name,pos in lineup:
        tot_score += score
        tot_cost += SALARIES[week][pos][name]
        players.append(name)
        #if tot_cost > cost_thresh:
        #    return (0,0,0)
        #else:
        #    continue    
    if cost == True:
        lineup_score = (tot_score,tot_cost,players)
    else:
        lineup_score = (tot_score,players)
    return lineup_score

################## Functions related to new Projection #########################
def compare_and_return(player_val,opponent_val,thresh=.3):
    """
    Compares two values to find a percentage difference.

    Parameters

    ----------
    player_val : float
        A player's average value of some field.
    opponent_value : float
        The opponent's average value of the same field.
    thresh : float, optional
        The threshold for the percent difference



    Returns

    -------
    result : float
        The result value is dependant on the percentage difference of
        the field value. If percent differnce is less than the `thresh`,
        the mean of the two values is returned.  If greater than the
        thresh a weighted average is returned.

    """
    numer = abs(player_val - opponent_val)
    denom = (player_val + opponent_val)/2
    percent_diff = numer/denom
    
    ary = np.array([player_val,opponent_val])
    x = .5*(1+percent_diff)
    y = 1-x
    if percent_diff < thresh:
        wt = np.array([.5,.5]) #equal weight
    elif percent_diff >=1.0:
        x = 1.0
        y = 0.0

    if player_val < opponent_val:
        wt = np.array([x,y])
    else:
        wt = np.array([y,x])
    result = np.average(ary,weights=wt)
    return result


def points_from_projection(player,proj,ppr=0.0):
    """
    Determine points from projected statistics.

    Parameters

    ----------
    player : class object
        The Player class object.
    proj : dictionary
        A dictionary contain the projected statistics.
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.



    Return

    ------
    points : float
        The fantasy point total based on the projection.

    """
    points = 0.0
    pos = player.abbr
    player.fantasy_point_multipliers["Rec"]=ppr
    
    for field,value in proj.items():
        points+=player.fantasy_point_multipliers[field]*value
    return points


def field_percentage(player,field,week,year):
    """
    Compares field totals by pos to get a percentage breakdown.

    Parameters

    ----------
    player : class object
        The player class object.
    field : string
        The field of interest, e.g. "PassTD","Rec", etc.
    week : int
        Determines the last week in the week range.
    year : int
        The four digit year.



    Return

    ------
    percent : float
        The return value ranges from 0.0 to 1.0. The purpose of the
        function is to properly distribute a field total allowed by
        the opponent to each player of a particular position.
            
    """
    w_list  = range(1,week+1)
    team = find_team(player,year)
    pos = player.abbr
    others = []
    for n,p in ROSTERS[year][team]:
        if p == pos and n != player.name:
            others.append(n)
    if others == []:
        percent = 1.0
    else:
        c_list = generate_class_list(pos,others)
        other_tot = 0.0
        for c in c_list:
            try:
                other_tot+=c.total(field,year,weeks=w_list)
            except KeyError:
                continue
                
        p_tot = player.total(field,year,weeks=w_list)
        denom = other_tot+p_tot
        if denom == 0.0:
            percent = 0.0
            return percent
        
        percent = p_tot/denom
    
    return percent


def find_team(player,year):
    """
    Find a player's team.  
    *Currently only works for 2015,2016 and players not on suspension.
    *I manually added some players to ROSTERS.

    Parameters

    ----------

    player : class object
        The Player class object.
    year : string
        The four digit year *Currently only works for 2015, 2016.



    Return

    ------
    team : string
        The player's team name.

    """
    name = player.name
    pos = player.abbr
    
    for team in TEAM_LIST:
        if (name,pos) in ROSTERS[year][team]:
            return team
        else:
            continue
    return "Free Agent or Suspended"


def player_field_averages(player,week,year):
    """
    Finds the average values for the below fields.

    Parameters

    ----------
    player : class object
        The Player class object.
    week : int
        Determines the last week in the week range.
    year : string
        The four digit year.



    Returns

    -------
    avg : dictionary
        A dictionary containing a player's average field values for 
        a specified year and week interval. 

    """
    w_list = range(1,week+1)
    avg = {}
    pos = player.abbr
    passing = ["PassAvg","PassAtt","PassYds","PassTD","Int","Sck"]
    rushing = ["RushAvg","RushAtt","RushYds","RushTD","Lost"]
    receiving = ["RecAvg","Rec","RecYds","RecTD"]
    if pos == "QB":
        fields = [x for x in passing +rushing]
    else:
        fields = [x for x in receiving+rushing]
    avg = {x:player.field_average(x,year,weeks=w_list) for x in fields}
    return avg


def opp_field_averages(p_avg,week,pos,opp,year):
    """
    Finds the average values for the below fields.

    Parameters

    ----------
    p_avg : dictionary
        A dictionary containing a player's average field values for 
        a specified year and week interval.
    week : int
        The defense averages up to the week parameter.
    pos : string
        The position of the player, e.g. "QB", "RB", etc.
    opp : string
        The opponent's team name, e.g. "Bears","Colts",etc.
    year : string
        The four digit year.



    Returns

    -------
    opp_avg : dictionary
        A dictionary containing the opponent's average allowed values 
        which correspond to the player's field.  
        
    """
    opp_avg={}
    for field in p_avg.keys():
        try:
            val = DEF_AVERAGES[year][week][pos][opp][field]
            opp_avg[field]=val
        except KeyError:
            continue
    return opp_avg


def projected_stats(player,player_avg,opp_avg,week,year,printout=False):
    """
    Creates projected stats for the week depending on the opponent's
    allowed averages and the player's performance throughout the 
    season.

    Parameters

    ----------
    player : class object
        The player class object.
    player_avg : dictionary
        A dictionary containing a player's average field values for 
        a specified year and week interval.
    opp_avg : dictionary
        A dictionary containing the opponent's average allowed values 
        which correspond to the player's field.
    year : string
        The four digit year.
    printout : bool, optional
        Default value is `False`. If `True`, then the function 
        will print the field modifiers.



    Return

    ------
    player_avg : dictionary
        A dictionary containing a player's projected game stats.

    """
    pos = player.abbr
    proj_stats ={}
    if player.abbr == "QB":
        qbf1 = "PassAtt"
        qbf2 = "PassTD"
        qbf3 = "Int"
        
        pass_att = np.mean([player_avg[qbf1],opp_avg[qbf1]])
        
        player_pass_avg = player_avg["PassAvg"]
        opp_pass_avg = opp_avg["PassYds"]/opp_avg[qbf1]
        
        pass_avg = np.mean([player_pass_avg,opp_pass_avg])
        #pass_avg = compare_and_return(player_pass_avg,opp_pass_avg)
        
        pass_yards = pass_att*pass_avg
        pass_td = np.mean([player_avg[qbf2],opp_avg[qbf2]])
        intercept = np.mean([player_avg[qbf3],opp_avg[qbf3]])
        #pass_td = compare_and_return(player_avg[qbf2],opp_avg[qbf2])
        #intercept = compare_and_return(player_avg[qbf3],opp_avg[qbf3])
        
        proj_stats["PassYds"] = pass_yards
        proj_stats[qbf2] = pass_td
        proj_stats[qbf3] = intercept
         
    else:
        f1 = "Rec"
        f2 = "RecTD"
        mod1 = field_percentage(player,f1,week-1,year)
        mod2 = field_percentage(player,f2,week-1,year)
        
        rec = mod1*opp_avg[f1]
        rec_avg = player_avg["RecAvg"]
        rec_yards = rec*rec_avg
        if mod2 != 0.0:
            rec_td = mod2*opp_avg[f2]
        else:
            rec_td = mod1*opp_avg[f2]
        
        if printout:
            print("rec modifier ",mod1)
            print("rectd modifier ",mod2)
        
        proj_stats["RecYds"] = rec_yards
        proj_stats[f1] = rec
        proj_stats[f2] = rec_td
        
    f3 = "RushAtt"
    f4 = "RushTD"
    
    mod3 = field_percentage(player,f3,week-1,year)
    mod4 = field_percentage(player,f4,week-1,year)
    #w = np.array([1.0,1.0-mod3])
    rush_att = player_avg[f3]
    player_rush_avg = player_avg["RushAvg"]
    try:
        opp_rush_avg = opp_avg["RushYds"]/opp_avg[f3]
    except ZeroDivisionError:
        opp_rush_avg = 0.0

    rush_avg = np.average([player_rush_avg,opp_rush_avg])
    rush_yds = rush_att*rush_avg
    
    if mod4 != 0.0:
        rush_td = mod4*opp_avg[f4]
    else:
        rush_td = mod3*opp_avg[f4]
    
    if printout:
            print("rush att modifier ",mod3)
            print("rush td modifier ",mod4)
            
    proj_stats["RushYds"]=rush_yds
    proj_stats[f4] = rush_td
    
    return proj_stats


def projected_points(player,week,year,ppr=0.0,
                     printout=False):
    """
    Find a player's projected week score.

    Parameters

    ----------
    player : class object
        The Player class object.
    year : int
        The four digit year.
    week : int
        Integer value of the week number from 1 - 17
    ppr : float, optional
        Default is `0.0`. Scoring parameter for points per reception.
    weeks : string or list, optional
            By default the string "ALL" means to average a field for
            all the weeks in a year.  If a list of integers ranging from 1-17
            is given, then only the stats corresponding to those weeks
            will be added to the array.
    printout : bool, optional
        Default value is `False`. If `True`, then the function 
        will print the field modifiers.



    Return

    ------
    projected_points : float
        The player's projected point total.

    """
    
    #home = player.find_home_games(year)
    #away = [x for x in player.stats[year].keys() if x not in home]
    pos = player.abbr
    name = player.name
    team = find_team(player,year)
    opp,where = SCHEDULE[team][week]
    
    
    p_avg = player_field_averages(player,week-1,year)
    opp_avg = opp_field_averages(p_avg,week-1,pos,opp,year)
    projection = projected_stats(player,p_avg,opp_avg,week,year,printout)
    projected_points = points_from_projection(player,projection,ppr)
    
    return projected_points