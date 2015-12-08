import pandas as pd
import urllib2
import wget
import os
import cronus.beat as beat
import sys
import gc

def downloader():

        print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
        print(" Option 1: Download data from UN ComTrade ")
        print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")

        print("\nFor this option, you will have to:\n\
        Specify the level of aggregation wanted for the commodity data\n\
        Specify the first and last year to be downloaded")
        print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
        
        # Choose the aggregate level: 2-digit/4-digit/6-digit
        valid_choices = ["AG2", "AG4", "AG6"]
        AG = None
        while AG not in valid_choices:
                AG = raw_input("Choose the levels of aggregation for commodities [AG2, AG4, AG6]: ")

        # Choose the year:
        valid_years = range(1962,2014) # gives [1962-2013]
        year_s = None
        while year_s not in valid_years:
                year_s = int(raw_input("Choose the first year to be downloaded [1962-2013]: "))
        year_e = None
        while year_e not in valid_years:
                year_e = int(raw_input("Choose the last year to be downloaded [1962-2013]: "))

        for year in range(year_s, year_e+1):                
                dl_path = os.path.join('data','dl',AG) # where the data from ComTrade will be downloaded
                if not os.path.exists(dl_path):
                        os.makedirs(dl_path)
                add_res = os.path.join('data','add_res') # where the additional files needed are stored

                ctrycodes = pd.read_excel(os.path.join(add_res,'country_iso_codes.xls'))
                ctryrx = pd.read_csv(os.path.join(add_res,'country_list_redux.csv'), sep='\t')

                ctryrx = pd.merge(ctryrx, ctrycodes, how='left', left_on='iso3', right_on='ISO3-digit Alpha')

                ctrys = ctryrx.loc[ctryrx['End Valid Year'] > 2009]
                ctrys = ctrys[['country', 'iso3', 'ctyCode']].drop_duplicates()

                error_list = []

                i = 0
                beat.set_rate(0.027) # 100req/hour = 0.027req/s * 3600s/h

                while beat.true():
                        try:
                                ctry = ctrys.iloc[i]
                        except:
                                print '\nDownload of %d files completed' % i
                                break

                        print '\ndownloading', year, ctry['country'], '...'
                        myfn = os.path.join(dl_path,"comtrade_EXtoWorld_%s_%s.csv" % (str(ctry['iso3']), str(year)))
                        if (os.path.exists(myfn) == True):
                                i += 1
                                continue

                        print 'Saving file in', myfn, '...'
                        ctry_code = ctry['ctyCode']
                        file_url = 'http://comtrade.un.org/api/get?max=50000&type=C&freq=A&cc=%s&px=HS&ps=%s&r=%s&p=0&rg=2&fmt=csv' % (str(AG), year, str(ctry_code))
                        
                        try:
                                file_name = wget.download(file_url, out = myfn)
                        except:
                                print 'error for ', ctry['country']
                                error_list[ctry_code]

                        i += 1
                        beat.sleep()


                # Redownload instantly the files with errors

                print 'Check for errors', '...'
                i = 0
                j = 0
                beat.set_rate(0.027) # 100req/hour = 0.027req/s * 3600s/h

                while beat.true():
                        try:
                                ctry = ctrys.iloc[i]
                        except:
                                print '\nRedownload of %d files completed' % i
                                break

                        myfn = os.path.join(dl_path,"comtrade_EXtoWorld_%s_%s.csv" % (str(ctry['iso3']), str(year)))
                        size = os.path.getsize(myfn)
                        if not (size == 36):
                                i += 1
                                j = i - 1
                                continue
                        print '\nReplacing', year, ctry['country'], '...'
                        os.remove(myfn)
                        print 'Saving file in', myfn, '...'
                        ctry_code = ctry['ctyCode']
                        file_url = 'http://comtrade.un.org/api/get?max=50000&type=C&freq=A&cc=%s&px=HS&ps=%s&r=%s&p=0&rg=2&fmt=csv' % (str(AG), year, str(ctry_code))
                        
                        try:
                                file_name = wget.download(file_url, out = myfn)
                        except:
                                print 'error for ', ctry['country']
                        size = os.path.getsize(myfn)
                        if (size == 36):
                                i -= 1   
                        i += 1
                        beat.sleep()


                #Cleaning the downloads
                        
                # Get all files.
                list = os.listdir(dl_path)

                redo_list = []
                filename = []
                cat1 = []
                cat2 = []
                cat3 = []
                cat4 = []

                for file in list:
                        location = os.path.join(dl_path, file)
                        size = os.path.getsize(location)
                        if size < 1000:
                                if pd.read_csv(location).iloc[0,0] == 'No data matches your query or your query is too complex. Request JSON or XML format for more information.':
                                        redo_list.append(file)
                                        filename.append(file[:-4])
                                        cat1.append(file[:-4].split('_')[0])
                                        cat2.append(file[:-4].split('_')[1])
                                        cat3.append(file[:-4].split('_')[2])
                                        cat4.append(file[:-4].split('_')[3])
                                        os.remove(location)
                                
                deleted = pd.DataFrame(filename, columns=['filename'])
                deleted['source'] = cat1
                deleted['type'] = cat2
                deleted['country'] = cat3
                deleted['year'] = cat4

                # Save a report of the deleted files
                print("\nThere were %s empty files. They have been deleted automatically" % len(redo_list))
                fname = 'DeletedFiles_%s_%s.csv' % (str(AG),str(cat4[0]))
                # Check the folder exists
                dest = os.path.join('data','dl','dl_reports')
                if not os.path.exists(dest):
                        os.makedirs(dest)
                # Save the file
                fdest = os.path.join(dest,fname)
                deleted.to_csv(fdest, sep='\t', index=False)
                print '\nSaving files in', fdest, '...'
                print("\nThe report DeletedFiles_%s.csv contains the information on the files that were empty and have been deleted.") % str(cat4[0])

        print '\nOperation complete.'
        raw_input("\nPress Enter to continue...")
