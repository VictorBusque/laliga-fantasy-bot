
from typing import List, Tuple
from Levenshtein import distance
from itertools import combinations
from unidecode import unidecode

class Utils:
    @staticmethod
    def distance(word1, word2):
        word1 = unidecode(word1)
        word2 = unidecode(word2)
        max_score = 0
        if not word2: return max_score
        word2_split = word2.split(' ')
        len1 = len(word1.split(' '))
        len2 = len(word2_split)
        if len1 > len2: 
            return 0
        for word in combinations(word2_split, len1):
            word = ' '.join(word)
            dist = distance(word1, word)
            score = 1 - dist/max(len(word), len(word1))
            max_score = max(max_score, score)
        return max_score
    
    @staticmethod
    def find_closest_n(search: str, list_to_match: List[Tuple[str, str]], n: int=1, min_sim: float=0.7) -> List[str]:

        item_distances = [(_id, name, Utils.distance(search, name))
                            for (_id, name) in list_to_match]
        item_distances.sort(key=lambda x: x[2], reverse=True)
        print(item_distances)
        return [_id for _id, _, dist in item_distances[:n] if dist >= min_sim]