import json
#pokerkit imports
from pokerkit import (
     Automation,
     FixedLimitDeuceToSevenLowballTripleDraw,
     NoLimitTexasHoldem,
)
#bots, these are templates right now but will be updated with submissions
from Players.TemplateBot1 import bot as bot1
from Players.TemplateBot2 import bot as bot2
players = [bot1, bot2]

#premade game class from pokerkit
game = NoLimitTexasHoldem(
    # automations
    automations = (
    Automation.ANTE_POSTING,
    Automation.BET_COLLECTION,
    Automation.BLIND_OR_STRADDLE_POSTING,
    Automation.CARD_BURNING,
    Automation.HOLE_DEALING,
    Automation.BOARD_DEALING,
    Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
    Automation.HAND_KILLING,
    Automation.CHIPS_PUSHING,
    Automation.CHIPS_PULLING,
    ),
    ante_trimming_status=True,  # False for big blind ante, True otherwise
    raw_antes=0,  # ante
    raw_blinds_or_straddles=(25, 50),  # blinds small 25, large 50
    min_bet=25,  # min first bet/raise amount
)
state = game(
    1000,  # starting stacks(money)
    2,  # number of players
)

#returns an updated dict with all game data
def updateData():
    data = {
    "TemplateBot1":
    {
        "Money": state.stacks[0],
        "Bet": state.bets[0],
        "Playing": state.statuses[0],
    },
    "TemplateBot2":
    {
        "Money": state.stacks[1],
        "Bet": state.bets[1],
        "Playing": state.statuses[1]
    },
    "Cards": [str(i) for i in tuple(state.cards_in_play)],
    "Pot": state.total_pot_amount,
    "Min": state.min_completion_betting_or_raising_to_amount,
    "Size": state.player_count
    }
    return data

#returns whether or not there is a winner in the current game
def checkWin():
    lost = 0
    for i in range(0,state.player_count):
        if state.stacks[i] == 0 and state.bets[i] == 0:
            lost += 1
    return lost >= state.player_count - 1

#parses the return value from the current players getAction method
def parseBotAction():
    bot_index = state.actor_index
    #this is the only point where getAction is called
    response = players[bot_index].getAction(state.hole_cards[bot_index], state.can_fold)
    if response == 0:
        state.check_or_call()
    elif response < 0:
        try:
            state.fold()
        except:
            state.check_or_call
    elif response >= 0:
        try:
            state.complete_bet_or_raise_to(response)
        except:
            try:
                state.fold()
            except:
                state.check_or_call()

#main

#runs until someone has won
while(not checkWin()):
    #uploads data to data.json
    data = updateData()
    with open("data.json", "w") as file:
        json.dump(data,file)
    #runs bot script
    if(state.total_pot_amount != 0):
        parseBotAction()
    #pot will always be > 0 due to blinds, unless the round has ended and the pot has been distributed
    else:
        state = game(
        state.stacks,  # starting stacks
        2,  # number of players
    )

data = updateData()
#uploads data to data.json, this doesn't do anything functionally but may be useful for debugging
with open("data.json", "w") as file:
    json.dump(data,file)
print(data)
#hole cards are the cards the player has
print(state.hole_cards)
print(tuple(state.cards_in_play))