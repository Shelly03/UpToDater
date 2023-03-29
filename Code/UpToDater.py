import json
import subprocess
import pandas
import snmp

class up_to_dater:
    
    def get_update_info(self):
        info = subprocess.check_output(['winget', 'upgrade'])
        info = info.decode()
        info = info.split('\r\n')[2:-2]
        df = pandas.DataFrame(columns=['name', 'id', 'version', 'available', 'source'])
        for line in info:
            line = (line.strip()).split()
            line = [word for word in line if word != '<']
            app_name = ' '.join(line[:-4])
            line = line[-4:]
            line.insert(0, app_name)
            df.loc[len(df)] = (line)
        return df
    
    def upgrade_all(self):
        info = subprocess.check_output(['winget', 'upgrade', '--all'])
        
    def get_jason_upgrades(self, upgrades_df):
        programs = [{'PackageIdentifier' : program_id} for program_id in upgrades_df['id']]
        
        import_file = {
        "$schema" : "https://aka.ms/winget-packages.schema.2.0.json",
	    "CreationDate" : "2023-03-25T21:45:24.637-00:00",
	    "Sources" : 
	        [
                {
                "Packages" : 
                    [
                        programs
                    ], 
                "SourceDetails" : 
		        {
				"Argument" : "https://cdn.winget.microsoft.com/cache",
				"Identifier" : "Microsoft.Winget.Source_8wekyb3d8bbwe",
				"Name" : "winget",
				"Type" : "Microsoft.PreIndexed.Package"
			    }
                }
                
            ],
        "WinGetVersion" : "1.4.10173"
        }
    
        with open("import.json", "w") as outfile:
            json.dump(import_file, outfile)
        


server =  up_to_dater()
print(server.get_update_info())