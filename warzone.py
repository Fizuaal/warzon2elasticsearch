import asyncio, json , os
from callofduty import Mode, Platform, Title, Login
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

async def lambda_handler():
    login = 'login'
    password = 'pass'
    client = await Login(login, password)
    friends = await get_friends(client)
    for player in friends:
        username=player['username']
        print(f"saving {username}")
        await save_player_stats(client, player)

async def get_player_stats():
    login = os.environ.get('login')
    password = os.environ.get('pass')
    client = await Login(login, password)
    playername="Ami1"
    results = await client.SearchPlayers(
        Platform.Activision, playername, limit=30)
    print(results)
    for player in results:
        profile = await player.profile(Title.ModernWarfare, Mode.Multiplayer)
        if profile["lifetime"]["all"]["properties"] is not None :
            print(f"{player.username} ({player.platform.name})")  
            # print(profile["lifetime"]["all"]["properties"]["kdRatio"])

async def save_player_stats(client, player):
    matches = await client.GetPlayerMatchesSummary(
        player["platform"] , player["username"],Title.ModernWarfare , Mode.Warzone, limit=200)
    body = {
        'name': player["username"], 
        'stats': matches,
        'timestamp': datetime.now() - timedelta(hours=1)
    }
    es = Elasticsearch("localhost")
    es.indices.create(index='wzf', ignore=400)
    res = es.index(index="wzf", body=body)
    print(res)


async def get_friends(client):
    friends = await client.GetMyFriends()
    friends_usernames = [
            {"username":"Ami1", "platform":Platform.BattleNet},
            {"username":"Ami2", "platform":Platform.BattleNet},
            {"username":"Ami3", "platform":Platform.BattleNet}
            ]
    for friend in friends:
        if "#" in friend.username:
            friends_usernames.append({"username":friend.username, "platform":friend.platform})
    return friends_usernames

asyncio.get_event_loop().run_until_complete(lambda_handler())
