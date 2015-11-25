import glob
import pandas as pd
import os
import sys

def concat_by_year_together():
    print("\nThis module concatenates all the files in the folder 'yearly' under 'data' for the selected aggregated level. \nBe sure that there are no unwanted files in the folder.")

    choice = None
    valid_choices = ['y','q']
    while choice not in valid_choices:
        choice = raw_input("\nWhen you are willing to continue, enter y or enter q to quit:\t")

    if choice == 'y':
        AG = None
        valid_choices = ["AG2", "AG4", "AG6"]
        while AG not in valid_choices:
            AG = raw_input("Choose the levels of aggregation for commodities [AG2, AG4, AG6]: ")
        path = os.path.join('raw','yearly',AG,'*.csv')
        allFiles = glob.glob(path) 
        frame = pd.DataFrame()

        list_ = []

        for file_ in allFiles:
            df = pd.read_csv(file_,index_col=None, header=0)
            list_.append(df)
        
        frame = pd.concat(list_)

        dest = os.path.join('data','database')
        if not os.path.exists(dest):
            os.makedirs(dest)
        filename = 'ExtoWorld_%s.csv' % str(AG)
        file_dest = os.path.join(dest, filename)
        frame.to_csv(file_dest, sep=',')





