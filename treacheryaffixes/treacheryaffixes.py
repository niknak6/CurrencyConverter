import requests
from bs4 import BeautifulSoup
from redbot.core import commands

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
        # Send a message to the channel saying that the output is printed
        await ctx.send("The output from the print_affixes function is printed to the terminal. Please check it and see if there is any error or missing data.")

# Define a function to get the affixes for a given week
def get_affixes(week):
    # Initialize an empty list to store the affix names
    affixes = []
    # Loop through the table cells that contain the affix icons and names
    for td in week.find_all("td")[1:]:
        # Get the div element that has the affix name
        div = td.find("div", class_="affix_row")
        # Get the span element that has the affix name
        span = div.find("span", class_="d-lg-block")
        # If the span element exists, append its text to the affix list
        if span:
            affixes.append(span.text.strip())
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
    # Find the last table row element that has the current week data
    week = table.find_all("tr", class_="table_row")[-1]
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
    # Find all the table row elements that have the upcoming week data
    weeks = table.find_all("tr", class_="table_row")
    # Initialize an empty list to store the upcoming weeks data
    upcoming_weeks = []
    # Loop through each week element
    for week in weeks:
        # Get the start date and affixes for each week using the helper functions
        start_date = get_start_date(week)
        affixes = get_affixes(week)
        # Append a tuple of start date and affixes to the upcoming weeks list
        upcoming_weeks.append((start_date, affixes))
    # Return the upcoming weeks list
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

     output += f"- Source: [keystone.guru](https://docs.discord.red/en/stable/framework_utils.html)\n\n"
    
     output += "**Upcoming Weeks**\n\n"
    
     for week in upcoming_weeks:
         output += f"- Start date: {week[0]}\n"
         output += f"- Affixes: {', '.join(week[1])}\n\n"
    
     output += f"Source: [keystone.guru](https://docs.discord.red/en/stable/framework_utils.html)"
     
     return output
