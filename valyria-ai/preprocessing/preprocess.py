import pandas as pd
import numpy as np
import warnings
import time
import os

warnings.filterwarnings('ignore')

def initialize(unprocessed_dir, processed_dir):
	contest = pd.read_csv(os.path.join(processed_dir, 'static/contests.csv'), encoding = 'utf-8')
	positions = ['SENATOR', 'GOVERNOR', 'VICE-GOVERNOR', 'MAYOR', 'VICE-MAYOR','PARTY LIST']
	codes = []
	for pos in positions:
	    mask = contest['CONTEST_NAME'].str.contains(pos)
	    codes_1 = contest.loc[mask]
	    codes.append(codes_1)
	codes = pd.concat(codes)

	candidates = pd.read_csv(os.path.join(processed_dir, 'static/candidates.csv'), encoding = 'utf-8')
	candidates = candidates.loc[candidates['CONTEST_CODE'].isin(codes['CONTEST_CODE'].values)]
	precincts = pd.read_csv(os.path.join(processed_dir, 'static/precincts.csv'), encoding = 'utf-8', dtype = {'VCM_ID':str})

	return codes, candidates, precincts

def prep_results(unprocessed_dir, precincts):
	df = pd.read_csv(os.path.join(unprocessed_dir,'results.csv'), encoding = 'utf-8', dtype = {'PRECINCT_CODE':str})
	df = df.merge(precincts, left_on = 'PRECINCT_CODE', right_on = 'VCM_ID', how = 'left')
	df = df.loc[df['REG_NAME'] != 'OAV']
	
	return df

def summarize_candidate(df, col, candidates):
	print('Summarizing...')
	s = time.time()
	summarized_candidate = pd.DataFrame(index = df[col].unique().tolist(), columns = candidates)
	grouped = df.groupby([col, 'CANDIDATE_NAME'])
	keys = grouped.groups.keys()
	for key in keys:
	    a = grouped.get_group(key)
	    summarized_candidate.loc[key[0]][key[1]] = a.VOTES_AMOUNT.sum()
	e = time.time()
	print('Total Duration of Summarization: ', e-s)
	summarized_candidate.index.name = col

	return summarized_candidate.reset_index()

def summarize(df, col, cols):
	summarized = pd.DataFrame(index = df[col].unique().tolist(), columns = cols)
	grouped = df.groupby(col)
	keys = grouped.groups.keys()
	for key in keys:
		a = grouped.get_group(key)
		a.drop_duplicates(subset = ['PRECINCT_CODE'], keep = 'first', inplace = True)
		for i in cols:
			summarized.loc[key][i] = a[i].sum()
	summarized.index.name = col
	return summarized.reset_index()

def save_file(df, outfile):
	print('Saving file')
	df.to_csv(outfile, encoding = 'utf-8', index = False)

def add_info(df, level, candidates, codes, outfile = False):
	df['LEVEL'] = level
	df = df.merge(candidates, left_on = 'variable', right_on = 'CANDIDATE_NAME', how = 'left')
	df = df.merge(codes, left_on = 'CONTEST_CODE', right_on = 'CONTEST_CODE', how = 'left')
	if outfile:
		save_file(df, outfile)

def transform(df, id_vars, value_vars, outfile = False):
	transformed = df.melt(id_vars = id_vars, value_vars=value_vars)
	if outfile:
		save_file(transformed, outfile)
	return transformed

if __name__ == '__main__':
	unprocessed_dir = os.path.abspath('../../unprocessed')
	processed_dir = os.path.abspath('../../processed')

	codes, candidates, precincts = initialize(unprocessed_dir, processed_dir)
	results = prep_results(unprocessed_dir, precincts)

	# summary = summarize(results, 'REG_NAME', ['NUMBER_VOTERS', 'UNDERVOTE', 'OVERVOTE'])
	# transform(summary, 'REG_NAME', ['NUMBER_VOTERS', 'UNDERVOTE', 'OVERVOTE'], 'REGION', 
	# 			candidates, codes, os.path.join(processed_dir, 'dynamic/etc.csv'))

	region_summary = summarize_candidate(results, 'REG_NAME', candidates.CANDIDATE_NAME.unique())
	region_summary = transform(region_summary, id_vars = ['REG_NAME'], value_vars = candidates.CANDIDATE_NAME.unique())
	add_info(region_summary, 'REGION', candidates, codes, os.path.join(processed_dir, 'dynamic/candidate_etc.csv'))