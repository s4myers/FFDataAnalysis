import csv
import os

main_dir = "c:/Users/sean/Documents/GitHub/FFDataAnalysis/CSV_data"  #Change depending on save location
team_list =["BUF","MIA","NE","NYJ","BAL","CIN","CLE","PIT","HOU","IND","JAC","TEN","DEN","KC","OAK","SD","DAL","NYG","PHI","WAS","CHI","DET","GB","MIN","ATL","CAR","NO","TB","ARI","STL","SF","SEA"]
year_list = ["2010","2011","2012","2013","2014"]

class Player(object):
	"""An active roster player to research for your fantasy lineup.

	Attributes:
		name: The name of the player as a string
	"""

	abbr = ""
	field_names=[]
	csv_file_name =""

	def __init__(self,name,team):
		self.name = name
		self.team = team
		self.csv_path = os.path.join(main_dir,self.csv_file_name)

		# Generate stat data for the player organized by year
		self.stats={year:{} for year in year_list}
		with open(self.csv_path) as csv_file:
			reader = csv.DictReader(csv_file)
			for year in year_list:
				for row in reader:
					if row["Player"]== self.name:
						self.stats[row["Year"]][row["WK"]]=row


	def total(self,field,year,weeks=["all_weeks"]):
		""" 
		Totals the value of a given field by week or by season
		
		Keyword Arguments:
		field - The field to total as a string
		year - the year of interest as a string
		weeks - optional a tuple of strings, e.g: ["14","15","16"]

		"""
		tot = 0.0
		if field not in self.field_names:
			print "Not a valid field. Please choice from: \n%s" % self.field_names
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
				#try:
				#	int(week)
				#	continue
				#except ValueError:
				#	print "weeks in list should be strings of interger values"
				#	return	
				tot+=0.0 if (self.stats[year][week][field]=="--" or self.stats[year][week][field]=="") else float(self.stats[year][week][field])
			return tot
		except KeyError:
			print "No data available for this year or invalid weeks"		
			return


class QuarterBack(Player):
	""" Quarter back position """

	abbr = "QB"
	field_names = ["G","GS","Comp","PassAtt","Pct","PassYds","PassTD","Int","Sck","Rate","RushAtt","RushYds","RushTD","FUM","Lost"]
	csv_file_name ="QBStats.csv"

class RunningBack(Player):
	""" Running back position """

	abbr = "RB"
	field_names =["G","GS","RushAtt","RushYds","Avg","RushLng","RushTD","Rec","RecYds","Avg","RecLng","RecTD","FUM","Lost"]
	csv_file_name = "RBStats.csv"

class WideReceiver(Player):
	""" Wide receiver position """

	abbr = "WR"
	field_names =["G","GS","RushAtt","RushYds","RushAvg","RushLng","RushTD","Rec","RecYds","RecAvg","RecLng","RecTD","FUM","Lost"]
	csv_file_name = "WRStats.csv"

class TightEnd(Player):
	""" Tight end position """

	abbr = "TE"
	field_names =["G","GS","RushAtt","RushYds","RushAvg","RushLng","RushTD","Rec","RecYds","RecAvg","RecLng","RecTD","FUM","Lost"]
	csv_file_name = "TEStats.csv"	