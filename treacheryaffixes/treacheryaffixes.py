from redbot.core import commands
import requests
from bs4 import BeautifulSoup
from discord import Embed

class TreacheryAffixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def fetch_and_parse_affixes(offset: int):
        # Fetch the HTML from the website
        response = requests.get(f'https://keystone.guru/affixes?offset={offset}')
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all table rows
        table_rows = soup.find_all('tr', {'class': ['table_row odd', 'table_row even']})

        # Initialize an empty list to store all affixes
        all_affixes = []

        for week_row in table_rows:
            # Find the date in the first column
            date = week_row.find('td', {'class': 'first_column'}).get_text(strip=True)

            # Find the affixes in the other columns
            affixes = [td.get_text(strip=True) for td in week_row.find_all('td')[1:-1]]

            # Append the date and affixes to the list
            all_affixes.append((date, affixes))

        return all_affixes

    @commands.command()
    async def affixes(self, ctx):
        # Fetch and parse affixes for current week and future weeks
        current_week_affixes = self.fetch_and_parse_affixes(0)[-1]
        future_weeks_affixes = self.fetch_and_parse_affixes(1)

        # Create a new embed object
        embed = Embed(title="Mythic+ Affixes", colour=0x3498db)

        # Add a field to the embed for current week's affixes
        embed.add_field(name=current_week_affixes[0], value=', '.join(current_week_affixes[1]), inline=False)

        for date, affix_list in future_weeks_affixes:
            # Add a field to the embed for each future week's affixes
            embed.add_field(name=date, value=', '.join(affix_list), inline=False)

        await ctx.send(embed=embed)
