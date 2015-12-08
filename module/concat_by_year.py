import glob
import pandas as pd
import os

def concat_by_year():

    print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print(" Option 2: Concatenate the raw data into yearly database ")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    print("\nFor this option, you will have to:\n\
    Specify the level of aggregation wanted for the commodity data\n\
    Specify the first and last year to be concatenated")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    
    # Choose the aggregate level: 2-digit/4-digit/6-digit
    valid_choices = ["AG2", "AG4", "AG6"]
    AG = None
    while AG not in valid_choices:
        AG = raw_input("\nChoose the levels of aggregation for commodities [AG2, AG4, AG6]: ")

    # Command for selecting year
    # Preventing to choose year that does not exist in our database
    valid_years = range(2000,2014) # gives [2000-2013]
    year_s = None
    year_e = None
    while year_s not in valid_years:
        year_s = int(raw_input("Choose the first year to be concatenated [2000-2013]: ")) 
    while year_e not in valid_years:
        year_e = int(raw_input("Choose the last year to be concatenated [2000-2013]: "))

    for i in range(year_s, year_e + 1 ):
        # grab all the files at the selected AG level of the selected year  
        path = os.path.join('data','dl',AG)
        myfn = os.path.join(path,'*%s.csv' % i)
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
        file_name = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(i)))
        print '\nSaving the file to %s' % str(file_name)
        frame.to_csv(file_name, sep=',', index=False)
        
    print '\nOperation complete.'
    raw_input("\nPress Enter to continue...")
