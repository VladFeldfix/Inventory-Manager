# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("Inventory Manager", "2.0")

        # set-up main memu
        self.sc.add_main_menu_item("VIEW INVENTORY", self.view)
        self.sc.add_main_menu_item("ADD ITEM", self.add)
        self.sc.add_main_menu_item("DELETE ITEM", self.delete)
        self.sc.add_main_menu_item("SWITCH DEFAULT INVENTORY", self.switch)

        # get settings and set paths
        # get settings
        self.db_location = self.sc.get_setting("Database Location")
        self.db_name = self.sc.get_setting("Default Database")
        self.inventory = self.db_location+"/"+self.db_name+"/inventory.csv"
        self.items = self.db_location+"/"+self.db_name+"/items.csv"

        # create folder
        if not os.path.isdir(self.db_location+"/"+self.db_name):
            os.makedirs(self.db_location+"/"+self.db_name)

        # make inventory and items
        if not os.path.isfile(self.inventory):
            file = open(self.inventory, 'w')
            file.write("INDEX,NAME,DESCRIPTION,BARCODE,EXP. DATE\n")
            file.close()
        if not os.path.isfile(self.items):
            file = open(self.items, 'w')
            file.write("BARCODE,NAME,DESCRIPTION\n")
            file.close()     

        # test paths
        self.sc.test_path(self.db_location)
        self.sc.test_path(self.db_location+"/"+self.db_name)
        self.sc.test_path(self.inventory)
        self.sc.test_path(self.items)

        # display main menu
        self.sc.start()
    
    ### MAIN MENU ###
    def view(self):
        # display inventory
        self.display_inventory()

        # get inventory
        inventory = self.sc.load_database(self.inventory, ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))
        
        # order by item description
        sorted_inventory = dict(sorted(inventory.items(), key=lambda item: item[1]))

        # save as an html file
        file = open(self.db_location+"/"+self.db_name+"/output.html", 'w')
        file.write('<html>\n')
        file.write('\t<head>\n')
        file.write('\t\t<style>\n')
        file.write('\t\t\ttable, tr, td, th{\n')
        file.write('\t\t\t\tborder: 1px solid black;\n')
        file.write('\t\t\t\tborder-collapse: collapse;\n')
        file.write('\t\t\t\tpadding: 5px;\n')
        file.write('\t\t\t\tfont-family:Arial, Helvetica, sans-serif\n')
        file.write('\t\t\t}\n')
        file.write('\t\t\tbody{\n')
        file.write('\t\t\t\tfont-family:Arial, Helvetica, sans-serif\n')
        file.write('\t\t\t}\n')
        file.write('\t\t\tth{\n')
        file.write('\t\t\t\tbackground-color: #4a4a4a;\n')
        file.write('\t\t\t\tcolor: white;\n')
        file.write('\t\t\t\ttext-align: left;\n')
        file.write('\t\t\t}\n')
        file.write('\t\t\t.red{\n')
        file.write('\t\t\t\tcolor: red;\n')
        file.write('\t\t\t}\n')
        file.write('\t\t</style>\n')
        file.write('\t</head>\n')
        file.write('\t<body>\n')
        file.write('\t\t<h1>Inventory name: '+self.db_name+'</h1>\n')
        file.write('\t\t<h3>Last update: '+self.sc.today()+" "+self.sc.now()+'</h3>\n')
        file.write('\t\t<table>\n')
        file.write('\t\t\t<tr>\n')
        file.write('\t\t\t\t<th>INDEX</th>\n')
        file.write('\t\t\t\t<th>NAME</th>\n')
        file.write('\t\t\t\t<th>DESCRIPTION</th>\n')
        file.write('\t\t\t\t<th>BARCODE</th>\n')
        file.write('\t\t\t\t<th>EXP. DATE</th>\n')
        file.write('\t\t\t</tr>\n')
        for key, val in sorted_inventory.items():
            if key != "INDEX":
                file.write('\t\t\t<tr>\n')
                file.write('\t\t\t\t<td>'+key+'</td>\n')
                i = 0
                for v in val:
                    red = ""
                    expired = ""
                    if i == 3:
                        exp = self.sc.compare_dates(v, self.sc.today())
                        if exp < 0:
                            red = " class = 'red'"
                            expired = " *Expired "+str(exp*-1)+" ago"
                    file.write('\t\t\t\t<td'+red+'>'+v+expired+'</td>\n')
                    i += 1
                file.write('\t\t\t</tr>\n')
        file.write('\t\t\t</tr>\n')
        file.write('\t\t</table>\n')
        file.write('\t</body>\n')
        file.write('</html>\n')
        file.close()

        # open file
        os.popen(self.db_location+"/"+self.db_name+"/output.html")
        
        # restart
        self.sc.restart()

    def add(self):
        # display inventory
        self.display_inventory()

        # variables
        abort = False

        # get items database
        items = self.sc.load_database(self.items, ("BARCODE","NAME","DESCRIPTION"))

        # get barcode
        barcode = self.sc.input("Insert barcode")

        # get item description
        if barcode in items:
            fullname = items[barcode]
            name = fullname[0]
            description = fullname[1]
            self.sc.print(name+" "+description)
        else:
            self.sc.error("This barcode is not in the database")
            if self.sc.question("Would you like to add a new item to the databae?"):
                name = self.sc.input("Insert item name")
                description = self.sc.input("Insert item description")
                items[barcode] = [name,description]
                self.sc.save_database(self.items, items)
                self.sc.good(barcode+" "+name+" "+description+" Successfully added to database!")
            else:
                abort = True
                self.sc.warning("Procedure aborted!")
        
        if not abort:
            # exp date
            ok = False
            while not ok:
                exp = self.sc.input("Insert expiration date YYYY-MM-DD")
                ok = self.sc.test_date(exp)

            # add to inventory
            # load inventory
            inventory = self.sc.load_database(self.inventory, ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))

            # get last box id
            index = 0
            for key in inventory.keys():
                try:
                    key = int(key)
                except:
                    key = 0
                    pass
                if key >= index:
                    index = key + 1
            self.sc.print("Your index is:"+str(index))
            inventory[index] = (name,description,barcode,exp)
            self.sc.save_database(self.inventory, inventory)
            self.sc.good(str(index)+" "+name+" "+description+" "+barcode+" "+exp+" Successfully added to inventory!")
            expired = self.sc.compare_dates(exp, self.sc.today())
            if expired < 0:
                self.sc.print("[X] NOTICE! this item expired "+str(expired*-1)+" days ago!", 'red')

        # restart
        self.sc.restart()
    
    def delete(self):
        # display inventory
        self.display_inventory()
        
        # load inventory
        inventory = self.sc.load_database(self.inventory, ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))

        # get item index
        index = self.sc.input("Insert item index to delete")

        # delete item
        if not index in inventory:
            self.sc.error("This index is not in the database!")
            self.sc.warning("Procedure aborted!")
        else:
            self.sc.print("Selected item:")
            self.sc.print(index+" "+inventory[index][0]+" "+inventory[index][1]+" "+inventory[index][2]+" "+inventory[index][3])
            if self.sc.question("Are you sure you want to delete this item?"):
                del inventory[index]
                self.sc.good("Successfully removed from inventory!")
            else:
                self.sc.warning("Procedure aborted!")
        
        self.sc.save_database(self.inventory, inventory)

        # restart
        self.sc.restart()
    
    def switch(self):
        # display inventory
        self.display_inventory()
        
        databases = []
        for root, dirs, files in os.walk(self.db_location):
            for dir in dirs:
                databases.append(dir)
        
        databases.append(" * Create a new one...")
        
        choice = self.sc.choose("Choose new default inventory",databases)
        if choice == " * Create a new one...":
            name = self.sc.input("Insert database name")
            os.makedirs(self.db_location+"/"+name)
            file = open(self.db_location+"/"+name+"/inventory.csv", 'w')
            file.write("INDEX,NAME,DESCRIPTION,BARCODE,EXP. DATE\n")
            file.close()
            file = open(self.db_location+"/"+name+"/items.csv", 'w')
            file.write("BARCODE,NAME,DESCRIPTION\n")
            file.close()        
            choice = name

        self.sc.good("New default inventory is selected to be: "+choice)
        file = open("settings.txt", 'w')
        file.write("Database Location > "+self.db_location+"\n")
        file.write("Default Database > "+choice+"\n")
        file.close()

        # get settings and set paths
        self.db_name = choice
        self.inventory = self.db_location+"/"+self.db_name+"/inventory.csv"
        self.items = self.db_location+"/"+self.db_name+"/items.csv"
        
        # restart
        self.sc.restart()
    
    ### OTHER ###
    def display_inventory(self):
        self.sc.print("INVENTORY: "+self.db_name,"blue")
main()