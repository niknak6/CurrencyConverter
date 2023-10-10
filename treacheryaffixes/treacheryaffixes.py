# Import the necessary modules
import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import bold
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re

class ScrapingError(Exception):
    pass

# Define a function to scrape the data from the website
def scrape_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the response status code is not 200
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", class_="affixes_overview_table")
        if table:
            affixes_data = []
            for row in table.find("tbody").find_all("tr"):
                row_data = {}
                start_date = row.find("td", class_="first_column").get_text().strip()
                row_data["start_date"] = start_date
                affix_names = []
                for affix in row.find_all("td")[1:]:
                    affix_name = affix.get_text().strip().rstrip("| ")
                    affix_names.append(affix_name)
                affix_names = affix_names[:3]
                row_data["affix_names"] = affix_names
                affixes_data.append(row_data)
            return affixes_data
        else:
            raise ScrapingError("Table element not found")
    except requests.exceptions.RequestException as e:
        raise ScrapingError(f"Error fetching data from {url}: {e}")

# Define a function to format the data as an embed message
def format_embed(data, title, upcoming_weeks=8):
    if isinstance(data, str):
        return data

    embed_description = ""
    
    for row in data:
        date = row["start_date"]
        level2, level7, level14 = row["affix_names"]
        
        # Check if the date string contains digits
        if any(char.isdigit() for char in date):
            date_pattern = re.compile(r"\d{4}/\w{3}/\d{2}.*")
            
            if date_pattern.match(date):
                date_obj = datetime.strptime(date[:15], "%Y/%b/%d\n\n\n")
            
                date_str = date_obj.strftime("%m/%d/%y")
            
                today = datetime.today()
                
                # Adjust the start of the week to Tuesday
                # Change this line to account for the website's update schedule
                # Old line: start = today - timedelta(days=(today.weekday() - 2) % 7 - 1)
                # New line: start = today - timedelta(days=(today.weekday() - 2) % 7)
                start = today - timedelta(days=(today.weekday() - 2) % 7)
                
                if today.weekday() < 2:
                    start -= timedelta(days=7)
                
                end = start + timedelta(days=6)
            
                # Check if the date falls within a range of upcoming_weeks weeks starting from the current week
                # Change this line to include the current week data
                # Old line: if start - timedelta(weeks=1) <= date_obj < start + timedelta(weeks=upcoming_weeks):
                # New line: if start <= date_obj < start + timedelta(weeks=upcoming_weeks):
                if start <= date_obj < start + timedelta(weeks=upcoming_weeks):
                    bs = "\\"
                    embed_description += f"**__{date_str}__**\n{level2} | {level7} | {level14.rstrip(bs)}\n"
            
            else:
                continue
        
        else:
            continue
    
    embed_message = discord.Embed(title=title, description=embed_description) 
    return embed_message 

class TreacheryAffixes(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def affixes(self, ctx):
        urls = ["https://keystone.guru/affixes", "https://keystone.guru/affixes?offset=1"]

        try:
            current_week_data = scrape_data(urls[0])
            upcoming_weeks_data = scrape_data(urls[1])

            current_week_embed = format_embed(current_week_data, "Current Week", upcoming_weeks=1)
            upcoming_weeks_embed = format_embed(upcoming_weeks_data, "Upcoming Weeks")

            if not isinstance(current_week_embed, str) and not isinstance(upcoming_weeks_embed, str):
                embed_message = discord.Embed(title="Mythic+ Schedule")
                embed_message.add_field(name="Current Week", value=current_week_embed.description)
                embed_message.add_field(name="Upcoming Weeks", value=upcoming_weeks_embed.description)

                await ctx.send(embed=embed_message)
            else:
                await ctx.send(f"An error occurred while formatting the data.")
        except ScrapingError as e:
            await ctx.send(f"An error occurred: {e}")
