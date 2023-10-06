# Import the necessary modules
from redbot.core import commands
from redbot.core.utils.chat_formatting import box, bold
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Define a function to scrape the data from the website
def scrape_data(url):
    # Send a GET request to the website and store the response
    response = requests.get(url)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        # Parse the response content as HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table element that contains the affixes data
        table = soup.find("table", class_="affixes_overview_table")

        # Check if the table element exists
        if table:
            # Create an empty list to store the affixes data
            affixes_data = []

            # Loop through each row of the table body
            for row in table.find("tbody").find_all("tr"):
                # Create an empty dictionary to store the row data
                row_data = {}

                # Get the start date of the week from the first column
                start_date = row.find("td", class_="first_column").get_text().strip()
                row_data["start_date"] = start_date

                # Get the affix names from the other columns
                affix_names = []
                for affix in row.find_all("td")[1:]:
                    affix_name = affix.get_text().strip()
                    affix_names.append(affix_name)
                row_data["affix_names"] = affix_names

                # Append the row data to the affixes data list
                affixes_data.append(row_data)

            # Return the affixes data list
            return affixes_data
        
        else:
            # Return None if the table element does not exist
            return None
    
    else:
        # Return None if the response status code is not 200 (OK)
        return None

# Define a function to format the data as a table
def format_table(data):
    # Initialize an empty list to store the table rows
    table = []
    
    # Add the header row with column names
    table.append("Date\t\tLevel 2\t\tLevel 7\t\tLevel 14\tSeasonal")
    
    # Loop through the data and add each row
    for row in data:
        # Get the date and the affixes from the dictionary
        date = row["start_date"]
        level2, level7, level14, seasonal = row["affix_names"]
        
        # Check if the date is within the current week
        today = datetime.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        date_obj = datetime.strptime(date, "%m/%d/%y")
        
        # If yes, bold the row
        if start <= date_obj <= end:
            table.append(bold(f"{date}\t{level2}\t{level7}\t{level14}\t{seasonal}"))
        
        # If no, add the row as it is
        else:
            table.append(f"{date}\t{level2}\t{level7}\t{level14}\t{seasonal}")
    
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
        # Define a list of urls of the website
        urls = ["https://keystone.guru/affixes", "https://keystone.guru/affixes?offset=1"]

        # Loop through each url in the list
        for url in urls:
            # Scrape the data from the website using the function
            data = scrape_data(url)

            # Check if the data is not None
            if data:
                # Format the data as a table using the function
                table = format_table(data)

                # Send the table in a box to the channel with a title indicating which week it is
                if url.endswith("offset=1"):
                    await ctx.send(f"Next week's M+ Affixes from [keystone.guru]:\n{box(table)}")
                else:
                    await ctx.send(f"Current week's M+ Affixes from [keystone.guru]:\n{box(table)}")
            else:
                # Send an error message if the data is None
                await ctx.send(f"Could not get the affixes data from [keystone.guru].")
