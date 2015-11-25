from __future__ import division # To allow the Python 3.x simpler division operator
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


####################################################################################
###################################    STEP 1    ###################################
############    Opening the data and preparing it for the selected year    #########
####################################################################################

def PCA():
    # Command for selecting year
    # Preventing to choose year that does not exist in our database
    valid_years = range(2000,2014) # gives [2000-2013]
    year_s = None
    year_e = None
    while year_s not in valid_years:
        year_s = int(raw_input("The PCA is perform on the averaged value over a period. Choose the starting year on which to perform the PCA [2000-2013]: ")) 
    while year_e not in valid_years:
        year_e = int(raw_input("Choose the ending year on which to perform the PCA [2000-2013]: "))

    # Data for services
    # Grab the interesting columns
    # Add an identifier to the service data before appending
    # Rename the columns
    # Subset for the *selected* years

    path1 = os.path.join('raw','service','ServiceDataCleaned.csv')
    df1 = pd.read_csv(path1, sep=',')
    df1 = df1.loc[df1['Period'].isin(range(year_s, year_e + 1))]

    # Data for commodities
    # Select the file of the *selected* year and OPEN it
    # Grab the interesting columns
    # Add an identifier to the commodity data before appending
    # Rename the columns
    path2 = os.path.join('raw','yearly','ExtoWorld_%s.csv' % str(year_s))
    df2 = pd.read_csv(path2, sep=',')
    for i in range(year_s + 1, year_e + 1 ):
        i_path = os.path.join('raw','yearly','ExtoWorld_%s.csv' % str(i))
        i_data = pd.read_csv(i_path, sep=',')
        df2.append(i_data, ignore_index = True)
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
    df3 = df1.append(df2, ignore_index = True)
    df3['SingularCode'] = df3['Type'] + df3['Code'].map(str)
    path3 = os.path.join('pca','database_%s_%s.csv' % (str(year_s), str(year_e)))
    df3.to_csv(path3, sep = ",", index=False)

    # Average the data over the years
    df3 = df3.groupby(['Reporter ISO','SingularCode'], as_index=False).mean()

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

    # Command for choosing the RCA transformation method
    print("Here you have to choose the method to transform the RCA.")
    print("N: keep the RCA as is.")
    print("B: Transorm the RCA into a Binomial equal 1 for RCA > 1 otherwise it's 0.")
    print("log1p: Transform the RCA taking the log of the RCA+1.")

    valid_choices = ["N", "B", "log1p"]
    choice = None
    while choice not in valid_choices:
        choice = raw_input("Choose your method to transform the RCA [N, B, log1p]: ")

    # Creating RCA as Share in country's exports / share in world exports
    it = np.nditer(data, flags=['multi_index'], op_flags=['writeonly'])
    a = np.sum(data)
    b = np.sum(data,1)/sum(np.sum(data))

    if choice == "N":
        while not it.finished:
            it[0] = (it[0]/a[it.multi_index[1]]) / (b[it.multi_index[0]])
            it.iternext()
        
    elif choice == "B":
        while not it.finished:
            it[0] = (it[0]/a[it.multi_index[1]]) / (b[it.multi_index[0]])
            if it[0] > 1:
                it[0] = 1
            else:
                it[0] = 0
            it.iternext()
        
    elif choice == "log1p":
        while not it.finished:
            it[0] = (it[0]/a[it.multi_index[1]]) / (b[it.multi_index[0]])
            it[0] = math.log1p(it[0])
            it.iternext()

    #################################################################################
    #################################################################################
    #################################################################################

    ##filename = 'plot/plot_distribution_%s.png' % str(year)
    ##print("Saving figure to '%s'..." % filename)
    ##plt.savefig(filename)
    ##plt.close()

    # You typically want your plot to be ~1.33x wider than tall.  
    # Common sizes: (10, 7.5) and (12, 9)
    # Remove the plot frame lines. They are unnecessary chartjunk.  
    plt.figure(figsize=(12, 9))  
    ax = plt.subplot()  
    ax.spines["top"].set_visible(False)  
    ax.spines["right"].set_visible(False)

    # Ensure that the axis ticks only show up on the bottom and left of the plot.  
    # Ticks on the right and top of the plot are generally unnecessary chartjunk.  
    ax.get_xaxis().tick_bottom()  
    ax.get_yaxis().tick_left()

     
    # Along the same vein, make sure your axis labels are large
    # enough to be easily read as well. Make them slightly larger
    # than your axis tick labels so they stand out.
    plt.xlabel("RCA", fontsize=16)
    plt.ylabel("Count", fontsize=16)

    # Plot the histogram. 
    plt.hist(list(data.values))
    ##plt.xlim((0, 40))

    # Finally, save the figure as a PNG.
    # You can also save it as a PDF, JPEG, etc.
    # Just change the file extension in this call.  
    # bbox_inches="tight" removes all the extra whitespace on the edges of your plot.

    path4 = os.path.join('pca','%s_plot_distribution_RCA_%s_%s.png' % (str(choice), str(year_s), str(year_e)))
    print 'Saving figure to', path4, '...'
    plt.savefig(path4)
    plt.close()

    #################################################################################
    ###############################    STEP 3    ####################################
    #############      Calculating the eigenvalues and eigenvectors      ############
    #################################################################################

    # Create covariance matrix
    # Create vector of eigen values and matrix of eigen vectors
    # Make a list of (eigenvalue, eigenvector) tuples
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    cov_mat = np.cov(data)
    eig_val, eig_vec = np.linalg.eig(cov_mat)
    eig_pairs = [(np.abs(eig_val[i]), eig_vec[:,i])
                 for i in range(len(eig_val))]
    eig_pairs.sort(reverse=True, key=(lambda x: x[0]))

    #################################################################################
    ###############################    STEP 4    ####################################
    ############      Extract some results in a readable format      ################
    #################################################################################

    loadings = pd.DataFrame()
    loadings['SingularCode'] = data.index

    file_path = os.path.join('raw','add_res','codelist.csv')
    code_list = pd.read_csv(file_path, sep=',') 
    loadings = pd.merge(loadings, code_list, how='left', on='SingularCode')

    for i in range(15):
        x = 'PC%s' % str(i+1)
        loadings[x]=eig_pairs[i][1]
    path5 = os.path.join('pca','%s_loadings_%s_%s.csv' % (str(choice), str(year_s), str(year_e)))
    loadings.to_csv(path5, sep = ",", index=False)
    print 'Saving calculation to', path5, '...'

    #################################################################################
    ###############################    STEP 5    ####################################
    ######################      Plot various results      ###########################
    #################################################################################

    # Construct the transformation matrix W from the eigenvalues that correspond to
    # the 2 largest eigenvalues
    # Transform the data using matrix W
    matrix_w_cov = np.hstack((eig_pairs[0][1].reshape(len(eig_pairs),1),
                              eig_pairs[1][1].reshape(len(eig_pairs),1)))
    data_transf = matrix_w_cov.T.dot(data).T

    # Plot the variance explained by the PCs
    tot = sum(np.abs(eig_val))
    var_exp = [(i / tot)*100 for i in sorted(np.abs(eig_val), reverse=True)]
    cum_var_exp = np.cumsum(var_exp)
    plt.plot(np.arange(30)+1, cum_var_exp[0:30],'xb-')
    #plt.ylim((0, 100))
    plt.xlabel('No. of principal components')
    plt.ylabel('Cumulative variance explained')
    plt.grid(axis = 'y', ls = '-', color = 'white')
    path6 = os.path.join('pca','%s_plot_variance_explained_%s_%s.png' % (str(choice), str(year_s), str(year_e)))
    print 'Saving figure to', path6, '...'
    plt.savefig(path6)
    plt.close()

    # Plot the data on the two first PCs
    x = data_transf[:,0]
    y = data_transf[:,1]
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    plt.title('Plotting into the space of the first two PCs')
    for i, txt in enumerate(data.columns):
        ax.annotate(txt.decode('unicode-escape'),(x[i],y[i]))
    path7 = os.path.join('pca','%s_plot_first_pc_space_%s_%s.png' % (str(choice), str(year_s), str(year_e)))
    print 'Saving figure to', path7, '...'
    plt.savefig(path7)
    plt.close()

    # 15 succesive loadings plot for two PCs
    for i in range(5):
        x = eig_pairs[i][1].reshape(len(eig_pairs),1)
        y = eig_pairs[i+1][1].reshape(len(eig_pairs),1)
        fig, ax = plt.subplots()
        ax.scatter(x, y)
        tit = 'Load plot for PC%s and PC%s' % (i+1, i+2)
        plt.title(tit)
        for j, txt in enumerate(data.index):
            ax.annotate(txt,(x[j],y[j]))
        
        path8 = os.path.join('pca', '%s_plot_loadings_%s_%s_%s.png' % (str(choice), str(year_s), str(year_e),i))
        print 'Saving figure to', path8, '...'
        plt.savefig(path8)
        plt.close()

