import pandas as pd
import urllib2
import wget
import os
import sys
import numpy as np
import shutil
import easygui

def service_downloader():
    ####################################################################################
    ## First make the user select all the necessary parameters
    ####################################################################################
    
    print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print(" Option 4: Cleaning and importing Service data ")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    print("\nFor this option, you will need the already posses the data on your computer.\nIf not:\n\
    \nGo to http://unstats.un.org/unsd/servicetrade/ \n\
    Under Data Query, select Express Selection. \n\
    For Partner Code, input 0 (for World) \n\
    For Trade Flow, select Export\n\
    Then you will import file into the application.")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    choice = None
    valid_choices = ['y','q']
    print 'When you are willing to continue, enter y or enter q to come back later'
    while choice not in valid_choices:
        choice = raw_input("\nWhat is your choice:\t")

    if choice == 'y':
        # Check the existence of the folder
        service_path = os.path.join('data','service')
        if not os.path.exists(service_path):
            os.makedirs(service_path)

        # Check the existence of the dataset
        service = os.path.join(service_path,'ServiceTrade_trade_data.csv')
        if not os.path.exists(service):
            # select the file and make a copy in the appropriate folder for the app
            print("\nPlease select the service data that you just downloaded. \n\
            We will make a copy available in the application folder for the future.")
            path = easygui.fileopenbox()
            shutil.copyfile(path, service)

        # Open the file selected after it have been copied
        print '\nReading the raw data', '...'
        df = pd.read_csv(service, sep=',')

        # Extract the services that we are interested in
        print 'Extracting the 12 most aggregated levels', '...'
        df = df.loc[df['Service Code'].isin([205,
                                             236,
                                             245,
                                             249,
                                             253,
                                             260,
                                             262,
                                             266,
                                             268,
                                             287,
                                             291,
                                             983])]

        df = df[[
            'Period',
            'Trade Flow',
            'Reporter',
            'Partner',
            'Service Code',
            ' Description', 
            'Trade Value']]
        df['Type'] = 'S'
        df.columns = [
            'Period',
            'Trade Flow',
            'Reporter',
            'Partner',
            'Code',
            'Description',
            'Value',
            'Type']

        # Drop the non-country/aggregate values
        print "\nDelete 'EU25', 'EU27' and 'Asia n.i.e.'", "..."
        df = df[df.Reporter != 'EU25']
        df = df[df.Reporter != 'EU27']
        df = df[df.Reporter != 'Asia n.i.e.']

        # Change the name of 'Micronesia' to the more conventional one
        print "Change 'FS Micronesia' to 'Micronesia'", "..."
        df.loc[df['Reporter'] == 'FS Micronesia', 'Reporter'] = 'Micronesia'

        print '\nInsert ISO3 code', '...'
        df.insert(3, 'Reporter ISO', np.nan)
        x, y = df.shape
        country_path = os.path.join('data','add_res', 'country_list_redux.csv')
        country_list = pd.read_csv(country_path,index_col=0, sep='\t')
        for i in range(x):
            name = df.Reporter.iloc[i]
            row_index = df.index[i]
            if name in country_list.index:
                df.loc[row_index,'Reporter ISO'] = country_list.loc[name, 'iso3']

        # Save the transformed file
        output = os.path.join(service_path, 'ServiceDataCleaned.csv')
        print '\nSaving file in', output, '...'
        df.to_csv(output, sep = ',', index=False)
        
        print '\nOperation complete.'
        raw_input("\nPress Enter to continue...")
