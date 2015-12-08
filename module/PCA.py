from __future__ import division # To allow the Python 3.x simpler division operator
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


def PCA():
    ####################################################################################
    ## First make the user select all the necessary parameters
    ####################################################################################
    
    # Choose the aggregate level: 2-digit/4-digit/6-digit
    print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print(" Option 5: Preparation of the data for the Principal Component Analysis ")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    print("\nFor this option, you will have to:\n\
    Specify the level of aggregation wanted for the commodity data\n\
    Specify the starting and ending year of the analysis\n\
    As well as the type of transformation you want to apply to the RCA.")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    
    valid_choices = ["AG2", "AG4", "AG6"]
    AG = None
    while AG not in valid_choices:
        AG = raw_input("\n1. Choose the levels of aggregation for commodities [AG2, AG4, AG6]: ")

    # Command for selecting year
    # Preventing to choose year that does not exist in our database
    valid_years = range(2000,2014) # gives [2000-2013]
    year_s = None
    year_e = None
    while year_s not in valid_years:
        year_s = int(raw_input("\nNote: The PCA is perform on the averaged value over a period. \n\n2. Choose the starting year on which to perform the PCA [2000-2013]: ")) 
    while year_e not in valid_years:
        year_e = int(raw_input("\n3. Choose the ending year on which to perform the PCA [2000-2013]: "))

    # Command for choosing the RCA transformation method
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print("\nHere you have to choose the method to transform the RCA.")
    print("N: keep the RCA as is.")
    print("B: Transorm the RCA into a Binomial equal 1 for RCA > 1 otherwise it's 0.")
    print("log1p: Transform the RCA taking the log of the RCA+1.")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    valid_choices = ["N", "B", "log1p"]
    choice = None
    while choice not in valid_choices:
        choice = raw_input("\n4. Choose your method to transform the RCA [N, B, log1p]: ")

    ####################################################################################
    ## Read the data
    ####################################################################################
    
    # Data for services
    # Subset for the *selected* years

    print "\nOpening the service data", "..."
    path1 = os.path.join('data','service','ServiceDataCleaned.csv')
    df1 = pd.read_csv(path1, sep=',')
    df1 = df1.loc[df1['Period'].isin(range(year_s, year_e + 1))]

    # Data for commodities
    # Select the file of the *selected* year and OPEN it
    # Grab the interesting columns
    # Add an identifier to the commodity data before appending
    # Rename the columns
    print "Opening the commodity data", "..." 
    dest = os.path.join('data','yearly',AG)
    path2 = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(year_s)))
    df2 = pd.read_csv(path2, sep=',')
    for i in range(year_s + 1, year_e + 1 ):
        i_path = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(i)))
        i_data = pd.read_csv(i_path, sep=',')
        df2 = df2.append(i_data, ignore_index = True)
    df2 = df2[[
        'Period',
        'Trade Flow',
        'Reporter Code',
        'Reporter',
        'Reporter ISO',
        'Partner',
        'Commodity Code',
        'Commodity',
        'Trade Value (US$)']]
    df2['Type'] = 'C'
    df2.columns = [
        'Period',
        'Trade Flow',
        'Reporter Code',
        'Reporter',
        'Reporter ISO',
        'Partner',
        'Code',
        'Description',
        'Value',
        'Type']

    # Create the database containing products & services for the selected year
    # Create a new variable called 'SingularCode' = a letter + the original code
    # Save the file to a CSV

    print "Merging the data", "..." 
    df3 = df1.append(df2, ignore_index = True)
    df3['SingularCode'] = df3['Type'] + df3['Code'].map(str)
    path3 = os.path.join('pca','database_%s_%s.csv' % (str(year_s), str(year_e)))
    df3.to_csv(path3, sep = ",", index=False)

    # Average the data over the years

    print "Averaging the data over the available years","..." 
    df3 = df3.groupby(['Reporter ISO','SingularCode'], as_index=False).mean()
    
    # Also by summing and dividing by the range we can
    # consider that an absence of data is zero
    # df3 = df3.groupby(['Reporter ISO','SingularCode'], as_index=False).sum()
    # df3.Value = df3.Value/(year_e - year_s + 1)

    #################################################################################
    ################################    STEP 2    ###################################
    ##############     Transforming the data and calculating the RCA    #############
    #################################################################################

    # Select only the 3 columns of interest
    # Spread the trade into columns
    # Replace NA with 0
    df = df3[['Reporter ISO', 'SingularCode', 'Value']]
    data = df.pivot(index='SingularCode', columns='Reporter ISO', values='Value')
    data = data.fillna(0)

    # Creating RCA as Share in country's exports / share in world exports
    print "Calculating the RCA", "..." 
    a = np.sum(data)
    b = np.sum(data,1)/sum(np.sum(data))
    x, y = data.shape

    if choice == "N":
        for i in range(x):
            for j in range(y):
                data.iloc[i, j] = (data.iloc[i, j] / a.iloc[j]) / (b.iloc[i])

    if choice == "B":
        for i in range(x):
            for j in range(y):
                data.iloc[i, j] = (data.iloc[i, j] / a.iloc[j]) / (b.iloc[i])
                if data.iloc[i, j] > 1:
                    data.iloc[i, j] = 1
                else:
                    data.iloc[i, j] = 0

    if choice == "log1p":
        for i in range(x):
            for j in range(y):
                data.iloc[i, j] = math.log1p((data.iloc[i, j] / a.iloc[j]) / (b.iloc[i]))

    path4 = os.path.join('pca','RCA_%s_%s_%s_%s.csv' % (str(AG),str(choice),str(year_s), str(year_e)))
    print 'Saving the file at %s' % path4 
    data.to_csv(path4, sep = ",")
    
    print '\nOperation complete.'
    raw_input("\nPress Enter to continue...")
