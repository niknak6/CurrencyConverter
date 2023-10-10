import requests
from bs4 import BeautifulSoup
from redbot.core import commands
import discord # Import the discord module

# Define a class for the cog
class TreacheryAffixes(commands.Cog):
    # Define a constructor for the cog
    def __init__(self, bot):
        self.bot = bot
    
    # Define a command called affixes
    @commands.command()
    async def affixes(self, ctx):
        # Call the print_affixes function and get the output as a string
        output = print_affixes()
        # Create an embed object with the output as the description
        embed = discord.Embed(description=output)
        # Send the embed message to the channel
        await ctx.send(embed=embed)

    # Define a command called affixdiag
    @commands.command()
    async def affixdiag(self, ctx):
        # Call the print_affixes function and get the output as a string
        output = print_affixes()
        # Print the output to the terminal
        print(output)
        # Create an embed object with the output as the description
        embed = discord.Embed(description=output)
        # Send the embed message to the channel
        await ctx.send(embed=embed)

# Define a function to get the affixes for a given week
def get_affixes(week):
    # Initialize an empty list to store the affix names
    affixes = []
    # Loop through the table cells that have the affix icons and names using the class attribute of the div element inside each table cell # Change from index to class selector
    for td in week.find_all("td", class_="border_top"):
        # Get the p element that has the affix name # Change from h5 to p element
        p = td.find("p")
        # If the p element exists, append its text to the affix list
        if p:
            affixes.append(p.text.strip())
    # Return the affix list
    return affixes

# Define a function to get the start date for a given week
def get_start_date(week):
    # Get the div element that has the start date
    div = week.find("div", class_="affix_row")
    # Get the span element that has the start date
    span = div.find("span")
    # Return the span text as a string
    return span.text.strip()

# Define a function to get the current week from keystone.guru/affixes
def get_current_week():
    # Send a GET request to keystone.guru/affixes and get the response content as HTML
    response = requests.get("https://keystone.guru/affixes")
    html = response.content
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Find the table element that has the affixes overview table
    table = soup.find("table", class_="affixes_overview_table")
    # Find the last table row element that has the current week data using the class attribute of the table row element # Change from -1 to current_week to find the current week row
    week = table.find("tr", class_="current_week")
    # Get the start date and affixes for the current week using the helper functions
    start_date = get_start_date(week)
    affixes = get_affixes(week)
    # Return a tuple of start date and affixes
    return (start_date, affixes)

# Define a function to get the upcoming weeks from keystone.guru/affixes?offset=1
def get_upcoming_weeks():
    # Send a GET request to keystone.guru/affixes?offset=1 and get the response content as HTML
    response = requests.get("https://keystone.guru/affixes?offset=1")
    html = response.content
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Find the table element that has the affixes overview table
    table = soup.find("table", class_="affixes_overview_table")
    # Find all the table row elements that have the upcoming week data except for timewalking weeks using a lambda function and a negative lookbehind assertion in a regular expression # Change from all rows to non-timewalking rows 
    weeks = table.find_all(lambda tag: tag.name == "tr" and tag.has_attr("class") and not re.search("(?<!timewalking) ", " ".join(tag["class"])))
    
     upcoming_weeks = []
    
     for week in weeks:
         start_date = get_start_date(week)
         affixes = get_affixes(week)
         upcoming_weeks.append((start_date, affixes))
    
     return upcoming_weeks

# Define a function to format and print the current and upcoming weeks data in an embed message
def print_affixes():
    
     output = ""
    
     current_week = get_current_week()
     upcoming_weeks = get_upcoming_weeks()
    
     output += "**World of Warcraft M+ Affixes**\n\n"
    
     output += "**Current Week**\n\n"
    
     output += f"- Start date: {current_week[0]}\n"
    
     output += f"- Affixes: {', '.join(current_week[1])}\n\n"

     output += f"- Source: [keystone.guru]\n\n" # Use hyperlink format
    
     output += "**Upcoming Weeks**\n\n"
    
     for week in upcoming_weeks:
         output += f"- Start date: {week[0]}\n"
         output += f"- Affixes: {', '.join(week[1])}\n\n"
    
     output += f"Source: [keystone.guru]" # Use hyperlink format
     
     return output
