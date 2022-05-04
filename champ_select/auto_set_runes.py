# This example imports runes into the client on champion lock in
# It deletes and adds a new page due to the client not updating a current page
# For more information see https://hextechdocs.dev/how-to-set-runes-using-lcu/

# Import LCU Driver
from lcu_driver import Connector
# Importing requests to use a runes API
import requests

#Initialize the variable
connector = Connector()

#Connected to League Client
@connector.ready
async def connect(connection):
    # Set previous game ID to 999999 (non existent game)
    connection.locals['gameId'] = 999999
    # Set current champion ID to 0
    connection.locals['championId'] = 0

# Function to change rune pages
async def change_rune_page(connection, champion):
    # Example runes API
    # Please do not use this API in production
    # Make your own runes API through collection matches through Match-V5 etc.
    runes = requests.get(f'https://www.bangingheads.net/runes?champion={champion}').json()

    # Get current page information so we know what to delete
    page = await connection.request('get', '/lol-perks/v1/currentpage')
    page = await page.json()

    # Delete the current page
    await connection.request('delete', f'/lol-perks/v1/pages/{page["id"]}')

    # Add a new page with the runes data requested
    # You could keep the name to give the illusion of only changing the runes in it
    await connection.request('post', '/lol-perks/v1/pages', data={
        "name": "BangingHeads Example",
        "primaryStyleId": runes['primaryTree'],
        "subStyleId": runes['secondaryTree'],
        "selectedPerkIds": runes['perks'],
        "current": True
    })


# Websocket Champ Select Updates
@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def champ_select(connection, event):
    # If event is from a different game than the previous (only run once per champ select)
    if event.data['gameId'] != connection.locals['gameId']:
        # Loop through actions looking for lock in
        for action in event.data['actions'][0]:
            # If there is a pick that is completed for the current summoner
            if action['actorCellId'] == event.data['localPlayerCellId'] and action['type'] == "pick" and action['completed'] == True:
                # Update game and champion so we don't try to make another page if not necessary
                connection.locals['gameId'] = event.data['gameId']
                connection.locals['championId'] = action['championId']
                # Change Rune Pages to correct page
                await change_rune_page(connection, action['championId'])
                return

    # If same game but champion changed due to trade, change page again
    elif event.data['gameId'] == connection.locals['gameId'] and event.data['myTeam'][event.data['localPlayerCellId']]['championId'] != connection.locals['championId']:
        await change_rune_page(connection, event.data['myTeam'][event.data['localPlayerCellId']]['championId'])


#Start the connector
connector.start()