# Import the necessary modules
import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import bold
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re

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
                    # Get the text of the affix and remove any trailing pipe or whitespace characters
                    affix_name = affix.get_text().strip().rstrip("| ")
                    # Append the cleaned affix name to the list
                    affix_names.append(affix_name)

                # Slice the list to only include the first three elements
                affix_names = affix_names[:3]

                row_data["affix_names"] = affix_names

                # Append the row data to the affixes data list
                affixes_data.append(row_data)

            print(f"Affixes data: {affixes_data}")  # Print out all fetched data

            # Return the affixes data list
            return affixes_data
        
        else:
            print("Table element not found")  # Print a message if the table element does not exist
            return None
    
    else:
        print(f"Failed to fetch data from {url}")  # Print a message if the GET request fails
        return None

# Define a function to format the data as an embed message
def format_embed(data, title):
    # Initialize an empty string to store the embed description
    
    embed_description = ""
    
    # Loop through the data and add each row to the embed description
    for row in data:
        # Get the date and the affixes from the dictionary
        date = row["start_date"]
        level2, level7, level14 = row["affix_names"]
        
        # Define a regex pattern to match the date format '%Y/%b/%d\n\n\n     @ %Hh'
        date_pattern = re.compile(r"\d{4}/\w{3}/\d{2}\n\n\n     @ \d{2}h")
        
        # Check if the date matches the pattern using match()
        if date_pattern.match(date):
            # Parse the date using the format '%Y/%b/%d\n\n\n     @ %Hh'
            date_obj = datetime.strptime(date, "%Y/%b/%d\n\n\n     @ %Hh")
        
            # Convert the date to US standard of MM/DD/YY and drop the time
            date_str = date_obj.strftime("%m/%d/%y")
        
            # Check if the date is within or after this week or last week (if today is Monday)
            today = datetime.today()
            start = today - timedelta(days=(today.weekday() - 1) % 7)  # Tuesday is weekday 1
            
            if today.weekday() < 1:  # If today is Monday (weekday 0), adjust start to last Tuesday
                start -= timedelta(days=7)
            
            end = start + timedelta(days=6)
        
            if start <= date_obj <= end:
                bs = "\\"
                embed_description += f"**__{date_str}__**\n{level2} | {level7} | {level14.rstrip(bs)}\n"
        
            else:
                continue
        
        else:
            print(f"Unexpected date format: {date}")
    
    embed_message = discord.Embed(title=title, description=embed_description) 
    return embed_message 

class TreacheryAffixes(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def affixes(self, ctx):
        urls = ["https://keystone.guru/affixes", "https://keystone.guru/affixes?offset=1"]

        embed_message = discord.Embed(title="M+ Affixes from keystone.guru")
        embed_message.add_field(name="Current week", value=format_embed(scrape_data("https://keystone.guru/affixes"), "Current week").description)
        embed_message.add_field(name="Upcoming weeks", value=format_embed(scrape_data("https://keystone.guru/affixes?offset=1"), "Upcoming weeks").description)

        await ctx.send(embed=embed_message)
