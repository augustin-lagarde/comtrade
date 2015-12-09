from __future__ import division # To allow the Python 3.x simpler division operator
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

def GPS():
    ####################################################################################
    ## First make the user select all the necessary parameters
    ####################################################################################
    
    print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print(" Option 6: Creation of the proximity matrix ")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

    print("\nFor this option, you will have to:\n\
    Specify the level of aggregation wanted for the commodity data\n\
    Specify the starting and ending year for the computation")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    
    # Choose the aggregate level: 2-digit/4-digit/6-digit
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
        year_s = int(raw_input("\n2. Choose a starting year [2000-2013]: ")) 
    while year_e not in valid_years:
        year_e = int(raw_input("\n3. Choose an ending year [2000-2013]: "))



    # Data for services
    # Subset for the *selected* years
    
    print "\nOpening the service data", "..."
    path1 = os.path.join('data','service','ServiceDataCleaned.csv')
    services = pd.read_csv(path1, sep=',')
    services = services.loc[services['Period'].isin(range(year_s, year_e + 1))]
    
    # Data for commodities
    # Select the file of the *selected* year and OPEN it
    # Grab the interesting columns
    # Add an identifier to the commodity data before appending
    # Rename the columns
    print "Opening the commodity data", "..." 
    dest = os.path.join('data','yearly',AG)
    path2 = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(year_s)))
    commodities = pd.read_csv(path2, sep=',')
    for i in range(year_s + 1, year_e + 1 ):
        i_path = os.path.join(dest,'ExtoWorld_%s_%s.csv' % (str(AG),str(i)))
        i_data = pd.read_csv(i_path, sep=',')
        commodities.append(i_data, ignore_index = True)
    commodities = commodities[[
        'Period',
        'Trade Flow',
        'Reporter Code',
        'Reporter',
        'Reporter ISO',
        'Partner',
        'Commodity Code',
        'Commodity',
        'Trade Value (US$)']]
    commodities['Type'] = 'C'
    commodities.columns = [
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
    data = commodities.append(services, ignore_index = True)
    data['SingularCode'] = data['Type'] + data['Code'].map(str)
    path3 = os.path.join('pca','database_%s_%s.csv' % (str(year_s), str(year_e)))
    data.to_csv(path3, sep = ",", index=False)

    # Average the data over the years

    print "\nAveraging the data over the available years","..." 
    data = data.groupby(['Reporter ISO','SingularCode'], as_index=False).mean()
    
    # Also by summing and dividing by the range we can
    # consider that an absence of data is zero
    # data = data.groupby(['Reporter ISO','SingularCode'], as_index=False).sum()
    # data.Value = data.Value/(year_e - year_s + 1)

    #################################################################################
    ################################    STEP 2    ###################################
    ##############     Transforming the data and calculating the RCA    #############
    #################################################################################

    # Select only the 3 columns of interest
    # Spread the trade into columns
    data = data[[
        'Reporter ISO',
        'SingularCode',
        'Value']]

    data = data.pivot(index='SingularCode', columns='Reporter ISO', values='Value')

    dest = os.path.join('data','GPS')
    if not os.path.exists(dest):
        os.makedirs(dest)

    # Creating RCA as Share in country's exports / share in world exports
    # Memo: iternext iterates over the column than go to the next line
    # it.multi_index[0] send back the line index
    # it.multi_index[1] send back the column index
    print '\nCreating the RCA matrix', '...'

    a = np.sum(data)
    b = np.sum(data,1)/sum(np.sum(data))

    x, y = data.shape
    for i in range(x):
        for j in range(y):
            data.iloc[i, j] = (data.iloc[i, j] / a.iloc[j]) / (b.iloc[i])

    filename = 'RCA.csv'
    file_dest = os.path.join(dest, filename)
    print "Writing the file 'RCA.csv'" ,"..."
    data.to_csv(file_dest, sep = ",")

    # Replacing RCA <= 1 by 0 for easier sum in the probability matrix calculation
    print '\nTransforming the RCA matrix', '...'

    for i in range(x):
        for j in range(y):
            if data.iloc[i, j] <= 1:
                data.iloc[i, j] = 0

    # Calculation of the probability matrix
    print 'Creating the probability matrix', '...'

    nb_prod = data.shape[0]
    cntrySum = np.sum(data,1)
    sum_condition = []

    for i in range(nb_prod):
        sum_condition.append(data.iloc[i] > 1)

    ProbMatrix = np.zeros((nb_prod, nb_prod))
    x, y = ProbMatrix.shape

    for i in range(x):
        for j in range(y):
            ProbMatrix[i, j] = ((data.iloc[i]).dot(sum_condition[j].T))/(cntrySum.iloc[j])

    filename = 'Probabilities.csv'
    file_dest = os.path.join(dest, filename)
    print "\nWriting the file 'Probabilities.csv'","..."
    Probabilities = pd.DataFrame(data=ProbMatrix, index=data.index, columns=data.index)
    Probabilities.to_csv(file_dest, sep = ",")

    # Calculation of the proximity matrix

    for i in range(x):
        for j in range(y):
            ProbMatrix[i, j] = min(ProbMatrix[i, j],ProbMatrix[j, i])

    Probabilities = pd.DataFrame(data=ProbMatrix, index=data.index, columns=data.index)
    filename = 'Proximities.csv'
    file_dest = os.path.join(dest, filename)
    print "Writing the file 'Proximities.csv'", "..."
    Probabilities.to_csv(file_dest, sep = ",")

    # Adding description of the ComCode to the proximity matrix
    #Commodity Code description
    AG4 = file_dest = os.path.join('data', 'add_res', 'AG4codes.txt')
    ComCode = pd.read_csv(AG4,index_col=0, sep='\t')
    ComCode.index = 'C' + ComCode.index.map(str)
    #Service Code description
    extract = services[['Code','Description']].drop_duplicates().sort('Code')
    SerCode = pd.DataFrame(data=extract.Description)
    SerCode.index = extract.Code
    SerCode.index = 'S' + SerCode.index.map(str)

    Coding = ComCode.append(SerCode)

    ProxiDesc = pd.merge(Probabilities, Coding, left_index=True, right_index=True)

    # move the column 'Description' in front
    cols = ProxiDesc.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    ProxiDesc = ProxiDesc[cols]


    print "Writing the file 'ProxiDesc.csv'", "..."
    filename = 'ProxiDesc.csv'
    file_dest = os.path.join(dest, filename)
    ProxiDesc.to_csv(file_dest, sep = ",")

    distance = []
    for i in range(x):
        for j in range(i+1,y):
            if ProbMatrix[i, j] > 0.5:
                distance.append((i,j))

    highest = []
    for i in distance:
        u = data.index[i[0]]
        w = Coding.loc[data.index[i[0]],'Description']
        x = data.index[i[1]]
        y = Coding.loc[data.index[i[1]],'Description']
        z = ProbMatrix[i]
        highest.append((u,w,x,y,z))

    highest.sort(reverse=True, key=(lambda x: x[4]))
    highProx = pd.DataFrame(data=highest, columns=['product1',
                                                   'product1_name',
                                                   'product2',
                                                   'product2_name',
                                                   'proximity'])

    print "Writing the file 'highest.csv'", "..."
    filename = 'highest.csv'
    file_dest = os.path.join(dest, filename)
    highProx.to_csv(file_dest, sep=',', index=False)

    print '\nOperation complete.'
    raw_input("\nPress Enter to continue...")
