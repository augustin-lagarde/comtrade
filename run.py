import module

def menu():

    #user chooses a number from list
    print("Choose a number to continue:\t\n\
    Select 1 to download from UN ComTrade\n\
    Select 2 to concatenate files from a specific year (request step 1 first)\n\
    Select 3 to merge several years together (request step 2 first)\n\
    Select 4 to download from UN ServiceTrade\n\
    Select 5 to perform the PCA analysis\n\
    Select 6 to exit the program")

def main():
    print("\nWelcome, this little program has been written by Augustin Lagarde.\n\
    It is here to help you deal with UN ComTrade data\n")
    menu()
    choice= int(input("Enter menu choice:\t"))

    while choice != 6:
        #get choice from user
        if choice == 1:
            #download data from ComTrade
            module.downloader()
            #module.cleaner()
        elif choice == 2:
            #concatenate file of a same year
            module.concat_by_year()
        elif choice == 3:
            #concatenante years together
            module.concat_by_year_together()
        elif choice == 4:
            module.service_downloader()
        elif choice == 5:
            #start the PCA
            module.PCA()

        menu()
        choice = int(input("\nEnter menu choice:\t"))

    print("\nApplication Complete")


# Launch the app
main()
