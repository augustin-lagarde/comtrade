import module

def menu():
    print("\n\n\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print(" WELCOME TO THE MENU ")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    #user chooses a number from list
    print("\nChoose a number to continue:\t\n\
    Select 1 to download from UN ComTrade\n\
    Select 2 to concatenate files from a specific year (request step 1 first)\n\
    Select 3 to merge several years together (request step 2 first)\n\
    Select 4 to clean and import data from UN ServiceTrade\n\
    Select 5 to prepare the data for the PCA\n\
    Select 6 to transform the data into a proximity matrix\n\
    Select 7 to exit the program")
    print("\n= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = ")
    print("\n\nCopyright Bruegel 2015. Programme written by Augustin Lagarde.\n\n")


def main():
    menu()
    choice= int(input("Enter menu choice:\t"))

    while choice != 7:
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
            #prepare the data for the PCA
            module.PCA()
        elif choice == 6:
            #Transform the data into a proximity matrix
            module.GPS()


        menu()
        choice = int(input("\n\nEnter menu choice:\t"))

    print("\nApplication Complete")


# Launch the app
main()
