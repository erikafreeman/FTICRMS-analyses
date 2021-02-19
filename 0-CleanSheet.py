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



for i, val in enumerate(FormAtt.columns.values):
    if project_name in val:
        site_code = val.split('_')[5]
        FormAtt = FormAtt.rename(columns = {val: site_code})


FormAtt_Clean = pd.DataFrame.drop(FormAtt, columns= 'id', axis=1)
listClean = list(FormAtt_Clean.iloc[:,63:].columns)
listAll = listClean + ['formula_isotopefree']
print(listAll)
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
