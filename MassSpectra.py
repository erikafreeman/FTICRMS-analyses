# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 11:38:58 2020

@author: ECF
"""

###Keeping this as a master of the code that I have already created. 

import sys 
import pandas as pd
from scipy.spatial import distance_matrix
from skbio.stats.ordination import pcoa
from skbio.diversity import alpha_diversity
from skbio.diversity import beta_diversity
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns
sns.set_style("white")
df = sns.load_dataset('iris')
from mpl_toolkits.mplot3d import axes3d, Axes3D


'project name is the fourth component of the sample string'
project_name = 'Canada' 
input_csv= '/home/erika/Desktop/likeliest_match.csv'
FormAtt= pd.read_csv(input_csv)


'''
This block of code takes the sample name column and splits the name into something 
a bit more diggestible
'''
for i, val in enumerate(FormAtt.columns.values):
    if project_name in val:
        site_code = val.split('_')[5]
        FormAtt = FormAtt.rename(columns = {val: site_code})

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


for col in ids:
    adiv_obs_otus = alpha_diversity('observed_otus', OTU_equivalent, ids[col])
    alpha = adiv_obs_otus.reset_index()
    alpha= alpha.rename(columns={0: 'Count'})
    alpha['Rank']= alpha['Count'].rank()
    alpha.plot(x='Rank', y = ['Count'], kind='bar')
    plt.show()
    
    
#bc_dm = beta_diversity("braycurtis", OTU_equivalent, TransForm['index'])
#wu_pc = pcoa(bc_dm)
#fig = wu_pc.plot(new ,'Position')




my_dpi=96
plt.figure(figsize=(480/my_dpi, 480/my_dpi), dpi=my_dpi)

# Keep the 'species' column appart + make it numeric for coloring
ids['Depth']=pd.Categorical(ids['Depth'])
my_color=ids['Depth'].cat.codes
#ids =ids.drop('Depth', 1)

# Run The PCA

pca = PCA(n_components=3)
principalComponents = pca.fit_transform(Formulae)
# Store results of PCA in a data frame
principalDf = pd.DataFrame(data = principalComponents, columns = ['PCA0', 'PCA1', 'PCA2'])
finalDf = pd.concat([principalDf, ids[['Position', 'Depth', 'SiteName']]], axis = 1)


# Plot initialization
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(principalDf['PCA0'], principalDf['PCA1'], principalDf['PCA2'], c=my_color, cmap="Set2_r", s=60)

# make simple, bare axis lines through space:
xAxisLine = ((min(principalDf['PCA0']), max(principalDf['PCA0'])), (0, 0), (0,0))
ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r')
yAxisLine = ((0, 0), (min(principalDf['PCA1']), max(principalDf['PCA1'])), (0,0))
ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r')
zAxisLine = ((0, 0), (0,0), (min(principalDf['PCA2']), max(principalDf['PCA2'])))
ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r')


# label the axes
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")
ax.set_title("PCA on soil DOM")
plt.show()



#fig = plt.figure(figsize = (8,8))
#ax = fig.add_subplot(1,1,1) 
#ax.set_xlabel('Principal Component 1', fontsize = 15)
#ax.set_ylabel('Principal Component 2', fontsize = 15)
#ax.set_title('2 component PCA', fontsize = 20)
##targets = ['05', '15', '30', '60']e
#targets = ['C1', 'C2', 'H2', 'H1'] 
##targets = ['B', 'F', 'ST' , 'T', 'S']
#colors = ['r', 'g', 'b', 'tan']
#
#
#for target, color in zip(targets,colors):
##    indicesToKeep = finalDf['Depth'] == target
#    indicesToKeep = finalDf['SiteName'] == target
##    indicesToKeep = finalDf['Position'] == target
#    ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
#               , finalDf.loc[indicesToKeep, 'principal component 2']
#               , c = color
#               , s = 50)
#ax.legend(targets)
#ax.grid()
print(pca.explained_variance_ratio_)

