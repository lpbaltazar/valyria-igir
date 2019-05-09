import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

def sliceDataframe(precincts, order, slicer):
	t = slicer*order
	precincts_included = precincts[:t]
	tranmission = data.loc[data.PRECINCT_CODE.isin(precincts_included)]
	tranmission.to_csv("unprocessed/dummy/results_"+str(order-1)+".csv", index=False)

#file = "raw-data/results_nle2016M12_17052016_1145.txt"
file ="unprocessed/results.csv"
data = pd.read_csv(file, sep=",", encoding = 'utf-8', dtype = {'PRECINCT_CODE':str})



"""data.columns = ["PRECINCT_CODE", "CONTEST_CODE", "CANDIDATE_NAME", 
				"PARTY_CODE", "VOTES_AMOUNT", "TOTALIZATION_ORDER",
				"NUMBER_VOTES", "UNDERVOTE", "OVERVOTE", "RECEPTION_DATE"]"""

precincts = data.PRECINCT_CODE.unique()


slicer = int(len(precincts)*.2)

for i in range(1,6):
	print(i)
	sliceDataframe(precincts, i, slicer)
