import random
from enum import Enum
import pandas as pd
import matplot
import matplotlib

# Object Oriented approach to AxisAllies calculator

class pieces(Enum):
    infantry = 1
    artillery = 2
    combinedInfantry = 3
    tank = 4
    fighter = 5
    bomber = 6
    submarine = 7
    destroyer = 8
    battleShipHit1 = 9
    battleShipHit2 = 10
    aircraftCarrier = 11
    antiAircraft = 12
    cruiser = 13
    battleShip = 14

class battleType(Enum):
    land = 1
    sea = 2
    amphibious = 3
    air = 4

class CombatantType(Enum):
    attacker = 1
    defender = 2


ipcVals = {pieces.infantry: 3}


#landDefenseProfile = [pieces.infantry, pieces.combinedInfantry, pieces.artillery, pieces.tank, pieces.fighter]
#seaDefenseProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.fighter, pieces.aircraftCarrier, pieces.battleShipHit2]
#subHitsProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.aircraftCarrier, pieces.battleShipHit2]


class Combatant(object):

    landDefenseProfile = [pieces.infantry, pieces.combinedInfantry, pieces.artillery, pieces.tank, \
        pieces.fighter, pieces.bomber, pieces.antiAircraft]
    airDefenseProfile = [pieces.fighter, pieces.bomber]
    subHitsProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.aircraftCarrier, \
        pieces.battleShipHit2]
    seaDefenseProfile = [pieces.battleShipHit1, pieces.submarine, pieces.destroyer, pieces.cruiser, pieces.fighter, \
        pieces.aircraftCarrier, pieces.battleShipHit2]

    def __init__(self, units):
        self.__pieces = dict.fromkeys(pieces, 0)
        for key in units.keys():
            self.__pieces[key] = units[key]

    def addCombatant(self, piece, numPieces):
        if (piece == pieces.battleShip):
            self.__pieces[pieces.battleShipHit1] += numPieces
            self.__pieces[pieces.battleShipHit2] += numPieces
            self.__pieces[piece] += numPieces
        else:
            self.__pieces[piece] += numPieces

    # Return remaining hits 
    def removeCombatant(self, piece, numPieces):
        remainingHits = 0
        if (self.pieces[piece] >= numPieces):
            self.pieces[piece] -= numPieces
            if (piece == pieces.battleShipHit2):
                #Remove equivalent number of battleships
                self.pieces[pieces.battleShip] -= numPieces
            remainingHits = 0
        elif (self.pieces[piece] < numPieces):
            numPieces -= self.pieces[piece]
            self.pieces[piece] = 0
            if (piece == pieces.battleShipHit2):
                #Remove all battleships
                self.pieces[pieces.battleShip] = 0
            remainingHits = numPieces

        return remainingHits

    def getNumCombatants(self, piece):
        return self.pieces[piece]

    def remainingCombatants(self):
        return (sum(self.pieces.values()) > 0)

    def __determineHitsByPiece(self, numRolls, attackVal):
        hits = 0
        for x in range(numRolls):
            randVal = random.randint(1,6)
            print ("RandVal = {0}, attackVal = {1}".format(randVal, attackVal))
            if (randVal <= attackVal):
                hits += 1
        return hits

    def __determineHits(self, attackVals, includeSubs):
        hits = dict.fromkeys(pieces, 0)
        for piece in pieces:
            if (piece != pieces.antiAircraft and (piece != pieces.submarine or includeSubs)):
                hits[piece] = self.__determineHitsByPiece(self.__pieces[piece], attackVals[piece])
        return(hits)

    def getPieces(self):
        return self.__pieces

    pieces = property(getPieces)

    def assignHits(self, hits, typeOfBattle):
        numHits = sum(hits.values())
        if (typeOfBattle == battleType.land):
            print ("Land Battle")
            # Anything hits anything with one special case...anti-aircraft are second to last hit          
            if(sum(self.__pieces.values()) - numHits == 1):
                numHits = self.removeCombatant(pieces.antiAircraft, 1)
            for piece in self.landDefenseProfile:
                numHits = self.removeCombatant(piece, numHits)
                if ( numHits == 0):
                    break
        elif (typeOfBattle == battleType.air):
            for piece in self.airDefenseProfile:
                if (self.removeCombatant(piece, hits[pieces.antiAircraft]) == 0):
                    break
        elif (typeOfBattle == battleType.sea):
            # Do sub hits first
            if (hits[pieces.submarine] > 0):
                for piece in self.subHitsProfile:
                    numHits = self.removeCombatant(piece, numHits)
                    if (numHits == 0):
                        break
            for piece in self.seaDefenseProfile:
                numHits = self.removeCombatant(piece, numHits)
                if (numHits == 0):
                    break

    def hasUnits(self, unit):
        return (self.pieces[unit] > 0)

    def sneakAttack(self, defender, attackVal):
        hits = dict.fromkeys(pieces, 0)
        #subs get a sneak attack if opponent does not have a destroyer
        numRolls = self.pieces[pieces.submarine]
        if (numRolls > 0 and not defender.hasUnits(pieces.destroyer)):
            print("Submarine Sneak Attacks: {0}".format(numRolls))
            hits[pieces.submarine] = self._Combatant__determineHitsByPiece(numRolls, attackVal)

            if (hits[pieces.submarine] > 0):
                defender.assignHits(hits, battleType.sea)

            return True
        else:
            return False

    def __str__(self):
        print(self.pieces)
        return ""

