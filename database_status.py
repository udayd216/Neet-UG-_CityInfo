import os
import oracledb
from prettytable import PrettyTable
from termcolor import colored

#oracledb.init_oracle_client()
oracledb.init_oracle_client(lib_dir=r"D:\app\udaykumard\product\instantclient_23_6")
conn = oracledb.connect(user='RESULT', password='LOCALDEV', dsn='192.168.15.208:1521/orcldev')
cur = conn.cursor()

class ShowDatabaseStatus:
    def __init__(self, cur):
        self.cur = cur  # Store the cursor for later use

    def get_status(self):
        str_jeeappno = "SELECT PROCESS_STATUS, COUNT(*) FROM I_NEET_UG_CITYINFO_25 GROUP BY PROCESS_STATUS"
        self.cur.execute(str_jeeappno)
        res = self.cur.fetchall()
        
        # Clear the terminal window
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if res:
            # Create PrettyTable object
            table = PrettyTable()
            table.field_names = [colored("Process Status", 'cyan', attrs = ['bold']), colored( "Count", 'cyan', attrs = ['bold'])]
            
            # Add rows with different colors based on some conditions
            for row in res:
                process_status, count = row
                if process_status == 'P': 
                    table.add_row([colored(process_status, 'yellow'), colored(count, 'yellow')])
                elif process_status == 'INVALID':
                    table.add_row([colored(process_status, 'red'), colored(count, 'red')])
                elif process_status == 'NA':
                    table.add_row([colored(process_status, 'white'), colored(count, 'white')])
                elif process_status == 'DONE':
                    table.add_row([colored(process_status, 'green'), colored(count, 'green')])
                else:
                    table.add_row([process_status, count])  # Default no color
            print(table)
        else:
            print("No data to display.")