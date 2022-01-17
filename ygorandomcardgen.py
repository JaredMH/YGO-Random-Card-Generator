import urllib.request
import random
import requests
import time

# A list of Extra Deck types, used for identifying if a card belongs in the Extra Deck later.
edtypes = ["Fusion Monster", "Link Monster", "Pendulum Effect Fusion Monster", "Synchro Monster", "Synchro Pendulum Effect Monster", "Synchro Tuner Monster","XYZ Monster", "XYZ Pendulum Effect Monster"]

# Returns a random card in the format [ID number, Name, database url, Main Deck card or not]
def getrandcard():
    # These are the current minimum and maximum Konami ID numbers (that I can find) as of Brothers of Legend
    # This is Konami's internal ID that the database uses, and is not on the physical cards.
    cardnum = random.randint(4007, 16636)
    cardurl = 'https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=' + str(cardnum)
    data = urllib.request.urlopen(cardurl)
    
    # Get the name of the card.
    cardname = ""
    for line in data:
        if '<title>' in str(line):
            cardname = line[9:-71].decode('UTF-8')
            break
    # Not all numbers are assigned, so try again if you get a bad one.
    if cardname == '':
        return getrandcard()
    
    id = getcardidfromname(cardname)
    
    return [id[0], cardname, cardurl, id[1]]

# Returns the ID number and whether it's an extra deck card from a card's name.
# This is the number in the corner of the card, and ygoprodeck uses it.
def getcardidfromname(cardname):
    ygopdapiurl = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    query = {'name': cardname}
    r = requests.get(ygopdapiurl, params = query)
    time.sleep(.1)  # Make sure we don't flood the API with requests. They have a 20 requests/second limit, so this should be safe.
    
    maindeck = True
    if r.json()['data'][0]['type'] in edtypes:
        maindeck = False
    return [r.json()['data'][0]['id'], maindeck]

def main():
    # Ask for number of cards to generate.
    numcardstoget = 'none'
    while not numcardstoget.isdigit():
        numcardstoget = input('Enter number of cards to get: ')
    
    maindeck = "#main\n"
    extradeck = "#extra\n"
    
    # Keep track of which cards we've grabbed
    cardids = []
    
    for i in range(int(numcardstoget)):
        card = getrandcard()
        # Make sure it's not a duplicate
        while card[0] in cardids:
            card = getrandcard()
        cardids.append(card[0])
        
        print (card[1] + '\t\t' + card[2])
        if card[3]:
            maindeck += str(card[0]) + '\n'
        else:
            extradeck += str(card[0]) + '\n'
            
    
    # Build a .ydk file for EDOPro or YGOPRODeck.
    ydk = maindeck + '\n' + extradeck + '\n' + '!side\n'
    with open('CardList.ydk', 'w') as file:
        file.write(ydk)

if __name__ == "__main__":
    main()