class Attacker(Combatant):

    attackVals = {pieces.infantry: 1, pieces.artillery: 2, pieces.combinedInfantry: 2, pieces.tank: 3,\
       pieces.fighter: 3, pieces.bomber: 4, pieces.submarine: 2, pieces.destroyer: 2, pieces.cruiser: 3, \
       pieces.battleShipHit1: 0, pieces.battleShipHit2: 0, pieces.battleShip: 4, pieces.aircraftCarrier: 1, pieces.antiAircraft: 0}

    ipcVals = {pieces.infantry: 3}
    #def __init__(self):
    #    super().__init__()

    #only happens with attackers, during the attack phase
    def __combineInfantry(self):
        #if we have infantry and artillery, the infantry attack better. create combined units
        if (self.pieces[pieces.infantry] > 0 and self.pieces[pieces.artillery] > 0):
            if (self.pieces[pieces.artillery] >= self.pieces[pieces.infantry]):
                self.pieces[pieces.artillery] -= self.pieces[pieces.infantry]
                self.pieces[pieces.combinedInfantry] = self.pieces[pieces.infantry] * 2
                self.pieces[pieces.infantry] = 0
            elif (self.pieces[pieces.infantry] > self.pieces[pieces.artillery]):
                self.pieces[pieces.infantry] -= self.pieces[pieces.artillery]
                self.pieces[pieces.combinedInfantry] = self.pieces[pieces.artillery] * 2
                self.pieces[pieces.artillery] = 0

    #break the infantry and artillery back out for hit assignment
    def __uncombineInfantry(self):
        if (self.pieces[pieces.combinedInfantry] > 0):
            self.pieces[pieces.infantry] += self.pieces[pieces.combinedInfantry] // 2
            self.pieces[pieces.artillery] += self.pieces[pieces.combinedInfantry] // 2
            self.pieces[pieces.combinedInfantry] = 0

    # Do all the attack logic
    def attack(self, battle, includeSubs):     
        self.__combineInfantry()
        return (super()._Combatant__determineHits(self.attackVals, includeSubs))

    def assignHits(self, hits, typeOfBattle):
        self.__uncombineInfantry()
        # For a land battle, anything can hit anything
        super().assignHits(hits, typeOfBattle)

