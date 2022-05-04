# This example prints your teammates names as soon as you enter champ select
# Useful for if you are wanting to lookup stats etc on your teammates

# Import LCU Driver
from lcu_driver import Connector

# Initialize the variable
connector = Connector()

# Connected to League Client
@connector.ready
async def connect(connection):
    # Set previous game ID to 999999 (non existent game)
    connection.locals['gameId'] = 999999

# Websocket Champ Select Updates
@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def champ_select(connection, event):
    # If event is from a different game than the previous (only run once per champ select)
    if event.data['gameId'] != connection.locals['gameId']:
        # Set game id to current
        connection.locals['gameId'] = event.data['gameId']
        # Initialize list of summoners
        summoners = []

        # Loop through team
        for summoner in event.data['myTeam']:
            # Request additional information for each summoner
            summ = await connection.request('get', f'/lol-summoner/v1/summoners/{summoner["summonerId"]}')
            # Parse JSON
            summ = await summ.json()
            # Get their display name
            name = summ["displayName"]
            # Append name to list
            summoners.append(name)
        # Print list of names
        print(summoners)

# Start the connector
connector.start()
