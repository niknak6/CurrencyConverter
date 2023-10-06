# Import the necessary modules
from redbot.core import commands
from redbot.core.utils.chat_formatting import box, bold
from datetime import datetime, timedelta # Added timedelta here

# Define the data as a list of tuples
data = [
    ("08/15/23", "Tyrannical", "Volcanic", "Sanguine"), # Added this line
    ("08/22/23", "Fortified", "Storming", "Bursting"),
    ("08/29/23", "Tyrannical", "Afflicted", "Bolstering"),
    ("09/05/23", "Fortified", "Incorporeal", "Sanguine"),
    ("09/12/23", "Tyrannical", "Entangling", "Bursting"),
    ("09/19/23", "Fortified", "Volcanic", "Spiteful"),
    ("09/26/23", "Tyrannical", "Storming", "Raging"),
    ("10/03/23", "Fortified", "Entangling", "Bolstering"),
    ("10/10/23", "Tyrannical", "Incorporeal", "Spiteful"),
    ("10/17/23", "Fortified", "Afflicted", "Raging"),
    ("10/24/23", "Tyrannical", "Volcanic", "Sanguine"),
    ("10/31/23", "Fortified", "Storming", "Bursting"),
    ("11/07/23", "Tyrannical", "Afflicted", "Bolstering"),
    ("11/14/23", "Fortified", "Incorporeal", "Sanguine"),
    ("11/21/23","Tyrannical","Entangling","Bursting"),
    ("11/28/23","Fortified","Volcanic","Spiteful"),
    ("12/05/23","Tyrannical","Storming","Raging"),
    ("12/12/23","Fortified","Entangling","Bolstering"),
    ("12/19/23","Tyrannical","Incorporeal","Spiteful"),
    ("12/26/23","Fortified","Afflicted","Raging"),
    ("01/02/24","Tyrannical","Volcanic","Sanguine")
]

# Define a function to format the data as a table
def format_table(data):
    # Initialize an empty list to store the table rows
    table = []
    
    # Add the header row with column names
    table.append("Date\t\tLevel 4\t\tLevel 7\t\tLevel 10")
    
    # Loop through the data and add each row
    for row in data:
        # Get the date and the affixes from the tuple
        date, level4, level7, level10 = row
        
        # Check if the date is within the current week
        today = datetime.today()
        start = today - timedelta(days=today.weekday()) # Changed datetime.timedelta to timedelta here
        end = start + timedelta(days=6) # Changed datetime.timedelta to timedelta here
        date_obj = datetime.strptime(date, "%m/%d/%y")
        
        # If yes, bold the row
        if start <= date_obj <= end:
            table.append(bold(f"{date}\t{level4}\t{level7}\t{level10}"))
        
        # If no, add the row as it is
        else:
            table.append(f"{date}\t{level4}\t{level7}\t{level10}")
    
    # Join the table rows with newlines and return the result
    return "\n".join(table)

# Define a class for the cog
class TreacheryAffixes(commands.Cog):
    
    # Define the constructor
    def __init__(self, bot):
        self.bot = bot
    
    # Define a command for affixes
    @commands.command()
    async def affixes(self, ctx):
        # Format the data as a table
        table = format_table(data)
        
        # Send the table in a box to the channel
        await ctx.send(box(table))