class Defender(Combatant):

    defenseVals = {pieces.infantry: 2, pieces.artillery: 2, pieces.combinedInfantry: 2, pieces.tank: 3,\
        pieces.fighter: 4, pieces.bomber: 1, pieces.submarine: 1, pieces.destroyer: 2, pieces.cruiser: 3, \
        pieces.battleShipHit1: 0, pieces.battleShipHit2: 0, pieces.battleShip: 4, pieces.aircraftCarrier:2, pieces.antiAircraft: 1}

    def antiAirAttack(self, attacker):
        hits = dict.fromkeys(pieces, 0)
        #anti-aircraft batteries get one attack at the beginning and up to 3 per unit
        numRolls = max((attacker.pieces[pieces.fighter] + attacker.pieces[pieces.bomber]), (self.pieces[pieces.antiAircraft]*3))
        print("Anti-Aircraft Attacks: {0}".format(numRolls))
        hits[pieces.antiAircraft] = self._Combatant__determineHitsByPiece(numRolls, self.defenseVals[pieces.antiAircraft])

        if (hits[pieces.antiAircraft] > 0):
            attacker.assignHits(hits, battleType.air)
        
    # Do all the attack logic
    def attack(self, battle, includeSubs):
        return (super()._Combatant__determineHits(self.defenseVals, includeSubs))

    def assignHits(self, hits, typeOfBattle):
        super().assignHits(hits, typeOfBattle)


# create a game piece



battle = battleType.land

random.seed(100)





winLossPercentage  = 0.0
drawPercentage = 0.0
monteCarloRuns = 100
finalResults = list()
# Do battle
for x in range(monteCarloRuns):
    print('Create an Attacker')

    attackerUnits = {pieces.infantry: 8, pieces.artillery: 2}
    attacker = Attacker(attackerUnits)


    print('Create a Defender')
    defenderUnits = {pieces.infantry: 8}
    defender = Defender(defenderUnits)

    attackerUnits = attacker.pieces.copy()
    defenderUnits = defender.pieces.copy()
    resultsOfRound = [{'attacker':attackerUnits,'defender':defenderUnits}]
    results = list()

    #results.append(resultsOfRound)
    # a couple special cases have to be handled above the attacker/defender
    if (defender.hasUnits(pieces.antiAircraft) and \
    (attacker.hasUnits(pieces.fighter) or attacker.hasUnits(pieces.bomber))):
        defender.antiAirAttack(attacker)
    round = 0
    while (attacker.remainingCombatants() and defender.remainingCombatants()):
        print("Round: {0}".format(round))
        attackerSneakAttack = attacker.sneakAttack(defender, attacker.attackVals[pieces.submarine])
        defenderSneakAttack = defender.sneakAttack(attacker, defender.defenseVals[pieces.submarine])
        attackerHits = attacker.attack(battle, not attackerSneakAttack)
        defenderHits = defender.attack(battle, not defenderSneakAttack)
        defender.assignHits(attackerHits, battle)
        attacker.assignHits(defenderHits, battle)
        print(attacker.pieces.values())
        results.append(attacker.pieces.copy())
#        results.append( [{'attacker:':attacker.pieces.copy(), 'defender': defender.pieces.copy()} ])
        round += 1

    finalResults.append(results[round-1])
    if (attacker.remainingCombatants()):
        print("Attacker Wins\n")
        winLossPercentage += 1.0
    elif (not attacker.remainingCombatants() and not defender.remainingCombatants()):
        drawPercentage += 1.0
    else:
        print("Defender Wins\n")

print("Total Attacker Win %: {0}".format((winLossPercentage/monteCarloRuns)*100))
print("Total Draw %: {0}".format((drawPercentage/monteCarloRuns)*100))
#print(results[0])

#print(resultsOfRound[0]['attacker'])
print(results)

tempUnits = dict.fromkeys(pieces, [])
tempUnits[pieces.infantry] = [2,1,1]
tempUnits[pieces.artillery] = [2,2,2]
pd.DataFrame()

df = pd.DataFrame(finalResults)
#df = df.transpose()
#df = pd.DataFrame.from_dict(tempUnits, orient = 'index')
print(df)
print(df.mean())
print(df.describe())
#df = df.mean()
#df = df.transpose()
from matplotlib.colors import ListedColormap

cmap = ListedColormap(['#0343df', '#e50000', '#ffff14', '#929591'])

#df.plot.bar()

#df.hist()
df.hist(column=pieces.infantry, bins=16)

#ax = resultsOfRound[0]['attacker'].values()
#ax = df.plot.bar(x='attacker', colormap=cmap)

#ax.set_xlabel(None)
#ax.set_ylabel('Seats')
#ax.set_title('UK election results')

import matplotlib.pyplot as plt
plt.show()





