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

            # Return the affixes data list
            return affixes_data
        
        else:
            return "Table element not found"
    
    else:
        return f"Failed to fetch data from {url}"

# Define a function to format the data as an embed message
def format_embed(data, title):
    if isinstance(data, str):
        return data

    embed_description = ""
    
    for row in data:
        date = row["start_date"]
        level2, level7, level14 = row["affix_names"]
        
        date_pattern = re.compile(r"\d{4}/\w{3}/\d{2}\n\n\n     @ \d{2}h")
        
        if date_pattern.match(date):
            date_obj = datetime.strptime(date, "%Y/%b/%d\n\n\n     @ %Hh")
        
            date_str = date_obj.strftime("%m/%d/%y")
        
            today = datetime.today()
            start = today - timedelta(days=(today.weekday() - 1) % 7)
            
            if today.weekday() < 1:
                start -= timedelta(days=7)
            
            end = start + timedelta(days=6)
        
            if start <= date_obj <= end:
                bs = "\\"
                embed_description += f"**__{date_str}__**\n{level2} | {level7} | {level14.rstrip(bs)}\n"
        
            else:
                continue
        
        else:
            return f"Unexpected date format: {date}"
    
    embed_message = discord.Embed(title=title, description=embed_description) 
    return embed_message 

class TreacheryAffixes(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def debugaffixes(self, ctx):
        urls = ["https://keystone.guru/affixes", "https://keystone.guru/affixes?offset=1"]

        current_week_data = scrape_data("https://keystone.guru/affixes")
        upcoming_weeks_data = scrape_data("https://keystone.guru/affixes?offset=1")

        await ctx.send(f"Current week data: {current_week_data}")
        await ctx.send(f"Upcoming weeks data: {upcoming_weeks_data}")

        current_week_embed = format_embed(current_week_data, "Current week")
        upcoming_weeks_embed = format_embed(upcoming_weeks_data, "Upcoming weeks")

        await ctx.send(f"Current week embed: {current_week_embed}")
        await ctx.send(f"Upcoming weeks embed: {upcoming_weeks_embed}")

        embed_message = discord.Embed(title="M+ Affixes from keystone.guru")
        embed_message.add_field(name="Current week", value=current_week_embed.description)
        embed_message.add_field(name="Upcoming weeks", value=upcoming_weeks_embed.description)

        await ctx.send(embed=embed_message)
