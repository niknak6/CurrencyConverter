from .CurrencyConverter import CurrencyConverter

def setup(bot):
    bot.add_cog(CurrencyConverter(bot))
