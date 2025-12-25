"""
Nordique LMC - Analyseur de Consensus Multi-IA
Détecte consensus, divergences, et insights émergents
"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter
from dataclasses import dataclass
from .lmc_calculator import LMCCalculator


@dataclass
class ResponseData:
    """Données d'une réponse IA"""
    name: str
    content: str
    H: float  # Entropie
    C: float  # Cohérence
    score: float  # Score LMC


@dataclass
class Claim:
    """Affirmation avec support multi-IA"""
    claim: str
    support: int  # Nombre d'IA qui supportent
    ais: List[str]  # Noms des IA
    confidence: float  # Confiance [0-1]


@dataclass
class Divergence:
    """Divergence d'une IA"""
    ai: str
    concepts: List[str]
    score: float  # Score de divergence


@dataclass
class EmergentInsight:
    """Insight émergent entre deux IA"""
    concept1: str
    concept2: str
    ai1: str
    ai2: str
    similarity: float
    rarity1: float
    rarity2: float


class ConsensusAnalyzer:
    """
    Analyseur de consensus et divergences multi-IA
    """
    
    def __init__(self, similarity_threshold: float = 0.5):
        """
        Initialise l'analyseur
        
        Args:
            similarity_threshold: Seuil de similarité pour consensus
        """
        self.lmc = LMCCalculator()
        self.similarity_threshold = similarity_threshold
    
    def analyze_responses(self, responses: Dict[str, ResponseData]) -> Dict:
        """
        Analyse complète des réponses multi-IA
        
        Args:
            responses: Dict {nom_ia: ResponseData}
            
        Returns:
            Dict avec consensus, divergences, insights
        """
        if len(responses) < 2:
            return {
                'consensus': {'concepts': [], 'claims': [], 'confidence': 0.0},
                'divergences': [],
                'insights': {},
                'emergent_insights': []
            }
        
        # 1. Extraire concepts fréquents
        all_concepts = self._extract_all_concepts(responses)
        consensus_concepts = self._find_consensus_concepts(all_concepts, responses)
        
        # 2. Analyser affirmations
        all_claims = self._extract_all_claims(responses)
        consensus_claims = self._find_consensus_claims(all_claims, responses)
        
        # 3. Détecter divergences
        divergences = self._find_divergences(responses, consensus_concepts)
        
        # 4. Trouver insights émergents
        emergent_insights = self._find_emergent_insights(responses)
        
        # 5. Insights par catégorie
        insights = self._categorize_insights(responses, consensus_concepts)
        
        # Confiance globale du consensus
        confidence = self._calculate_consensus_confidence(
            len(consensus_concepts),
            len(consensus_claims),
            len(responses)
        )
        
        return {
            'consensus': {
                'concepts': consensus_concepts,
                'claims': consensus_claims,
                'confidence': confidence
            },
            'divergences': divergences,
            'insights': insights,
            'emergent_insights': emergent_insights
        }
    
    def _extract_all_concepts(self, responses: Dict[str, ResponseData]) -> Dict[str, Dict]:
        """Extrait tous les concepts (mots 4+) avec fréquences"""
        all_words = {}
        
        for ai_name, response in responses.items():
            words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', response.content.lower())
            
            for word in words:
                if word not in all_words:
                    all_words[word] = {'total': 0, 'ais': set()}
                
                all_words[word]['total'] += 1
                all_words[word]['ais'].add(ai_name)
        
        return all_words
    
    def _find_consensus_concepts(self, all_concepts: Dict, responses: Dict) -> List[str]:
        """Trouve concepts présents dans majorité des réponses"""
        threshold = len(responses) * 0.5  # 50%+ des IA
        
        consensus = []
        for word, data in all_concepts.items():
            if len(data['ais']) >= threshold and data['total'] >= 3:
                consensus.append(word)
        
        # Trier par fréquence
        consensus.sort(key=lambda w: all_concepts[w]['total'], reverse=True)
        
        return consensus[:30]  # Top 30
    
    def _extract_all_claims(self, responses: Dict[str, ResponseData]) -> Dict[str, List[str]]:
        """Extrait toutes les affirmations par IA"""
        all_claims = {}
        
        for ai_name, response in responses.items():
            claims = self.lmc.extract_claims(response.content)
            all_claims[ai_name] = claims
        
        return all_claims
    
    def _find_consensus_claims(self, all_claims: Dict, responses: Dict) -> List[Claim]:
        """Trouve affirmations similaires entre IA"""
        consensus_claims = []
        processed = set()
        
        ai_names = list(all_claims.keys())
        
        for i, ai1 in enumerate(ai_names):
            for claim1 in all_claims[ai1]:
                if claim1 in processed:
                    continue
                
                supporting_ais = [ai1]
                similar_claims = [claim1]
                
                # Chercher claims similaires dans autres IA
                for ai2 in ai_names[i+1:]:
                    for claim2 in all_claims[ai2]:
                        if claim2 in processed:
                            continue
                        
                        similarity = self.lmc.claims_similarity(claim1, claim2)
                        
                        if similarity >= self.similarity_threshold:
                            supporting_ais.append(ai2)
                            similar_claims.append(claim2)
                            processed.add(claim2)
                
                # Si supporté par 2+ IA
                if len(supporting_ais) >= 2:
                    confidence = len(supporting_ais) / len(responses)
                    
                    consensus_claims.append(Claim(
                        claim=claim1,
                        support=len(supporting_ais),
                        ais=supporting_ais,
                        confidence=confidence
                    ))
                
                processed.add(claim1)
        
        # Trier par support
        consensus_claims.sort(key=lambda c: c.support, reverse=True)
        
        return consensus_claims[:15]  # Top 15
    
    def _find_divergences(
        self,
        responses: Dict[str, ResponseData],
        consensus_concepts: List[str]
    ) -> List[Divergence]:
        """Détecte IA avec concepts uniques (divergents)"""
        divergences = []
        consensus_set = set(consensus_concepts)
        
        for ai_name, response in responses.items():
            words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', response.content.lower())
            word_freq = Counter(words)
            
            # Concepts uniques (pas dans consensus)
            unique_concepts = []
            for word, count in word_freq.most_common(20):
                if word not in consensus_set and count >= 2:
                    unique_concepts.append(word)
            
            if unique_concepts:
                # Score de divergence
                divergence_score = len(unique_concepts) / max(len(consensus_concepts), 1)
                
                divergences.append(Divergence(
                    ai=ai_name,
                    concepts=unique_concepts[:10],
                    score=divergence_score
                ))
        
        # Trier par score
        divergences.sort(key=lambda d: d.score, reverse=True)
        
        return divergences
    
    def _find_emergent_insights(self, responses: Dict[str, ResponseData]) -> List[EmergentInsight]:
        """Trouve insights émergents (concepts rares partagés entre 2 IA)"""
        insights = []
        ai_names = list(responses.keys())
        
        # Extraire concepts par IA avec fréquences
        ai_concepts = {}
        for ai_name, response in responses.items():
            words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', response.content.lower())
            ai_concepts[ai_name] = Counter(words)
        
        # Comparer paires d'IA
        for i, ai1 in enumerate(ai_names):
            for ai2 in ai_names[i+1:]:
                concepts1 = ai_concepts[ai1]
                concepts2 = ai_concepts[ai2]
                
                # Trouver concepts communs rares
                common = set(concepts1.keys()) & set(concepts2.keys())
                
                for concept in common:
                    freq1 = concepts1[concept]
                    freq2 = concepts2[concept]
                    
                    # Calcul rareté (inverse de fréquence totale)
                    total_freq1 = sum(1 for ai_c in ai_concepts.values() if concept in ai_c)
                    rarity1 = 1.0 / total_freq1
                    rarity2 = rarity1  # Même concept
                    
                    # Si rare (présent dans <50% des IA) et significatif
                    if total_freq1 <= len(responses) * 0.5 and freq1 >= 2 and freq2 >= 2:
                        similarity = min(freq1, freq2) / max(freq1, freq2)
                        
                        insights.append(EmergentInsight(
                            concept1=concept,
                            concept2=concept,
                            ai1=ai1,
                            ai2=ai2,
                            similarity=similarity,
                            rarity1=rarity1,
                            rarity2=rarity2
                        ))
        
        # Trier par rareté
        insights.sort(key=lambda i: i.rarity1, reverse=True)
        
        return insights[:10]  # Top 10
    
    def _categorize_insights(
        self,
        responses: Dict[str, ResponseData],
        consensus_concepts: List[str]
    ) -> Dict[str, List[str]]:
        """Catégorise insights par thème"""
        categories = {
            'structure': [],
            'processus': [],
            'impact': [],
            'relation': []
        }
        
        # Keywords par catégorie
        keywords = {
            'structure': ['système', 'architecture', 'organisation', 'structure', 'modèle', 'composant'],
            'processus': ['processus', 'méthode', 'approche', 'mécanisme', 'fonctionnement', 'évolution'],
            'impact': ['effet', 'impact', 'conséquence', 'résultat', 'influence', 'changement'],
            'relation': ['relation', 'lien', 'connexion', 'interaction', 'corrélation', 'dépendance']
        }
        
        for concept in consensus_concepts:
            for category, kws in keywords.items():
                if any(kw in concept for kw in kws):
                    categories[category].append(concept)
                    break
        
        return categories
    
    def _calculate_consensus_confidence(
        self,
        n_concepts: int,
        n_claims: int,
        n_ais: int
    ) -> float:
        """Calcule confiance globale du consensus"""
        if n_ais < 2:
            return 0.0
        
        # Pondération
        concept_score = min(n_concepts / 20.0, 1.0)
        claim_score = min(n_claims / 10.0, 1.0)
        
        confidence = (concept_score * 0.6 + claim_score * 0.4)
        
        return min(confidence, 1.0)
