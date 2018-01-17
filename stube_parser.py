import requests
auth = ('user', 'password')
import re
import random
import time
import sys
import pickle
import json
import progressbar
from multiprocessing.dummy import Pool as ThreadPool

card_map = {
    'S7': 'Karo-7',
    'S8': 'Karo-8',
    'S9': 'Karo-9',
    'SX': 'Karo-10',
    'SU': 'Karo-Bube',
    'SO': 'Karo-Dame',
    'SK': 'Karo-Koenig',
    'SA': 'Karo-Ass',
    'H7': 'Herz-7',
    'H8': 'Herz-8',
    'H9': 'Herz-9',
    'HX': 'Herz-10',
    'HU': 'Herz-Bube',
    'HO': 'Herz-Dame',
    'HK': 'Herz-Koenig',
    'HA': 'Herz-Ass',
    'G7': 'Pik-7',
    'G8': 'Pik-8',
    'G9': 'Pik-9',
    'GX': 'Pik-10',
    'GU': 'Pik-Bube',
    'GO': 'Pik-Dame',
    'GK': 'Pik-Koenig',
    'GA': 'Pik-Ass',
    'E7': 'Kreuz-7',
    'E8': 'Kreuz-8',
    'E9': 'Kreuz-9',
    'EX': 'Kreuz-10',
    'EU': 'Kreuz-Bube',
    'EO': 'Kreuz-Dame',
    'EK': 'Kreuz-Koenig',
    'EA': 'Kreuz-Ass',
}

class Game(object):
    player = False
    cards = None
    distributions = None
    game_id = None
    game_type = None

    def addCards(self, card):
        if self.cards is None:
            self.cards = []
        self.cards.append(card)

    def setId(self, id):
        self.game_id = id

    def setType(self, game_type):
        self.game_type = game_type

    def setPlayer(player):
        self.player = player

    def calc_distribution(self):
        if self.distributions is not None:
            return self.distributions
        self.distributions = []
        for player_cards in self.cards:
            distr = {}
            for card in player_cards:
                distr[card[1:2]] = distr.get(card[1:2], 0) + 1
            self.distributions.append(distr)
        return self.distributions

def get_game(id):
    while(True):
        try:
            r = requests.get('https://www.skatstube.de/spiele/'+str(id), auth=auth)
        except requests.exceptions.ConnectionError:
            continue
        if r.status_code == 200:
            break
        time.sleep(random.randint(1, 4))
    match = re.findall(r'<span class="card-image fr g3 .{1,2}"', r.text)
    game_type = re.findall(r'<h1>.*von', r.text)
    if len(game_type) > 0:
        game_type = game_type[0][4:-4]
    else:
        game_type = 'dummy'
    first = match[30][-3:-1]
    second = match[31][-3:-1]
    game = Game()
    game.addCards([x[-3:-1] for x in match[0:10]])
    game.addCards([x[-3:-1] for x in match[10:20]])
    game.addCards([x[-3:-1] for x in match[20:30]])
    game.addCards([x[-3:-1] for x in match[30:32]])
    game.setId(id)
    game.setType(game_type)
    return game

args = sys.argv
if len(args) != 3:
    print("usage: python stube_parses.py startid endid")
    sys.exit(0)
try:
    start = int(args[1])
    end = int(args[2])
except ValueError:
    print("usage: python stube_parses.py startid endid")
    sys.exit(0)
r = requests.get('https://www.skatstube.de/spiele/'+str(start), auth=auth)
if r.status_code != 200:
    print("invalid start id")
    sys.exit(0)
r = requests.get('https://www.skatstube.de/spiele/'+str(end), auth=auth)
if r.status_code != 200:
    print("invalid end id")
    sys.exit(0)

to_calc = range(start, end+1)
games = []
result = {}
pool = ThreadPool(64)
games = pool.map(get_game, to_calc)
pool.close()
pool.join()

for x in games:
    result[x.game_id] = [x.game_type] + x.cards

with open("skatstube_"+str(start)+"_to_"+str(end)+".json","wb") as handle:
    json.dump(result, handle)
