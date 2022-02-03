from urllib import response
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import os
import datetime 
from discord.embeds import EmbedProxy
from datetime_utils import get_zone_id, get_zone_time, get_utc_timestamp


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

bot = commands.Bot(command_prefix='?', description=description)

def format_weather_response(response_content:dict):
    "Format response message as embedded object"
    name = response_content['name']
    description = response_content['weather'][0]['description']
    country = response_content['sys']['country']
    icon_id = response_content['weather'][0]['icon']
    temp_min = response_content['main']['temp_min']
    temp_max = response_content['main']['temp_max']
    
    time_stamp = response_content['dt']
    time_zone = datetime.timezone(datetime.timedelta(seconds = response_content['timezone']))
    local_time = datetime.datetime.fromtimestamp(time_stamp,tz=time_zone).strftime("%A, %d-%b-%y, %I:%M %p")
    
    embedded_dict = {}
    embedded_dict['title'] = f'Weather {name} - {country}'
    embedded_dict['description'] = description
    embedded_obj = discord.Embed.from_dict(embedded_dict)
    embedded_obj.set_image(url=f'https://openweathermap.org/img/wn/{icon_id}@2x.png')
    embedded_obj.set_footer(text=local_time)
    embedded_obj.add_field(name='min:',value=temp_min,inline=True)
    embedded_obj.add_field(name='max:',value=temp_max,inline=True)
    return embedded_obj
    
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def weather(ctx,city:str,*args):
    """Send weather information
    Args:
        city: str - must be a valid city
        args: additional information specifier
            TO BE ADDED
    """
    #Fetching API key
    if "OPEN_WEATHER_TOKEN" in os.environ:
        OPEN_WEATHER_API = os.getenv("OPEN_WEATHER_TOKEN")
    else:
        raise ValueError("Open weather map API not provided!")
    
    #Check if unit is requested
    if "units" in args:
        try:
            unit_index = args.index('units')
            unit_value = args[unit_index+1]
            if unit_value not in ['standard','metric','imperial']:
                raise ValueError(f"Unit {unit_value} must be one of 'standard', 'imperial','metric'.")
        except:
            unit_value = 'metric'
    else:
        unit_value='metric'
        
    #Format request parameters:
    params = {'q':city,'appid':OPEN_WEATHER_API,'units':unit_value}
    response = requests.get('https://api.openweathermap.org/data/2.5/weather',params=params)
    response.raise_for_status()
    response_content = response.json()

    #Send weather formatted response
    await ctx.send(embed = format_weather_response(response_content))

@bot.command()
async def supported_time_zone(ctx):
    pass

@bot.command()
async def supported_weather_locations(ctx):
    pass

@bot.command()
async def current_time(ctx,region:str):
    try:
        zone_id = get_zone_id(region)
    except ValueError as e:
        await ctx.send(e)
        raise
    ts= get_utc_timestamp()
    result = get_zone_time(zone_id,ts)
    await ctx.send(result)
       
@bot.command()
async def convert_time(ctx,region_from:str, region_to:str, datetime:str):
    """Command to convert datetime from one region to another. To check supported time_zones, use "?supported_time_zone"

    Args:
        ctx ([type]): context manager
        region_from (str): region where input datetime is provided. Long region names should be enclosed in " ".
        region_to (str): region where output datetime is required. Long region names should be enclosed in " ".
        datetime (str): provided datetime. String MUST be enclosed in double quotation " ". 
        The following formats are accepted: 
            "day-month-year hour:minute AM/PM"
            "day-month-year hour:minute" - in 24 hour format
            "hour:minute AM/PM"
            "hour:minute" - in 24 hour format
        Examples of acceptable datetime: 
        "Monday 1-Jul-20 23:32"
        "11:32 PM"
    """
    try:
        zone_from = get_zone_id(region_from)
        zone_to   = get_zone_id(region_to)
    except ValueError as e:
        await ctx.send(e)
        raise 
    await ctx.send("Please ensure that datetime is entered in this format: "\
                   "week_day day-month-year hour:minute AM/PM. "\
                   "Type ?help convert_time for more examples.")


bot.run(TOKEN)