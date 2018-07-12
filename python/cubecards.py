from pycube256 import CubeRandom

class CubeRoulette:
    def __init__(self):
        self.wheel = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26]
        self.colors = {0:"Green",32:"Red",15:"Black",19:"Red",4:"Black",21:"Red",2:"Black",25:"Red",17:"Black",34:"Red",6:"Black",27:"Red",13:"Black",36:"Red",11:"Black",30:"Red",8:"Black",23:"Red",10:"Black",5:"Red",24:"Black",16:"Red",33:"Black",1:"Red",20:"Black",14:"Red",31:"Black",9:"Red",22:"Black",18:"Red",29:"Black",7:"Red",28:"Black",12:"Red",35:"Black",3:"Red",26:"Black"}

    def spin_wheel(self):
        pocket = CubeRandom().choice(self.wheel)
        return pocket, self.colors[pocket]

class CubeDice:
    def __init__(self, sides=6):
        self.sides = sides
        self.min = 1

    def roll(self):
        return CubeRandom().randint(self.min,self.sides)

class CubeCoins:
    def __init__(self, coins=1):
        self.sides = ['Heads','Tails']
        self.coins = coins

    def flip(self):
        return CubeRandom().choice(self.sides)

class CubeBingo:
    def __init__(self):
        self.name = "BINGO"
        self.numbers = 75
        self.pool = []
        for x in range(1,self.numbers+1):
            self.pool.append(x)

    def draw(self):
        choice = CubeRandom().choice(self.pool)
        return self.pool.pop(self.pool.index(choice))

class CubeCards:
    def __init__(self, decks=1):
        self.decks = decks
        self.cards = { 'AH':11, '2H':2, '3H':3, '4H':4, '5H':5,'6H':6, '7H':7, '8H':8, '9H':9, '10H':10, 'JH':10, 'QH':10, 'KH':10, 'AD':11, '2D':2, '3D':3, '4D':4, '5D':5,'6D':6, '7D':7, '8D':8, '9D':9, '10D':10, 'JD':10, 'QD':10, 'KD':10, 'AS':11, '2S':2, '3S':3, '4S':4, '5S':5,'6S':6, '7S':7, '8S':8, '9S':9, '10S':10, 'JS':10, 'QS':10, 'KS':10, 'AC':11, '2C':2, '3C':3, '4C':4, '5C':5,'6C':6, '7C':7, '8C':8, '9C':9, '10C':10, 'JC':10, 'QC':10, 'KC':10 }
        self.deck = []
        self.reload_deck()

    def reload_deck(self):
        for x in range(self.decks):
            for key in self.cards.keys():
                self.deck.append(key)
        self.shuffle()

    def draw(self, num=1):
        cards = []
        for x in range(num):
            if len(self.deck) == 0:
                self.reload_deck()
            cards.append(self.deck.pop(self.deck.index(CubeRandom().choice(self.deck))))
        return cards

    def shuffle(self):
        deck = []
        for x in range(len(self.deck)):
            deck.append(self.deck.pop(self.deck.index(CubeRandom().choice(self.deck))))
        self.deck = list(deck)

#game = CubeRoulette()
#print game.spin_wheel()
#dice = CubeDice()
#print dice.roll()
#print CubeCoins().flip()
#bingo = CubeBingo()
#for x in range(75):
#    print bingo.draw()
deck = CubeCards()
for x in range(52):
    print deck.draw()
for x in range(52):
    print deck.draw()
