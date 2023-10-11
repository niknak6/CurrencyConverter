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
            # Find the date in the first column and reformat it
            date = week_row.find('td', {'class': 'first_column'}).get_text(strip=True)
            year, month, day_hour = date.split('/')
            day, hour = day_hour.split('@')
            month_number = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }.get(month[:3], '')
            formatted_date = f"{month_number}/{day}/{year[-2:]}"

            # Find the affixes in the other columns
            affixes = [td.get_text(strip=True) for td in week_row.find_all('td')[1:-1]]

            # Append the date and affixes to the list
            all_affixes.append((formatted_date, affixes))

        return all_affixes

    @commands.command()
    async def affixes(self, ctx):
        # Fetch and parse affixes for current week and future weeks
        current_week_affixes = self.fetch_and_parse_affixes(0)[-1]
        future_weeks_affixes = self.fetch_and_parse_affixes(1)

        # Create a new embed object
        embed = Embed(title="Mythic+ Affixes", colour=0x3498db)

        # Add a field to the embed for current week's affixes
        embed.add_field(name="Current Week", value=f"{current_week_affixes[0]}: {', '.join(current_week_affixes[1])}", inline=False)

        # Add a field to the embed for upcoming weeks' affixes
        embed.add_field(name="Upcoming Weeks", value='\n'.join([f"{date}: {', '.join(affix_list)}" for date, affix_list in future_weeks_affixes]), inline=False)

        await ctx.send(embed=embed)
