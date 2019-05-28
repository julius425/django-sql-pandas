"""PandasSQLInterface module(PSQLI)"""

import datetime
# Plot encoding imports
from io import BytesIO
import base64
# Main imports
import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
from pylab import rcParams



# Interface class
class DataBaseConnector:

    """
    Initialises MySQL database connection.

    """

    def connect_db(self, addr, psswd, uname, dbname):
        try:
            db = MySQLdb.connect(
                addr,
                psswd,
                uname,
                dbname
            )
            return db
        except Exception as e:
            return f'Connection failed{e.message}, excception occured! '


class DataFrameMaker:

    """
    Class sends a query to Sample db,
    read query-data with pandas method
    build tables and plots based on received query-data
    """

    def __init__(self, db, node, time_from, time_to):
        """
       Accepts parameters to run the query.
       Sql-query is hard-coded so user could only have
       limited access to the data base.
        :param db: initial database connection with DataBaseConnector class through django model methods.
        :param node: node id we want to get info from
        :param time_from:
        :param time_to:
        """
        self.db = db
        self.node = node
        self.time_from = time_from
        self.time_to = time_to
        self.query = f"""
                         SELECT 
                             SampleItemToGet1,  
                             SampleItemToGet2   
                         FROM 
                             SampleDatabase                   
                         WHERE 
                             system_node='{self.node}'
                         AND
                             ReportedTime BETWEEN
                                 '{self.time_from}' AND
                                 '{self.time_to}'                    
                      """
        # The whole syslog itself
        self.df = pd.read_sql(self.query, self.db)

    def get_nunique_messages(self):
        """Get non-unique frame messages"""
        return self.df.groupby('Message').nunique().to_html()

    def get_log(self):
        """Get log in html format """
        return self.df.to_html()

    def get_last_messages(self):
        """Get five last log messages"""
        return self.df.tail(5).to_html()

    def get_plot(self):
        """Processes and returns plot image to django view."""

        self.df.plot()
        # Creating a buffer, saving plot pic in it(we don't want to store images on server)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        # Get pic from a buffer
        image_png = buffer.getvalue()
        buffer.close()
        # Encode image in base64
        graphic = base64.b64encode(image_png)
        # Decode as utf8
        graphic = graphic.decode('utf-8')

        return graphic  # Html template with django tag: <img src="data:image/png;base64,{{ graphic|safe }}">

    def get_sim_card_names(self):
        """This block is to show up f'{sim}' on a plot"""

        sim_names = ['A', 'B', 'C']
        sim_numbers = []

        for sim in sim_names:

            item = self.df.loc[(self.df['Message'].str.startswith(f'Sim \'{sim}\' S/N'), 'Message')].reset_index()

            if len(item) > 0:
                sim_numbers.append(item['Message'][0])
            else:
                sim_numbers.append('no record')

        return sim_numbers
