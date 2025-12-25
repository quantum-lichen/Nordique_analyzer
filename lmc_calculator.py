"""
Nordique LMC - Calculs de Complexité Minimale (LMC)
Basé sur la théorie CEML: J(s) = C(s|Ω) / (H(s) + ε)
"""

import re
import math
from typing import List, Dict, Set
from collections import Counter


class LMCCalculator:
    """
    Calculateur de scores LMC (Least Model Complexity)
    Implémente CEML: Cohérence / (Entropie + epsilon)
    """
    
    def __init__(self, epsilon: float = 0.001):
        """
        Initialise le calculateur LMC
        
        Args:
            epsilon: Constante de régularisation (défaut: 0.001)
        """
        self.epsilon = epsilon
        self.stopwords = {
            'cette', 'comme', 'dans', 'pour', 'avec', 'sont', 'leurs', 'plus', 'peut',
            'être', 'fait', 'permet', 'avoir', 'faire', 'entre', 'donc', 'aussi', 'ainsi',
            'selon', 'toute', 'tous', 'était', 'serait', 'pourrait', 'existe', 'autres',
            'chaque', 'peuvent', 'encore', 'toujours', 'quelque', 'certains', 'plusieurs'
        }
    
    def calculate_entropy(self, text: str) -> float:
        """
        Calcule l'entropie de Shannon du texte
        H = -Σ p(x) log₂ p(x)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Entropie normalisée [0-1]
        """
        if not text or len(text) < 50:
            return 0.0
        
        # Extraire mots (3+ lettres, avec accents français)
        words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{3,}\b', text.lower())
        
        if not words:
            return 0.0
        
        # Calculer fréquences
        freq = Counter(words)
        total = len(words)
        
        # Entropie de Shannon
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normaliser (max ~10 pour texte naturel)
        return min(entropy / 10.0, 1.0)
    
    def calculate_coherence(self, text: str) -> float:
        """
        Calcule la cohérence contextuelle
        C = f(répétition, longueur, contenu, négations)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Cohérence [0-1]
        """
        if not text or len(text) < 50:
            return 0.0
        
        # Phrases
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if len(s) > 20]
        if len(sentences) < 2:
            return 0.5
        
        # Mots (4+ lettres)
        words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', text.lower())
        unique_words = set(words)
        
        # 1. Taux de répétition
        repetition_rate = 1.0 - (len(unique_words) / max(len(words), 1))
        
        # 2. Cohérence de longueur
        avg_sentence_length = len(words) / len(sentences)
        length_coherence = min(avg_sentence_length / 20.0, 1.0)
        
        # 3. Ratio de mots de contenu
        content_words = [w for w in words if w not in self.stopwords]
        content_ratio = len(content_words) / max(len(words), 1)
        
        # 4. Bonus de complexité (négations)
        negations = re.findall(
            r"n'est pas|ne sont pas|n'a pas|ne peut pas|jamais|aucun",
            text.lower()
        )
        negation_bonus = min(len(negations) / 10.0, 0.1)
        
        # Combinaison pondérée
        coherence = (
            repetition_rate * 0.25 +
            length_coherence * 0.35 +
            content_ratio * 0.30 +
            negation_bonus * 0.10
        )
        
        return coherence
    
    def calculate_lmc_score(self, text: str) -> Dict[str, float]:
        """
        Calcule le score LMC complet
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict avec H (entropie), C (cohérence), score LMC
        """
        H = self.calculate_entropy(text)
        C = self.calculate_coherence(text)
        
        # Score LMC: C / (H + ε)
        score = C / (H + self.epsilon)
        
        return {
            'H': H,
            'C': C,
            'score': score
        }
    
    def split_sentences(self, text: str) -> List[str]:
        """Divise le texte en phrases valides"""
        if not text:
            return []
        
        sentences = re.split(r'[.!?]\s+|\n{2,}', text)
        return [s.strip() for s in sentences if 20 < len(s) < 500]
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extrait les affirmations clés du texte
        
        Args:
            text: Texte source
            
        Returns:
            Liste des affirmations (max 20)
        """
        if not text or len(text) < 100:
            return []
        
        # Marqueurs d'affirmations
        markers = [
            'est ', 'sont ', 'représente', 'correspond', 'signifie', 'implique',
            'démontre', 'prouve', 'permet', 'cause', 'entraîne', 'résulte',
            'montre', 'indique', 'suggère', 'confirme', 'révèle', 'favorise',
            'aide', 'améliore', 'réduit', 'augmente', 'consiste'
        ]
        
        negations = ['n\'est pas', 'ne sont pas', 'n\'a pas', 'ne peut pas', 'jamais', 'aucun']
        
        sentences = self.split_sentences(text)
        
        claims = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            has_marker = any(m in sentence_lower for m in markers)
            has_negation = any(n in sentence_lower for n in negations)
            
            if has_marker or has_negation:
                claims.append(sentence)
        
        return claims[:20]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule similarité entre deux textes (Levenshtein normalisé)
        
        Args:
            text1, text2: Textes à comparer
            
        Returns:
            Similarité [0-1]
        """
        if not text1 or not text2:
            return 0.0
        
        # Utiliser le plus long
        longer = text1 if len(text1) > len(text2) else text2
        shorter = text2 if len(text1) > len(text2) else text1
        
        if len(longer) == 0:
            return 1.0
        
        # Distance d'édition
        distance = self._edit_distance(longer.lower(), shorter.lower())
        
        return (len(longer) - distance) / len(longer)
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Distance de Levenshtein"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def claims_similarity(self, claim1: str, claim2: str) -> float:
        """
        Similarité sémantique entre affirmations (Jaccard sur mots)
        
        Args:
            claim1, claim2: Affirmations à comparer
            
        Returns:
            Similarité [0-1]
        """
        if not claim1 or not claim2:
            return 0.0
        
        # Extraire mots significatifs (4+ lettres)
        words1 = set(re.findall(r'\b\w{4,}\b', claim1.lower()))
        words2 = set(re.findall(r'\b\w{4,}\b', claim2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
