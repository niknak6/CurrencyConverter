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
    # Loop through the table cells that have the affix icons and names using the class attribute of the div element inside each table cell 
    for td in week.find_all("td", class_="border_top"):
        # Get the p element that has the affix name 
        p = td.find("p")
        # If the p element exists, append its text to the affix list
        if p:
            affixes.append(p.text.strip())
    # Return the affix list
    return affixes

# Define a function to get the start date for a given week
def get_start_date(week):
    # Get the div element that has the start date using the class attribute of the div element
    div = week.find("div", class_="affix_row")
    # Get the span element that has the start date inside the div element
    span = div.find("span")
    # Return the span text as a string
    return span.text.strip()

# Define a function to get the current week from keystone.guru/affixes
def get_current_week():
    # Send a GET request to keystone.guru/affixes and get the response content as HTML using requests module
    response = requests.get("https://keystone.guru/affixes")
    html = response.content
    # Parse the HTML using BeautifulSoup module
    soup = BeautifulSoup(html, "html.parser")
    # Find the table element that has the affixes overview table using the class attribute of the table element
    table = soup.find("table", class_="affixes_overview_table")
    # Find the last table row element that has the current week data using the class attribute of the table row element 
    week = table.find("tr", class_="current_week")
    # Get the start date and affixes for

the current week using get_start_date and get_affixes helper functions
start_date = get_start_date(week)
affixes = get_affixes(week)
# Return a tuple of start date and affixes
return (start_date, affixes)

# Define a function to get the upcoming weeks from keystone.guru/affixes?offset=1
def get_upcoming_weeks():
# Send a GET request to keystone.guru/affixes?offset=1 and get the response content as HTML using requests module
response = requests.get("https://keystone.guru/affixes?offset=1")
html = response.content
# Parse the HTML using BeautifulSoup module
soup = BeautifulSoup(html, "html.parser")
# Find the table element that has the affixes overview table using the class attribute of the table element
table = soup.find("table", class_="affixes_overview_table")
# Find all non-timewalking weeks using a list comprehension and checking if "timewalking" is not in their class attribute 
weeks = [tr for tr in table.find_all("tr") if "timewalking" not in tr["class"]]
# Initialize an empty list to store the upcoming weeks data 
upcoming_weeks = []
# Loop through each week and get their start date and affixes using get_start_date and get_affixes helper functions 
for week in weeks:
    start_date = get_start_date(week)
    affixes = get_affixes(week)
    # Append a tuple of start date and affixes to the upcoming weeks list 
    upcoming_weeks.append((start_date, affixes))
# Return the upcoming weeks list 
return upcoming_weeks

# Define a function to format and print the current and upcoming weeks data in an embed message
def print_affixes():
# Initialize an empty string to store the output 
output = ""
# Get the current week and upcoming weeks data using get_current_week and get_upcoming_weeks functions 
current_week = get_current_week()
upcoming_weeks = get_upcoming_weeks()
# Format and append the data to the output string using f-strings and markdown syntax 
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
# Return the output string 
return output
