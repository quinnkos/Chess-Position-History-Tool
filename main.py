from __future__ import division
import pandas as pd

#imports lichess dataframe; selects relevant columns
origDf = pd.read_csv("/Users/quinnkoster/Documents/Chess Position History Tool/games.csv")
origDf = origDf[['rated', 'winner', 'white_rating', 'black_rating', 'moves']]

#stores PGN of user's current position; removes special characters and strings w/o letters
currentPosPGN = input("Enter PGN or move list: ").strip().split(' ')
currentPosMoves = []
for i in range(len(currentPosPGN)):
    if any(j.isalpha() for j in currentPosPGN[i]):
        currentPosMoves.append(''.join(x for x in currentPosPGN[i] if x.isalnum()))

#filters dataframe to only include games in the requested elo range
eloRange = input("Enter ELO range (e.g. 1600-2000) or type \"all\": ")
try:
    eloRange = eloRange.split("-")
    origDf = origDf[float(eloRange[0]) <= (origDf.white_rating+origDf.black_rating/2) <= float(eloRange[1])]
except: pass

#filters dataframe to only include rated games (if requested by user)
ratedOnly = input("Only include rated games (y/n)? ")
if ratedOnly in ["y", "ye", "yes", "yep", "yeah"]:
    origDf = origDf[origDf.rated].reset_index(drop=True)

def mainLoop(df, currentMoves):
    
    #creates new dataframe with games that reached the same position as user
    alikeGames = pd.DataFrame(columns=df.columns)
    nextMoves = []
    for game in range(len(df)):
            moveList = df.moves[game].split(' ')
            if moveList[:len(currentMoves)] == currentMoves:
                alikeGames = pd.concat([alikeGames, df[game:game+1]])
                if len(moveList) > len(currentMoves):
                    nextMoves.append(moveList[len(currentMoves)])

    #prints every next move that has occurred in the given position, the number of games in which each move occurred, and the results of the games
    def showNextMoves(moves):
        output = []
        for move in set(moves):
            sameNextMove = pd.DataFrame(columns=alikeGames.columns)
            for row in range(len(alikeGames)):
                try:
                    if alikeGames.moves.iloc[row].split(' ')[len(currentMoves)] == move:
                        sameNextMove = pd.concat([sameNextMove, alikeGames[row:row+1]])
                except: pass
            try: whiteWins = sameNextMove.winner.value_counts()['white']
            except: whiteWins = 0
            try: blackWins = sameNextMove.winner.value_counts()['black']
            except: blackWins = 0
            try: draws = sameNextMove.winner.value_counts()['draw']
            except: draws = 0
            output.append("    %s: %d (1-0: %d (%.0f%%) | 0-1: %d (%.0f%%) | ½/½: %d (%.0f%%))" %
                (move, nextMoves.count(move), whiteWins, whiteWins/nextMoves.count(move)*100, blackWins, blackWins/nextMoves.count(move)*100, draws, draws/nextMoves.count(move)*100))
        output.sort(key=lambda x: int(x.strip().split(' ')[1]), reverse=True)
        for line in output:
            print(line)

    #prints number of games that reached the same position and the results of the games
    try: whiteWins = alikeGames.winner.value_counts()['white']
    except: whiteWins = 0
    try: blackWins = alikeGames.winner.value_counts()['black']
    except: blackWins = 0
    try: draws = alikeGames.winner.value_counts()['draw']
    except: draws = 0
    print("Games that reached same position: %d (1-0: %d (%.0f%%) | 0-1: %d (%.0f%%) | ½/½: %d (%.0f%%))" %
        (len(alikeGames), whiteWins, whiteWins/len(alikeGames)*100, blackWins, blackWins/len(alikeGames)*100, draws, draws/len(alikeGames)*100))

    #calls function to print next moves and related stats;
    print("Games that continued with:")
    showNextMoves(nextMoves)

    #allows user to rerun the program with the addition of a given move to the position
    addedMove = input("Explore path (enter next move): ")
    if addedMove not in nextMoves:
        print("The path", ' '.join(currentMoves), addedMove, "is not in the database!")
        addedMove = input("Try a new move: ")
    currentMoves.append(addedMove)
    mainLoop(alikeGames.reset_index(drop=True), currentMoves)

#original call that runs the program
mainLoop(origDf, currentPosMoves)
