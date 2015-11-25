import glob
import pandas as pd
import os

def concat_by_year():
    # Choose the year:
    valid_years = range(1962,2014) # gives [1962-2013]
    year = None
    while year not in valid_years:
        year = int(raw_input("Choose the year to be concatenated [1962-2013]: ")) 

    # Choose the aggregate level: 2-digit/4-digit/6-digit
    valid_choices = ["AG2", "AG4", "AG6"]
    AG = None
    while AG not in valid_choices:
        AG = raw_input("Choose the levels of aggregation for commodities [AG2, AG4, AG6]: ")

    # grab all the files at the selected AG level of the selected year  
    path = os.path.join('data','dl',AG)
    myfn = os.path.join(path,'*%s.csv' % year)
    allFiles = glob.glob(myfn) 
    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        df = pd.read_csv(file_,index_col=None, header=0)
        list_.append(df)
    frame = pd.concat(list_)

    frame = frame[frame.Reporter != 'EU-28']

    # Save the yearly file in the appropriate folder
    dest = os.path.join('data','yearly',AG)
    if not os.path.exists(dest):
        os.makedirs(dest)
    file_name = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(year)))
    frame.to_csv(file_name, sep=',', index=False)
