# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *

class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("Inventory Manager", "1.1")

        # set-up main memu
        self.sc.add_main_menu_item("VIEW INVENTORY", self.view)
        self.sc.add_main_menu_item("ADD ITEM", self.add)
        self.sc.add_main_menu_item("DELETE ITEM", self.delete)

        # test paths
        self.sc.test_path("inventory.csv")
        self.sc.test_path("items.csv")

        # display main menu
        self.sc.start()
    
    ### MAIN MENU ###
    def view(self):
        # get inventory
        inventory = self.sc.load_database("inventory.csv", ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))
        
        # order by item description
        sorted_inventory = dict(sorted(inventory.items(), key=lambda item: item[1]))

        # save as an html file
        file = open('output.html', 'w')
        file.write('<html>\n')
        file.write('\t<link rel="stylesheet" href="style.css" type="text/css">\n')
        file.write('\t<body>\n')
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
        os.popen('output.html')
        
        # restart
        self.sc.restart()

    def add(self):
        # variables
        abort = False

        # get items database
        items = self.sc.load_database("items.csv", ("BARCODE","NAME","DESCRIPTION"))

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
                self.sc.save_database("items.csv", items)
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
            inventory = self.sc.load_database("inventory.csv", ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))

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
            self.sc.save_database("inventory.csv", inventory)
            self.sc.good(str(index)+" "+name+" "+description+" "+barcode+" "+exp+" Successfully added to inventory!")
            expired = self.sc.compare_dates(exp, self.sc.today())
            if expired < 0:
                self.sc.print("[X] NOTICE! this item expired "+str(expired*-1)+" days ago!", 'red')

        # restart
        self.sc.restart()
    
    def delete(self):
        # load inventory
        inventory = self.sc.load_database("inventory.csv", ("INDEX", "NAME", "DESCRIPTION", "BARCODE", "EXP. DATE"))

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
        
        self.sc.save_database("inventory.csv", inventory)

        # restart
        self.sc.restart()
main()