# Import the necessary libraries
import requests
from bs4 import BeautifulSoup
from redbot.core import commands

# Define the cog class
class TreacheryAffixes(commands.Cog):
    """A cog that shows the current and upcoming World of Warcraft M+ Affixes."""

    def __init__(self, bot):
        self.bot = bot

    # Define the command
    @commands.command()
    async def affixes(self, ctx):
        """Shows the current and upcoming World of Warcraft M+ Affixes."""

        # Get the HTML data from keystone.guru
        current_url = "https://keystone.guru/affixes"
        upcoming_url = "https://keystone.guru/affixes?offset=1"
        current_response = requests.get(current_url)
        upcoming_response = requests.get(upcoming_url)

        # Parse the data using BeautifulSoup
        current_soup = BeautifulSoup(current_response.text, "html.parser")
        upcoming_soup = BeautifulSoup(upcoming_response.text, "html.parser")

        # Find the table row that contain the affix information
        # Change the class name to match the new HTML structure
        current_row = current_soup.find("tr", class_="current_week")
        upcoming_rows = upcoming_soup.find_all("tr", class_="table_row")

        # Extract the relevant information from each row
        current_date = current_row.find("span").text.strip()
        current_affixes = [div.text.strip() for div in current_row.find_all("div", class_="col")]
        upcoming_data = []
        for row in upcoming_rows:
            date = row.find("span").text.strip()
            affixes = [div.text.strip() for div in row.find_all("div", class_="col")]
            upcoming_data.append((date, affixes))

        # Format the output using markdown elements
        output = f"**Current week ({current_date}):**\n"
        output += " | ".join(current_affixes) + "\n\n"
        output += "**Upcoming weeks:**\n"
        for date, affixes in upcoming_data:
            output += f"**{date}:**\n"
            output += " | ".join(affixes) + "\n\n"

        # Send the output to the user
        await ctx.send(output)
