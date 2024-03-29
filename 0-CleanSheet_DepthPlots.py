import sys 
import pandas as pd
import re
'''
This block of code takes the sample name column and splits the name into something 
a bit more digestible
'''
input_csv= '/home/erika/Desktop/likeliest_match.csv'
FormAtt= pd.read_csv(input_csv)


'project name is the fourth component of the sample string'
project_name = 'Canada' 

def func(row):
    if len(str(row))>1 and len(str(row))< 3:
        r = ''.join(x for x in row if x.isalpha())
        return r
    else:
        return row

sample_list= []
for i, val in enumerate(FormAtt.columns.values):
    if project_name in val:
        site_code = val.split('_')[5]
        sample_list.append(site_code)
        FormAtt = FormAtt.rename(columns = {val: site_code})


samps = sample_list.copy()
sample_list.append('formula_isotopefree')

'''
Just adding some lines here in order to export the calculated chemical metrics that correspond to function from the sheets. 

'''
chemlist = ['formula_isotopefree','homseries', 'totalc', 'H.C', 'O.C', 'C', 'H', 'O', 'N', 'S', 'P', 'Cl', 'Na', 'C13',
'O18', 'N15', 'S34', 'Cl37', 'Co', 'Cu.i', 'Cu.ii', 'Cu65.i',
'Cu65.ii', 'Fe.ii', 'Fe.iii', 'Fe54.ii', 'Fe54.iii', 'Br79', 
'Br81', 'Ni.ii', 'Ni60.ii', 'Zn.ii', 'Zn66.ii', 'I', 'MDL', 'ResPow', 'SE',
'present_in', 'AI', 'AI.mod', 'DBE', 
'Aromatic', 'Aromatic.O_rich', 'Aromatic.O_poor', 
'Highly.unsaturated', 'Highly.unsaturated.O_rich',
'Highly.unsaturated.O_poor', 'Unsaturated',
'Unsaturated.O_rich', 'Unsaturated.O_poor',
'Unsaturated.with.N', 'Saturated', 'Saturated.O_rich', 'Saturated.O_poor']
chemframe = FormAtt[chemlist]
chemframe.to_csv('/home/erika/Desktop/likeliest_match_chemframe.csv')

massframe= FormAtt[sample_list]
massframe= massframe.set_index('formula_isotopefree')
massframe= massframe.T.drop_duplicates().T

'''
Column's get_loc() function returns a masked array if it finds duplicates with 'True' 
values pointing to the locations where duplicates are found. I then use the mask to assign
new values into those locations. In my case, I know ahead of time how many dups I'm going
to get and what I'm going to assign to them but it looks like df.columns.get_duplicates()
would return a list of all dups and you can then use that list in conjunction with get_loc()
if you need a more generic dup-weeding action
'''
#dup weeding 
cols=pd.Series(massframe.columns)
for dup in massframe.columns[massframe.columns.duplicated(keep=False)]: 
    cols[massframe.columns.get_loc(dup)] = ([dup + '.' + str(d_idx) 
                                     if d_idx != 0 
                                     else dup 
                                     for d_idx in range(massframe.columns.get_loc(dup).sum())])
massframe.columns=cols


massframe.to_csv('/home/erika/Desktop/likeliest_match_mz.csv')

#number of peaks plot input
massframe= massframe.fillna(0)
massframe[massframe>1]=1
df_sum= massframe.sum(axis=0)
newdf= pd.DataFrame(df_sum, columns = ['n_peaks'])
newdf= newdf.reset_index()
newdf['Site']= newdf['index'].str.slice(start=0, stop=2)
newdf['Slope1']= newdf['index'].str.slice(start=2)
newdf['Slope2']= newdf['index'].str.slice(start=2, stop=3)
newdf['Depth1']= newdf['index'].str.slice(start=3)
newdf['Slope'] = newdf['Slope1'].where(newdf['Slope1'].str.contains('ST'), newdf['Slope2'])
newdf['Depth'] = newdf['Depth1'].where(newdf['Slope'].str.contains('ST'), newdf['Depth1'])


newdf['Depth']= newdf['Depth'].astype('str')

newdf['Depth'] = newdf['Depth'].apply(lambda x: 'Stream' if x.startswith('T') or x.startswith('ST') else x)
newdf.drop(['Slope1', 'Slope2', 'Depth1'], axis=1, inplace=True)
#string needs to be exact match to work properly
newdf['Slope'] = newdf['Slope'].replace({'\.1\b': '', '\.2\b': '', '\.3\b': ''}, regex=True)
newdf['Depth'] = newdf['Depth'].replace({'.1': '', '.2': '', '.3': ''}, regex=True)
#hacky solution to ST problem
newdf['Slope'].replace({"S": "1S", "B": "2B", "F": "3F", "T": '4T', 'ST':'5ST', 'ST1.1':'5ST' ,'ST2.1':'5ST', 'ST1':'5ST', 'ST2':'5ST', 'ST.1':'5ST' }, inplace=True)
print(newdf.iloc[98])

newdf.to_csv('/home/erika/Desktop/likeliest_match_abspres.csv')

fdata= SampleNames.set_index('SampleID')

FormAtt_Clean = pd.DataFrame.drop(FormAtt, columns= 'id', axis=1)
listClean = list(FormAtt_Clean.iloc[:,63:].columns)
listAll = listClean + ['formula_isotopefree']
SampleFormulae = FormAtt_Clean[listAll]
SampleFormulae = SampleFormulae.set_index('formula_isotopefree')
#Samp = SampleFormulae.groupby(by=SampleFormulae.columns, axis=1).mean()
Samp = SampleFormulae.copy()
#
SpeciesRichness = Samp.count(axis='columns')
Samp = Samp.reset_index()
SpeciesRichness.plot(kind='bar')

TransForm = Samp.T
TransForm.columns = TransForm.iloc[0]
TransForm = pd.DataFrame.drop(TransForm, 'formula_isotopefree', axis=0)


TransForm = TransForm.fillna(0)
TransForm = TransForm.reset_index()
new = TransForm['index'].str.split('(\d+)([A-Za-z]+)', n = 3, expand = True) 
new['SiteName'] = new[0]+ new[1] 
new = new.rename(columns={2: 'Position', 3: 'Depth'})
ids = pd.DataFrame.drop(new, [0,1], axis=1)
OTU_equivalent = pd.DataFrame.drop(TransForm, 'index', axis=1) 

Formulae = TransForm.reset_index()
Formulae = pd.DataFrame.drop(Formulae, 'index', axis=1) 