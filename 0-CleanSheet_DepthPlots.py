import sys 
import pandas as pd

'''
This block of code takes the sample name column and splits the name into something 
a bit more diggestible
'''
input_csv= '/home/erika/Desktop/likeliest_match.csv'
FormAtt= pd.read_csv(input_csv)

'project name is the fourth component of the sample string'
project_name = 'Canada' 

sample_list= []
for i, val in enumerate(FormAtt.columns.values):
    if project_name in val:
        site_code = val.split('_')[5]
        sample_list.append(site_code)
        FormAtt = FormAtt.rename(columns = {val: site_code})

samps = sample_list.copy()
sample_list.append('mz')
massframe= FormAtt[sample_list]
massframe= massframe.set_index('mz')

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
                                     for d_idx in range(massframe.columns.get_loc(dup).sum())]
                                    )

# FormAtt_Clean = pd.DataFrame.drop(FormAtt, columns= 'id', axis=1)
# listClean = list(FormAtt_Clean.iloc[:,63:].columns)
# listAll = listClean + ['formula_isotopefree']
# SampleFormulae = FormAtt_Clean[listAll]
# SampleFormulae = SampleFormulae.set_index('formula_isotopefree')
# #Samp = SampleFormulae.groupby(by=SampleFormulae.columns, axis=1).mean()
# Samp = SampleFormulae.copy()
# #
# SpeciesRichness = Samp.count(axis='columns')
# Samp = Samp.reset_index()
# SpeciesRichness.plot(kind='bar')

# TransForm = Samp.T
# TransForm.columns = TransForm.iloc[0]
# TransForm = pd.DataFrame.drop(TransForm, 'formula_isotopefree', axis=0)


# TransForm = TransForm.fillna(0)
# TransForm = TransForm.reset_index()
# new = TransForm['index'].str.split('(\d+)([A-Za-z]+)', n = 3, expand = True) 
# new['SiteName'] = new[0]+ new[1] 
# new = new.rename(columns={2: 'Position', 3: 'Depth'})
# ids = pd.DataFrame.drop(new, [0,1], axis=1)
# OTU_equivalent = pd.DataFrame.drop(TransForm, 'index', axis=1) 

# Formulae = TransForm.reset_index()
# Formulae = pd.DataFrame.drop(Formulae, 'index', axis=1) 
