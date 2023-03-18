import subprocess
import pandas

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
    
    def upgrade_all():
        info = subprocess.check_output(['winget', 'upgrade', '--all'])


server =  up_to_dater()
print(server.get_update_info())