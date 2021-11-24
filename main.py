from flask import Flask, render_template, request
import requests
import numpy as np
import pandas as pd
import json

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/converter', methods=['GET', 'POST'])
def converter():
    errors = ""
    url = "https://api.splinterlands.io/settings"
    response = requests.get(url).json()
    if request.method == "POST":
        amount = None
        try:
            amount = request.form.get('amount')
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form['amount'])
        if amount is not None:
            if request.method == "POST":
                selection = request.form['Currencies']
                if selection == "DEC":
                    decPrice = response['dec_price']
                    result = float(amount) * float(decPrice)            
                    result = str(result)
                    return render_template('converter.html', errors=errors, selection=selection, amount=amount, result=str(result))
                if selection == "SPS":
                    spsPrice = response['sps_price']
                    result = float(amount) * float(spsPrice)
                    result = str(result)
                    return render_template('converter.html', errors=errors, selection=selection, amount=amount, result=str(result))
                if selection == "LAND PLOT":
                    url = "https://wax.api.atomicassets.io/atomicmarket/v1/sales?state=1&collection_name=splintrlands&schema_name=land.claims&page=1&limit=1&order=asc&sort=price"
                    response = requests.get(url).json()                    
                    data = response['data']
                    storage = {}

                    for k, v in [(key, d[key]) for d in data for key in d]:
                        if k not in storage:
                            storage[k] = [v]
                        else:
                            storage[k].append(v)

                    data = storage['price']
                    storage = {}

                    for k, v in [(key, d[key]) for d in data for key in d]:
                        if k not in storage:
                            storage[k] = [v]
                        else:
                            storage[k].append(v)

                    currentPrice = storage['amount']
                    currentPrice = str(currentPrice)[2:-10]

                    waxAPI = "https://api.coingecko.com/api/v3/simple/price?ids=wax&vs_currencies=usd"
                    response = requests.get(waxAPI).json()
                    data = response['wax']
                    waxPrice = data['usd']
                    landPrice = float(currentPrice) * float(waxPrice)
                    result = float(amount) * float(landPrice)                    
                    return render_template('converter.html', selection=selection, amount=amount, result=str(result))
    return render_template('converter.html')


@app.route('/playerstats', methods=['GET', 'POST'])
def playerstats():
    errors = ""
    if request.method == 'POST':
        if request.form.get('submitStats'):
            player = None
            try:
                player = request.form['playerName'].lower()
            except:
                errors += "<p>{!r} is not a number.</p>\n".format(request.form['playerName'])
            if player is not None:
                url = f"https://api.splinterlands.io/players/balances?username={player}"
                response = requests.get(url).json()
                encodedJson = json.dumps(response, indent=4)
                data = json.loads(encodedJson)

                storage = {}
                for k, v in [(key, d[key]) for d in data for key in d]:
                    if k not in storage:
                        storage[k] = [v]
                    else:
                        storage[k].append(v)

                try:
                    tokens = storage['token']
                except KeyError:
                    return render_template('500.html')
                balances = storage['balance']
                df = pd.DataFrame(np.array([tokens, balances]).T)
                df.columns = ['Tokens', 'Balance']
                result = df.to_html(index=False, border=4, classes="table table-dark").replace('<th>', '<th class="th">')
                return render_template('playerstats.html', tableHtml=result, player=player)
        elif request.form.get('submitRichlist'):
            token = None
            try:
                token = request.form['richlist']
            except:
                errors += "<p>{!r} is not a number.</p>\n".format(request.form['playerName'])
            if token is not None:
                selection = request.form['richlist']
                url = f"https://api2.splinterlands.com/players/richlist?token_type={selection}"
                response = requests.get(url).json()
                richlist = response['richlist']
                storage = {}

                for k, v in [(key, d[key]) for d in richlist for key in d]:
                    if k not in storage:
                        storage[k] = [v]
                    else:
                        storage[k].append(v)

                player = storage['player']
                balance = storage['balance']

                df = pd.DataFrame(np.array([player, balance]).T)
                df.columns = ['player', 'balance']
                df.index += 1
                result = df.to_html(index=True, border=4, classes="table table-dark").replace('<th>', '<th class="th">')
                return render_template('playerstats.html', result=result, selection=selection)
    return render_template('playerstats.html')


@app.route('/guildstats', methods=['GET', 'POST'])
def guildstats():
    errors = ""
    url = "https://api2.splinterlands.com/guilds/list"
    response = requests.get(url).json()
    storage = {}

    for k, v in [(key, d[key]) for d in response for key in d]:
        if k not in storage:
            storage[k] = [v]
        else:
            storage[k].append(v)

    guildID = storage['id']
    guildNames = storage['name']

    if request.method == 'POST':
        getID = None            
        try:
            getID = request.form.get('getID')
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form['getID'])
        if getID is not None:
            selection = request.form['guilds']
            guildDict = {guildNames[i]: guildID[i] for i in range(len(guildNames))}
            getFinalID = guildDict[f'{selection}']
            return render_template('guildstats.html', guildNames=guildNames, getFinalID=getFinalID, selection=selection)
    if request.form.get('guildID'):
        guildID = None
        try:
            guildID = request.form['guildID']
        except:
            errors += "<p>{!r} is not a number.</p>\n".format(request.form['guildID'])
        if guildID is not None:
            url = f"https://api2.splinterlands.com/guilds/members?guild_id={guildID}"
            response = requests.get(url).json()
            encodedJson = json.dumps(response, indent=4)
            data = json.loads(encodedJson)

            storage = {}
            for k, v in [(key, d[key]) for d in data for key in d]:
                if k not in storage:
                    storage[k] = [v]
                else:
                    storage[k].append(v)

            playerList = []
            guildHall = []
            guildShop = []
            barracks = []
            arena = []
            totalcontributions = []

            try:
                for i in range(len(storage['player'])):
                    if storage['status'][i] == 'active':
                        player = storage['player'][i]
                        playerList.append(player)
                        contributions = json.loads(storage['data'][i])['contributions']
                        guildHallData = contributions.get('guild_hall') or int()
                        guildHall.append(guildHallData)
                        guildShopData = contributions.get('guild_shop') or {}
                        guildShopDEC = guildShopData.get('DEC') or int()
                        guildShop.append(guildShopDEC)
                        barracksData = contributions.get('barracks') or {}
                        barracksDEC = barracksData.get('DEC') or int()
                        barracks.append(barracksDEC)
                        arenaData = contributions.get('arena') or {}
                        arenaDEC = arenaData.get('DEC') or int()
                        arena.append(arenaDEC)
                        total = guildHallData + guildShopDEC + barracksDEC + arenaDEC
                        totalcontributions.append(total)
            except KeyError:
                return render_template('500.html')
        
            df = pd.DataFrame(np.array([playerList, guildHall, guildShop, barracks, arena, totalcontributions]).T)
            df.columns = ['Player', 'Guild Hall', 'Guild Shop', 'Barracks', 'Arena', 'Total']
            df.index += 1
            result = df.to_html(index=True, border=4, classes="table table-dark").replace('<th>', '<th class="th">')
            return render_template('guildstats.html', result=result, guildNames=guildNames)
    return render_template('guildstats.html', guildNames=guildNames)

    
if __name__ == '__main__':
    app.run()
