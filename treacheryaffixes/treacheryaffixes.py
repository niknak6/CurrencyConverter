import requests
from bs4 import BeautifulSoup
from redbot.core import commands

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
        table = soup.find("table", class_="affixes_overview_table")
        
        # Initialize an empty list to store the results
        results = []
        
        # Loop through the table rows, except the header row
        for row in table.find_all("tr")[1:]:
            # Initialize an empty dictionary to store the data for this week
            week = {}
            
            # Get the start date from the first column
            start_date = row.find("td", class_="first_column").text.strip()
            week["start_date"] = start_date
            
            # Get the affixes from the second, third, and fourth columns
            affixes = []
            for column in row.find_all("td")[1:4]:
                # Get the affix name from the tooltip attribute
                # Check if the div tag exists before accessing its attribute
                try:
                    affix_name = column.find("div", class_="affix_icon")["data-original-title"]
                except TypeError:
                    affix_name = "Unknown"
                affixes.append(affix_name)
            week["affixes"] = affixes
            
            # Get the seasonal affix from the fifth column, if any
            seasonal_affix = row.find("td", class_="last_column").text.strip()
            if seasonal_affix:
                week["seasonal_affix"] = seasonal_affix
            
            # Append the week dictionary to the results list
            results.append(week)
        
        # Return the results list
        return results

    @commands.command()
    async def affixes(self, ctx):
        """Shows the Mythic+ Schedule for Treachery."""

        # Get the current week affixes from https://keystone.guru/affixes
        current_week = self.get_affixes("https://keystone.guru/affixes")[0]

        # Create an embed for the current week affixes
        current_week_embed = discord.Embed(
            title="Current Week Affixes",
            description=f"The current week started on: {current_week['start_date']}",
            color=discord.Color.blue()
        )
        
        # Add fields for each affix level and name
        current_week_embed.add_field(name="+2", value=current_week["affixes"][0], inline=True)
        current_week_embed.add_field(name="+7", value=current_week["affixes"][1], inline=True)
        current_week_embed.add_field(name="+14", value=current_week["affixes"][2], inline=True)

        # Add a field for the seasonal affix, if any
        if "seasonal_affix" in current_week:
            current_week_embed.add_field(name="Seasonal", value=current_week["seasonal_affix"], inline=True)

        # Send the embed to the channel
        await ctx.send(embed=current_week_embed)

        # Get the upcoming weeks affixes from https://keystone.guru/affixes?offset=1
        upcoming_weeks = self.get_affixes("https://keystone.guru/affixes?offset=1")

        # Create an embed for each upcoming week affixes
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

            # Send the embed to the channel
            await ctx.send(embed=upcoming_week_embed)
