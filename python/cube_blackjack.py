from pycube256 import CubeRandom

class CubeBlackJack:
    def __init__(self, decks=1):
        self.decks = decks
        self.cards = { 'AH':11, '2H':2, '3H':3, '4H':4, '5H':5,'6H':6, '7H':7, '8H':8, '9H':9, '10H':10, 'JH':10, 'QH':10, 'KH':10, 'AD':11, '2D':2, '3D':3, '4D':4, '5D':5,'6D':6, '7D':7, '8D':8, '9D':9, '10D':10, 'JD':10, 'QD':10, 'KD':10, 'AS':11, '2S':2, '3S':3, '4S':4, '5S':5,'6S':6, '7S':7, '8S':8, '9S':9, '10S':10, 'JS':10, 'QS':10, 'KS':10, 'AC':11, '2C':2, '3C':3, '4C':4, '5C':5,'6C':6, '7C':7, '8C':8, '9C':9, '10C':10, 'JC':10, 'QC':10, 'KC':10 }
        self.deck = []
        for x in range(decks):
            for key in self.cards.keys():
                self.deck.append(key)
        self.shuffle_deck()
        self.discard_deck = []
        self.player1_name = ""
        self.player1_score = 0
        self.player2_score = 0
        self.double_bust = 0
        self.draw_count = 0
        self.dealers_history = []
        self.dealers_last_choice = 0
        self.dealers_average = 0
        self.dealers_count = 0
        self.pot = 0
        self.table_min = 5
        self.player1_bet = self.table_min
        self.player2_bet = self.table_min
        self.player1_purse = 0
        self.player2_purse = 0

    def shuffle_deck(self, times=1):
        for x in range(0,times):
            self.deck = CubeRandom().shuffle(self.deck)

    def deal_hand(self):
        p1_hand = {}
        p2_hand = {}
        p1_cards = []
        p2_cards = []
        p1_value = 0
        p2_value = 0
        if len(self.deck) > 4:
            for card in range(0,2):
                p1 = self.deck.pop(0)
                p1_value += self.cards[p1]
                p2 = self.deck.pop(0)
                p2_value += self.cards[p2]
                p1_cards.append(p1)
                p2_cards.append(p2)
                self.discard_deck.append(p1)
                self.discard_deck.append(p2)
            p1_hand = { "value":p1_value, "cards":p1_cards }
            p2_hand = { "value":p2_value, "cards":p2_cards }
        else:
            #self.deck = []
            for card in range(len(self.discard_deck)):
                self.deck.append(self.discard_deck.pop(0))
            #self.deck = list(self.discard_deck)
            self.discard_deck = []
            self.shuffle_deck()
            self.dealers_count = 0
            for card in range(0,2):
                p1 = self.deck.pop(0)
                p1_value += self.cards[p1]
                p2 = self.deck.pop(0)
                p2_value += self.cards[p2]
                p1_cards.append(p1)
                p2_cards.append(p2)
                self.discard_deck.append(p1)
                self.discard_deck.append(p2)
            p1_hand = { "value":p1_value, "cards":p1_cards }
            p2_hand = { "value":p2_value, "cards":p2_cards }
        return p1_hand, p2_hand

    def draw_card(self, hand):
        if len(self.deck) > 0 and len(self.deck) <= 52:
            card = self.deck.pop(0)
            hand["cards"].append(card)
            if "A" in card and hand["value"] >= 11:
                hand["value"] = (hand["value"] + self.cards[card]) - 10
            else:
                hand["value"] = hand["value"] + self.cards[card]
            self.discard_deck.append(card)
        elif len(self.deck) == 0:
            #self.deck = []
            for card in range(len(self.discard_deck)):
                self.deck.append(self.discard_deck.pop(0))
            #self.deck = list(self.discard_deck)
            self.discard_deck = []
            self.shuffle_deck()
            self.dealers_count = 0
            card = self.deck.pop(0)
            hand["cards"].append(card)
            if "A" in card and hand["value"] >= 11:
                hand["value"] = (hand["value"] + self.cards[card]) - 10
            else:
                hand["value"] = hand["value"] + self.cards[card]
            self.discard_deck.append(card)
        else:
            print len(self.deck)
            print self.deck
            #exit(0)
        return hand

    def set_player_name(self, name):
        self.player1_name = name

    def game(self, test=False, name=None):
        if name != None:
            self.player1_name = name
        hand_num = 0
        while True:
            hand_num += 1
            print "*** Hand Number ", hand_num
            winner = None
            p1_hand, p2_hand = self.deal_hand()
            print "New hand (player1): ", p1_hand, "New Hand (CPU player) ", p2_hand
            print p1_hand["cards"], p2_hand["cards"]
            if test == False:
                action = raw_input("Enter action(hit/stand)?")
            else:
                action = "stand"
                if p1_hand["value"] <= 17:
                    action = "hit"
                    self.pot += self.player1_bet
            self.dealer_count(p1_hand["cards"], p2_hand["cards"])
            if self.dealers_choice(p2_hand["value"]) == "hit":
                p2_hand = self.draw_card(p2_hand)
            if action == "hit":
                p1_hand = self.draw_card(p1_hand)
            if action == "quit":
                exit(0)
            if p1_hand["value"] > p2_hand["value"] and p1_hand["value"] <= 21:
                winner = "p1"
                if p1_hand["value"] > 21:
                    winner = None
            if p2_hand["value"] > p1_hand["value"] and p2_hand["value"] <= 21:
                winner = "p2"
                if p2_hand["value"] > 21:
                    winner = None
                else:
                    self.dealer_learn(p2_hand["value"])
            busted = []
            if winner == None:
                if p1_hand["value"] == p2_hand["value"]:
                    winner = "Draw"
                if p1_hand["value"] > 21:
                    busted.append("p1")
                if p2_hand["value"] > 21:
                    busted.append("p2")
            if len(busted) == 1:
                if "p1" in busted and "p2" not in busted:
                    winner = "p2"
                else:
                    winner = "p1"
            if winner == "p1":
                self.player1_score += 1
                self.player1_purse += self.pot
                self.pot = 0
            elif winner == "p2":
                self.player2_score += 1
                self.player2_purse += self.pot
                self.pot = 0
            elif winner == "Draw":
                self.draw_count += 1
            if len(busted) == 2:
                self.double_bust += 1
            #self.dealer_count(p1_hand["cards"], p2_hand["cards"])
            print "Score: Player1 ", self.player1_score, " Player 2 ", self.player2_score, " Draws ", self.draw_count, "Double busts ", self.double_bust
            print self.player1_name, self.player1_score, " points - CPU Player ", self.player2_score, " points"
            print "Winnings: ", self.player1_purse, self.player2_purse
            print "End hand ", self.player1_name, " ", p1_hand, "End hand (CPU player) ", p2_hand
            print "Winner winner chicken dinner!! ", winner, "\n"
            if len(self.deck) > 52:
                print "!!! Alert !!!"
                print len(self.deck)
                print self.deck
                #exit(0)
            print self.deck
    
    def dealers_choice(self, value):
        #choices = [10, 11, 12, 13, 14, 15, 16, 17 ]
        #choices = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 ]
        choices = [ 12, 13, 14 ]
        #choices = [ 12, 13 ]
        choice = "stand"
        min = 12
        if len(self.dealers_history) >= 500:
            min = self.dealers_average - 1
            max = self.dealers_average + 1
            print "Setting MIN MAX to ", min, max
        else:
            max = 14
        dealers_choice = CubeRandom().choice(choices)
        self.dealers_last_choice = dealers_choice
        #print "Dealers history", self.dealers_history
        print "Dealers average", self.dealers_average
        if value < 21 and value <= dealers_choice:
            choice = "hit"
        if value < 21 and self.true_count >= 1:
        #if value <= 17 and (self.true_count >= 1 or self.dealers_count >=1):
            choice = "hit"
            self.pot += 5
        return choice

    def dealer_learn(self, winning_value):
        total = 0
        self.dealers_history.append(self.dealers_last_choice)
        if len(self.dealers_history) > 2:
            for value in self.dealers_history:
                total += value
            self.dealers_average = total / len(self.dealers_history)

    def dealer_count(self, p1_cards, p2_cards):
        for card in p1_cards:
            self.count_value(card)
        for card in p2_cards:
            self.count_value(card)
        print "Dealers count ", self.dealers_count
   
    def count_value(self, card):
        cvalue = self.cards[card]
        if cvalue >= 2 and cvalue <= 6:
            self.dealers_count += 1
        elif cvalue >= 7 and cvalue <= 9:
            pass
        elif cvalue >= 10:
            self.dealers_count -= 1
        self.true_count = self.dealers_count / (self.decks * 52) / len(self.deck) 

game = CubeBlackJack(decks=1)
#game.game()
game.game(test=True, name="Karl")
