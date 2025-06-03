import random
from typing import List, Tuple
from states import State

class Game:
    __picks = ('\U0001F534', '\U000026AA', '\U0001F535', '\U0001F338', '\U0001F7E0', '\U0001F7E3', '\U0001F7E1', '\U0001F7E2')

    def get_tries(self) -> int:
        return self.__tries
    
    def get_solution(self) -> List[int]:
        return self.__solution

    def __init__(self) -> None:
        self.__tries = 11
        self.__exp = 0
        self.__solution = [''] * 4
        for i in range(4):
            self.__solution[i] = random.choice(self.__picks)

    def evaluate(self, guess: List[str]) -> Tuple[List[str], List[str], State]:
        guessE = self.__str_to_emoji(guess)
        resultE = sorted(self.__calc_result(guessE), key = self.__sort_key)
        won = True
        for i in range(4):
            if resultE[i] != '\U000026AB':
                won = False
                break
        if won == True:
            return resultE, self.__solution, State.WON
        self.__tries -= 1
        if self.__tries == 0:
            return resultE, self.__solution, State.GAME_OVER
        return resultE, guessE, State.WRONG_GUESS

    def __str_to_emoji(self, list: List[str]) -> List[str]:
        emoji = []
        for s in list:
            match s:
                case 'Red':
                    emoji.append('\U0001F534')
                case 'White':
                    emoji.append('\U000026AA')
                case 'Blue':
                    emoji.append('\U0001F535')
                case 'Pink':
                    emoji.append('\U0001F338')
                case 'Orange':
                    emoji.append('\U0001F7E0')
                case 'Purple':
                    emoji.append('\U0001F7E3')
                case 'Yellow':
                    emoji.append('\U0001F7E1')
                case 'Green':
                    emoji.append('\U0001F7E2')
        return emoji
    
    def __calc_result(self, guess: List[str]) -> List[str]:
        result = []
        remsolution = []
        remGuess = []
        for i in range(4):
            if self.__solution[i] == guess[i]:
                result.append('\U000026AB')
                self.__exp += 3
            else:
                remsolution.append(self.__solution[i])
                remGuess.append(guess[i])
        for g in remGuess:
            if g in remsolution:
                result.append('\U000026AA')
                remsolution.remove(g)
                self.__exp += 2
            else:
                result.append('\U0000274C')
        return result
    
    def __sort_key(self, s) -> int:
        if s == '\U000026AB':
            return 0
        elif s == '\U000026AA':
            return 1
        else:
            return 2
        
    def return_exp(self) -> int:
        return (self.__tries * 10) + self.__exp
