from redbot.core import commands
import requests
from bs4 import BeautifulSoup

class TreacheryAffixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def affixes(self, ctx):
        # Fetch the HTML from the website
        response = requests.get('https://keystone.guru/affixes')
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table row for the current week
        current_week_row = soup.find_all('tr', {'class': ['table_row even', 'current_week']})[-1]

        # Find the date in the first column
        date = current_week_row.find('td', {'class': 'first_column'}).get_text(strip=True)

        # Find the affixes in the other columns
        affixes = [td.get_text(strip=True) for td in current_week_row.find_all('td')[1:-1]]

        # Send a message with the affixes
        await ctx.send(f"Date: {date}\nAffixes: {', '.join(affixes)}")

    @commands.command()
    async def future_affixes(self, ctx, offset: int):
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

        # Send a message with all affixes
        await ctx.send(all_affixes)
