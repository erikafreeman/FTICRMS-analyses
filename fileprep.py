import pandas as pd 

lkmatch= pd.read_csv('/home/erika/Desktop/likeliest_match.csv')
columns = lkmatch.columns
samples= [col for col in lkmatch if col.startswith('Sample')]
analID= [i.split('_', 1)[0] for i in samples]
lID=[i.split('_', 1)[1] for i in samples]
laID=[i.split('_', 1)[0] for i in lID]
labID=[i.split('masslists', 1)[1] for i in laID]

SampleName= [i.split('_', 1)[1] for i in lID]
x = pd.Series(SampleName)
y= x.str.split('_', expand=True)
erikaName= y[3]
erikaName= erikaName.tolist()
SampleNames= pd.DataFrame({'SampleID':analID,'LabID': labID,'ErikaID': erikaName})
SampleNames['ErikaID']= SampleNames['ErikaID'].astype('str')
SampleNames['ErikaID'] = SampleNames['ErikaID'].apply(lambda x: 0 if len(x) < 5 else x)
SampleNames['Site']= SampleNames['ErikaID'].str.slice(start=0, stop=2)
SampleNames['Slope1']= SampleNames['ErikaID'].str.slice(start=2)
SampleNames['Slope2']= SampleNames['ErikaID'].str.slice(start=2, stop=3)
SampleNames['Depth1']= SampleNames['ErikaID'].str.slice(start=3)
SampleNames['Slope'] = SampleNames['Slope1'].where(SampleNames['Slope1'].str.contains('ST'), SampleNames['Slope2'])
SampleNames['Depth'] = SampleNames['Depth1'].where(SampleNames['Slope'].str.contains('ST'), SampleNames['Depth1'])
SampleNames['Depth']= SampleNames['Depth'].astype('str')
SampleNames['Depth'] = SampleNames['Depth'].apply(lambda x: 'Stream' if x.startswith('T') else x)

SampleNames.drop(['Slope1', 'Slope2', 'Depth1'], axis=1, inplace=True)
fdata= SampleNames.set_index('SampleID')
#fdata.to_csv('/home/erika/Desktop/SampleNames.csv')


edata_start = lkmatch[['mz']]
edata_start.rename(columns={'mz': 'Mass'}, inplace=True)
edata_end = lkmatch[samples]
edata_end.columns = analID
efinal0 = pd.DataFrame(edata_end)
edata= efinal0.fillna(0)
edata= edata.join(edata_start)
edata= edata.set_index('Mass')



emeta_cols = ['Mass	C','H','O','N','C13','S','P','Error','NeutralMass']
emeta = lkmatch[['mz','C','H','O','N','C13','S','P','SE','reference']]
emeta.rename(columns={'mz':'Mass','SE': 'Error','reference': 'NeutralMass'}, inplace=True)
emeta= emeta.set_index('Mass')

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('/home/erika/Desktop/pandas_multiple.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
edata.to_excel(writer, sheet_name='e_data')
fdata.to_excel(writer, sheet_name='f_data')
emeta.to_excel(writer, sheet_name='e_meta')

# Close the Pandas Excel writer and output the Excel file.
writer.save()