# Import the required modules
import discord
from redbot.core import commands
import requests
from bs4 import BeautifulSoup

# Define the cog class
class TreacheryAffixes(commands.Cog):
    """A cog that shows the current and upcoming World of Warcraft M+ Affixes."""

    def __init__(self, bot):
        self.bot = bot

    # Define the command affixes
    @commands.command()
    async def affixes(self, ctx):
        """Shows the current and upcoming World of Warcraft M+ Affixes."""

        # Get the current week affixes from keystone.guru
        current_url = "https://keystone.guru/affixes"
        current_response = requests.get(current_url)
        current_soup = BeautifulSoup(current_response.text, "html.parser")
        current_row = current_soup.find("tr", class_="table_row even current_week") # Changed this line to find the correct row
        current_date = current_row.find("span").text.strip()
        current_affixes = [div.text.strip() for div in current_row.find_all("div", class_="col d-lg-block d-none pl-1")]

        # Get the upcoming weeks affixes from keystone.guru
        upcoming_url = "https://keystone.guru/affixes?offset=1"
        upcoming_response = requests.get(upcoming_url)
        upcoming_soup = BeautifulSoup(upcoming_response.text, "html.parser")
        upcoming_rows = upcoming_soup.find_all("tr", class_="table_row")
        upcoming_dates = [row.find("span").text.strip() for row in upcoming_rows]
        upcoming_affixes = [[div.text.strip() for div in row.find_all("div", class_="col d-lg-block d-none pl-1")] for row in upcoming_rows]

        # Create an embed to display the affixes
        embed = discord.Embed(title="World of Warcraft M+ Affixes", color=discord.Color.blurple())
        embed.add_field(name=f"Current week ({current_date})", value="\n".join(current_affixes), inline=False)
        for i in range(len(upcoming_dates)):
            embed.add_field(name=f"Upcoming week {i+1} ({upcoming_dates[i]})", value="\n".join(upcoming_affixes[i]), inline=False)
        embed.set_footer(text=f"Data source: keystone.guru")

        # Send the embed to the context channel
        await ctx.send(embed=embed)
