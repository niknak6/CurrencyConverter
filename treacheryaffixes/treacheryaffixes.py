from redbot.core import commands
import requests
from bs4 import BeautifulSoup

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

        # Initialize an empty string to store all affixes
        all_affixes = ""

        for week_row in table_rows:
            # Find the date in the first column
            date = week_row.find('td', {'class': 'first_column'}).get_text(strip=True)

            # Find the affixes in the other columns
            affixes = [td.get_text(strip=True) for td in week_row.find_all('td')[1:-1]]

            # Append the date and affixes to the string
            all_affixes += f"Date: {date}\nAffixes: {', '.join(affixes)}\n\n"

        return all_affixes

    @commands.command()
    async def affixes(self, ctx, offset: int = 0):
        affixes = self.fetch_and_parse_affixes(offset)
        await ctx.send(affixes)
