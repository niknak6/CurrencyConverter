from redbot.core import commands
import requests

class CurrencyConverter(commands.Cog):
    """A cog that converts currencies using API Ninjas"""

    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.api-ninjas.com/v1/convertcurrency"

    @commands.command(name="currconv")
    async def convert(self, ctx, have: str, want: str, amount: float):
        """Converts an amount of one currency to another

        Parameters
        ----------
        have: The currency code of the currency you have (e.g. USD)
        want: The currency code of the currency you want (e.g. EUR)
        amount: The amount of currency to convert
        """
        # Validate the parameters
        if len(have) != 3 or len(want) != 3:
            await ctx.send("Please enter valid currency codes (e.g. USD, EUR, GBP)")
            return
        if amount <= 0:
            await ctx.send("Please enter a positive amount of currency to convert")
            return

        # Make a request to the API
        params = {
            "have": have.upper(),
            "want": want.upper(),
            "amount": amount
        }
        response = requests.get(self.api_url, params=params)

        # Check the status code and parse the response
        if response.status_code == 200:
            data = response.json()
            new_amount = data["quotes"][f"{have.upper()}{want.upper()}"]
            await ctx.send(f"{amount} {have.upper()} is equal to {new_amount:.2f} {want.upper()}")
        else:
            await ctx.send(f"Sorry, something went wrong. Error code: {response.status_code}")
