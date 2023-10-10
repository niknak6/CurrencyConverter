import requests
from bs4 import BeautifulSoup
from redbot.core import commands
import discord # Import the discord module

class TreacheryAffixes(commands.Cog):
    """A cog that shows the current affixes for Treachery."""

    def __init__(self, bot):
        self.bot = bot

    def get_affixes(self, url):
        # Get the HTML content from the URL
        response = requests.get(url)
        html = response.text
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the table that contains the affixes
        table = soup.find("table", class_="table-affixes") # Change the class name to match the website
        
        # Initialize an empty list to store the results
        results = []
        
        # Check if the table tag exists before using find_all on it
        try:
            table = soup.find("table", class_="table-affixes")
            rows = table.find_all("tr")[1:]
        except AttributeError:
            rows = [] # Assign an empty list to rows if the table tag is not found
        
        # Loop through the table rows, except the header row
        for row in rows:
            # Initialize an empty dictionary to store the data for this week
            week = {}
            
            # Get the start date from the first column
            start_date = row.find("td", class_="affixes-start-date").text.strip()
            week["start_date"] = start_date
            
            # Get the affixes from the second column
            affixes = []
            for affix in row.find("td", class_="affixes-list").find_all("div", class_="affix"):
                # Get the affix name from the tooltip attribute
                affix_name = affix["data-original-title"]
                affixes.append(affix_name)
            week["affixes"] = affixes
            
            # Get the seasonal affix from the third column, if any
            seasonal_affix = row.find("td", class_="affixes-seasonal").text.strip()
            if seasonal_affix:
                week["seasonal_affix"] = seasonal_affix
            
            # Append the week dictionary to the results list
            results.append(week)
        
        # Return the results list
        return results

    @commands.command()
    async def affixes(self, ctx):
        """Shows the Mythic+ Schedule for Treachery."""

        # Check if the list is empty before accessing its elements
        try:
            current_week = self.get_affixes("https://keystone.guru/affixes")[0] # Add a try-except block to handle IndexError
        except IndexError:
            current_week = None # Assign None to current_week if the list is empty

        # Check if the current_week variable is not None before accessing its keys
        try: 
            description=f"The current week started on: {current_week['start_date']}" # Add a try-except block to handle TypeError
        except TypeError:
            description="No current week data available" # Assign a default message to description if current_week is None

        # Create an embed for the current week affixes
        current_week_embed = discord.Embed(
            title="Current Week Affixes",
            description=description,
            color=discord.Color.blue()
        )
        
        # Add fields for each affix level and name
        current_week_embed.add_field(name="+2", value=current_week["affixes"][0], inline=True)
        current_week_embed.add_field(name="+7", value=current_week["affixes"][1], inline=True)
        current_week_embed.add_field(name="+14", value=current_week["affixes"][2], inline=True)

        # Add a field for the seasonal affix, if any
        if "seasonal_affix" in current_week:
            current_week_embed.add_field(name="Seasonal", value=current_week["seasonal_affix"], inline=True)

        # Create a list of embeds
        embed_list = [current_week_embed] # Add the current week embed to the list

        # Get the upcoming weeks affixes from https://keystone.guru/affixes?offset=1
        upcoming_weeks = self.get_affixes("https://keystone.guru/affixes?offset=1")

        # Loop through the upcoming weeks and create an embed for each one
        for i, week in enumerate(upcoming_weeks):
            upcoming_week_embed = discord.Embed(
                title=f"Week {i+1} Affixes",
                description=f"The week {i+1} starts on: {week['start_date']}",
                color=discord.Color.green()
            )

            # Add fields for each affix level and name
            upcoming_week_embed.add_field(name="+2", value=week["affixes"][0], inline=True)
            upcoming_week_embed.add_field(name="+7", value=week["affixes"][1], inline=True)
            upcoming_week_embed.add_field(name="+14", value=week["affixes"][2], inline=True)

            # Add a field for the seasonal affix, if any
            if "seasonal_affix" in week:
                upcoming_week_embed.add_field(name="Seasonal", value=week["seasonal_affix"], inline=True)

            # Add the upcoming week embed to the list
            embed_list.append(upcoming_week_embed)

        # Send the list of embeds in one message
        await ctx.send(embeds=embed_list) # Use the embeds parameter instead of the embed parameter
