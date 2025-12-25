"""
🧠 NORDIQUE LMC - MONOLITHE EDITION
Analyse Multi-IA par Complexité Minimale
Basé sur la théorie CEML: J(s) = C(s|Ω) / (H(s) + ε)

Auteur: Bryan Ouellette (Lichen Architect)
Version: 1.0.0 (Monolith)
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import re
import math
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional
from collections import Counter
from dataclasses import dataclass

# --- 1. CONFIGURATION & CSS (DOIT ÊTRE AU DÉBUT) ---

st.set_page_config(
    page_title="Nordique LMC",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .consensus-high {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .consensus-medium {
        background: #f59e0b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .consensus-low {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CLASSES DE DONNÉES ---

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
    support: int
    ais: List[str]
    confidence: float

@dataclass
class Divergence:
    """Divergence d'une IA"""
    ai: str
    concepts: List[str]
    score: float

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

# --- 3. LOGIQUE MÉTIER : LMC CALCULATOR ---

class LMCCalculator:
    """
    Calculateur de scores LMC (Least Model Complexity)
    Implémente CEML: Cohérence / (Entropie + epsilon)
    """
    
    def __init__(self, epsilon: float = 0.001):
        self.epsilon = epsilon
        self.stopwords = {
            'cette', 'comme', 'dans', 'pour', 'avec', 'sont', 'leurs', 'plus', 'peut',
            'être', 'fait', 'permet', 'avoir', 'faire', 'entre', 'donc', 'aussi', 'ainsi',
            'selon', 'toute', 'tous', 'était', 'serait', 'pourrait', 'existe', 'autres',
            'chaque', 'peuvent', 'encore', 'toujours', 'quelque', 'certains', 'plusieurs',
            'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'car', 'ni', 'or'
        }
    
    def calculate_entropy(self, text: str) -> float:
        """H = -Σ p(x) log₂ p(x)"""
        if not text or len(text) < 50:
            return 0.0
        
        words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{3,}\b', text.lower())
        if not words:
            return 0.0
        
        freq = Counter(words)
        total = len(words)
        
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalisation empirique
        return min(entropy / 10.0, 1.0)
    
    def calculate_coherence(self, text: str) -> float:
        """C = f(répétition, longueur, contenu, négations)"""
        if not text or len(text) < 50:
            return 0.0
        
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if len(s) > 20]
        if len(sentences) < 2:
            return 0.5
        
        words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', text.lower())
        unique_words = set(words)
        
        repetition_rate = 1.0 - (len(unique_words) / max(len(words), 1))
        avg_sentence_length = len(words) / len(sentences)
        length_coherence = min(avg_sentence_length / 20.0, 1.0)
        
        content_words = [w for w in words if w not in self.stopwords]
        content_ratio = len(content_words) / max(len(words), 1)
        
        negations = re.findall(r"n'est pas|ne sont pas|n'a pas|ne peut pas|jamais|aucun", text.lower())
        negation_bonus = min(len(negations) / 10.0, 0.1)
        
        coherence = (
            repetition_rate * 0.25 +
            length_coherence * 0.35 +
            content_ratio * 0.30 +
            negation_bonus * 0.10
        )
        return coherence
    
    def calculate_lmc_score(self, text: str) -> Dict[str, float]:
        H = self.calculate_entropy(text)
        C = self.calculate_coherence(text)
        score = C / (H + self.epsilon)
        return {'H': H, 'C': C, 'score': score}
    
    def split_sentences(self, text: str) -> List[str]:
        if not text: return []
        sentences = re.split(r'[.!?]\s+|\n{2,}', text)
        return [s.strip() for s in sentences if 20 < len(s) < 500]
    
    def extract_claims(self, text: str) -> List[str]:
        if not text or len(text) < 100: return []
        
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
        if not text1 or not text2: return 0.0
        longer = text1 if len(text1) > len(text2) else text2
        shorter = text2 if len(text1) > len(text2) else text1
        if len(longer) == 0: return 1.0
        
        # Levenshtein simplifié via ensemble de mots (Jaccard) pour performance
        w1 = set(longer.lower().split())
        w2 = set(shorter.lower().split())
        intersection = len(w1 & w2)
        union = len(w1 | w2)
        return intersection / union if union > 0 else 0.0

    def claims_similarity(self, claim1: str, claim2: str) -> float:
        if not claim1 or not claim2: return 0.0
        words1 = set(re.findall(r'\b\w{4,}\b', claim1.lower()))
        words2 = set(re.findall(r'\b\w{4,}\b', claim2.lower()))
        if not words1 or not words2: return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

# --- 4. LOGIQUE MÉTIER : CONSENSUS ANALYZER ---

class ConsensusAnalyzer:
    """Analyseur de consensus et divergences multi-IA"""
    
    def __init__(self, similarity_threshold: float = 0.5):
        self.lmc = LMCCalculator()
        self.similarity_threshold = similarity_threshold
    
    def analyze_responses(self, responses: Dict[str, ResponseData]) -> Dict:
        if len(responses) < 2:
            return {
                'consensus': {'concepts': [], 'claims': [], 'confidence': 0.0},
                'divergences': [],
                'insights': {},
                'emergent_insights': []
            }
        
        all_concepts = self._extract_all_concepts(responses)
        consensus_concepts = self._find_consensus_concepts(all_concepts, responses)
        
        all_claims = self._extract_all_claims(responses)
        consensus_claims = self._find_consensus_claims(all_claims, responses)
        
        divergences = self._find_divergences(responses, consensus_concepts)
        emergent_insights = self._find_emergent_insights(responses)
        insights = self._categorize_insights(responses, consensus_concepts)
        
        confidence = self._calculate_consensus_confidence(
            len(consensus_concepts), len(consensus_claims), len(responses)
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
        threshold = len(responses) * 0.5
        consensus = []
        for word, data in all_concepts.items():
            if len(data['ais']) >= threshold and data['total'] >= 3:
                consensus.append(word)
        consensus.sort(key=lambda w: all_concepts[w]['total'], reverse=True)
        return consensus[:30]
    
    def _extract_all_claims(self, responses: Dict[str, ResponseData]) -> Dict[str, List[str]]:
        all_claims = {}
        for ai_name, response in responses.items():
            claims = self.lmc.extract_claims(response.content)
            all_claims[ai_name] = claims
        return all_claims
    
    def _find_consensus_claims(self, all_claims: Dict, responses: Dict) -> List[Claim]:
        consensus_claims = []
        processed = set()
        ai_names = list(all_claims.keys())
        
        for i, ai1 in enumerate(ai_names):
            for claim1 in all_claims[ai1]:
                if claim1 in processed: continue
                
                supporting_ais = [ai1]
                
                for ai2 in ai_names[i+1:]:
                    for claim2 in all_claims[ai2]:
                        if claim2 in processed: continue
                        
                        similarity = self.lmc.claims_similarity(claim1, claim2)
                        if similarity >= self.similarity_threshold:
                            supporting_ais.append(ai2)
                            processed.add(claim2)
                
                if len(supporting_ais) >= 2:
                    confidence = len(supporting_ais) / len(responses)
                    consensus_claims.append(Claim(
                        claim=claim1,
                        support=len(supporting_ais),
                        ais=supporting_ais,
                        confidence=confidence
                    ))
                processed.add(claim1)
        
        consensus_claims.sort(key=lambda c: c.support, reverse=True)
        return consensus_claims[:15]
    
    def _find_divergences(self, responses: Dict[str, ResponseData], consensus_concepts: List[str]) -> List[Divergence]:
        divergences = []
        consensus_set = set(consensus_concepts)
        
        for ai_name, response in responses.items():
            words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', response.content.lower())
            word_freq = Counter(words)
            unique_concepts = []
            for word, count in word_freq.most_common(20):
                if word not in consensus_set and count >= 2:
                    unique_concepts.append(word)
            
            if unique_concepts:
                score = len(unique_concepts) / max(len(consensus_concepts), 1)
                divergences.append(Divergence(ai=ai_name, concepts=unique_concepts[:10], score=score))
        
        divergences.sort(key=lambda d: d.score, reverse=True)
        return divergences
    
    def _find_emergent_insights(self, responses: Dict[str, ResponseData]) -> List[EmergentInsight]:
        insights = []
        ai_names = list(responses.keys())
        ai_concepts = {}
        for ai_name, response in responses.items():
            words = re.findall(r'\b[a-zàâäéèêëïîôöùûüœæç]{4,}\b', response.content.lower())
            ai_concepts[ai_name] = Counter(words)
        
        for i, ai1 in enumerate(ai_names):
            for ai2 in ai_names[i+1:]:
                concepts1 = ai_concepts[ai1]
                concepts2 = ai_concepts[ai2]
                common = set(concepts1.keys()) & set(concepts2.keys())
                
                for concept in common:
                    freq1 = concepts1[concept]
                    freq2 = concepts2[concept]
                    total_freq = sum(1 for ai_c in ai_concepts.values() if concept in ai_c)
                    
                    if total_freq <= len(responses) * 0.5 and freq1 >= 2 and freq2 >= 2:
                        similarity = min(freq1, freq2) / max(freq1, freq2)
                        insights.append(EmergentInsight(
                            concept1=concept, concept2=concept, ai1=ai1, ai2=ai2,
                            similarity=similarity, rarity1=1.0/total_freq, rarity2=1.0/total_freq
                        ))
        insights.sort(key=lambda i: i.rarity1, reverse=True)
        return insights[:10]
    
    def _categorize_insights(self, responses: Dict, consensus_concepts: List[str]) -> Dict[str, List[str]]:
        categories = {'structure': [], 'processus': [], 'impact': [], 'relation': []}
        keywords = {
            'structure': ['système', 'architecture', 'organisation', 'structure', 'modèle'],
            'processus': ['processus', 'méthode', 'approche', 'mécanisme', 'fonctionnement'],
            'impact': ['effet', 'impact', 'conséquence', 'résultat', 'influence'],
            'relation': ['relation', 'lien', 'connexion', 'interaction', 'corrélation']
        }
        for concept in consensus_concepts:
            for category, kws in keywords.items():
                if any(kw in concept for kw in kws):
                    categories[category].append(concept)
                    break
        return categories
    
    def _calculate_consensus_confidence(self, n_concepts: int, n_claims: int, n_ais: int) -> float:
        if n_ais < 2: return 0.0
        concept_score = min(n_concepts / 20.0, 1.0)
        claim_score = min(n_claims / 10.0, 1.0)
        return min((concept_score * 0.6 + claim_score * 0.4), 1.0)

# --- 5. INTERFACE UTILISATEUR : STREAMLIT APP ---

class NordiqueLMCApp:
    """Application principale"""
    
    def __init__(self):
        self.init_session_state()
        self.lmc = LMCCalculator()
        # On initialise l'analyseur plus tard avec les settings
        
        self.presets = {
            'Standard': {'epsilon': 0.1, 'similarity_threshold': 0.45, 'min_length': 100},
            'Académique': {'epsilon': 0.05, 'similarity_threshold': 0.5, 'min_length': 200},
            'Créatif': {'epsilon': 0.2, 'similarity_threshold': 0.4, 'min_length': 100},
            'Strict': {'epsilon': 0.01, 'similarity_threshold': 0.6, 'min_length': 150}
        }
        self.default_ai_names = ['Claude', 'ChatGPT', 'Gemini', 'Perplexity', 'Llama', 'Mistral', 'GPT-4', 'Grok']
    
    def init_session_state(self):
        if 'responses' not in st.session_state: st.session_state.responses = {}
        if 'num_ais' not in st.session_state: st.session_state.num_ais = 3
        if 'settings' not in st.session_state: st.session_state.settings = {'epsilon': 0.1, 'similarity_threshold': 0.45, 'min_length': 100}
        if 'synthesis' not in st.session_state: st.session_state.synthesis = None
        if 'history' not in st.session_state: st.session_state.history = []
    
    def render_sidebar(self):
        with st.sidebar:
            st.title("🧠 Nordique LMC")
            st.markdown("**Analyse Multi-IA par Complexité Minimale**")
            st.markdown("---")
            
            st.header("⚙️ Configuration")
            preset = st.selectbox("Préréglage", options=list(self.presets.keys()), index=0)
            if st.button("📋 Appliquer Preset"):
                st.session_state.settings = self.presets[preset].copy()
                st.success(f"Preset '{preset}' appliqué!")
            
            st.markdown("---")
            with st.expander("🔧 Paramètres Avancés"):
                st.session_state.settings['epsilon'] = st.slider("Epsilon (ε)", 0.001, 0.5, st.session_state.settings['epsilon'], 0.001)
                st.session_state.settings['similarity_threshold'] = st.slider("Seuil similarité", 0.0, 1.0, st.session_state.settings['similarity_threshold'], 0.05)
                st.session_state.settings['min_length'] = st.number_input("Longueur min", 50, 500, st.session_state.settings['min_length'], 50)
            
            st.markdown("---")
            st.header("🤖 Nombre d'IA")
            st.session_state.num_ais = st.number_input("Nombre d'IA", 2, 8, st.session_state.num_ais, 1)
            
            if st.button("🔄 Réinitialiser"):
                st.session_state.responses = {}
                st.session_state.synthesis = None
                st.success("Réinitialisé!")
            
            st.markdown("---")
            if st.session_state.synthesis:
                st.header("💾 Export")
                self.export_json()
                self.export_csv()
    
    def render_input_section(self):
        st.header("📝 Réponses des IA")
        col1, col2 = st.columns([3, 1])
        with col1: st.markdown("Entrez les réponses de chaque IA ci-dessous:")
        with col2: 
            if st.button("💡 Charger Exemple"): self.load_example()
        
        st.markdown("---")
        cols = st.columns(min(st.session_state.num_ais, 3))
        
        for i in range(st.session_state.num_ais):
            col_idx = i % len(cols)
            with cols[col_idx]:
                key = f"ai_{i}"
                ai_name = st.text_input(f"Nom IA {i+1}", value=st.session_state.responses.get(key, {}).get('name', self.default_ai_names[i]), key=f"name_{key}")
                content = st.text_area(f"Réponse {ai_name}", value=st.session_state.responses.get(key, {}).get('content', ''), height=200, key=f"content_{key}")
                
                if len(content) >= st.session_state.settings['min_length']:
                    H = self.lmc.calculate_entropy(content)
                    C = self.lmc.calculate_coherence(content)
                    score = C / (H + st.session_state.settings['epsilon'])
                    st.session_state.responses[key] = ResponseData(name=ai_name, content=content, H=H, C=C, score=score)
                    st.metric("Score LMC", f"{score:.3f}")
                    c1, c2 = st.columns(2)
                    c1.metric("H (Entropie)", f"{H:.3f}")
                    c2.metric("C (Cohérence)", f"{C:.3f}")
                elif content:
                    st.warning("⚠️ Texte trop court")
        
        st.markdown("---")
        valid = sum(1 for r in st.session_state.responses.values() if len(r.content) >= st.session_state.settings['min_length'])
        if valid >= 2:
            if st.button("🔍 Analyser Consensus", type="primary", use_container_width=True): self.analyze_responses()
        else:
            st.info(f"Besoin d'au moins 2 réponses valides ({valid}/2)")

    def render_synthesis_section(self):
        if not st.session_state.synthesis:
            st.info("ℹ️ Lancez une analyse d'abord.")
            return
        
        synth = st.session_state.synthesis
        st.header("🎯 Synthèse Multi-IA")
        
        c1, c2, c3 = st.columns(3)
        conf = synth['consensus']['confidence']
        color = '#10b981' if conf > 0.7 else '#f59e0b' if conf > 0.4 else '#ef4444'
        
        c1.markdown(f'<div class="metric-card"><h3>Confiance</h3><h1 style="color:{color}">{conf:.1%}</h1></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h3>Concepts</h3><h1>{len(synth["consensus"]["concepts"])}</h1></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>Affirmations</h3><h1>{len(synth["consensus"]["claims"])}</h1></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        t1, t2, t3, t4 = st.tabs(["🤝 Consensus", "🔀 Divergences", "💡 Insights", "✨ Émergents"])
        
        with t1:
            st.subheader("Concepts Partagés")
            if synth['consensus']['concepts']:
                st.dataframe(pd.DataFrame({'Concept': synth['consensus']['concepts'][:20]}), use_container_width=True)
            
            st.subheader("Affirmations Consensus")
            for claim in synth['consensus']['claims'][:10]:
                conf_cls = 'consensus-high' if claim.confidence > 0.7 else 'consensus-medium' if claim.confidence > 0.4 else 'consensus-low'
                st.markdown(f"""
                <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; color: black;">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="{conf_cls}">{claim.confidence:.0%} confiance</span>
                        <span>Support: {claim.support} IA</span>
                    </div>
                    <p style="margin-top:0.5rem"><strong>{claim.claim}</strong></p>
                    <small>IA: {', '.join(claim.ais)}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with t2:
            if synth['divergences']:
                for div in synth['divergences']:
                    with st.expander(f"🤖 {div.ai} (Divergence: {div.score:.2f})"):
                        st.write(", ".join(div.concepts))
            else: st.info("Pas de divergences majeures.")
            
        with t3:
            for cat, items in synth['insights'].items():
                if items:
                    with st.expander(f"📁 {cat.capitalize()}"):
                        for i in items[:10]: st.write(f"- {i}")
        
        with t4:
            if synth['emergent_insights']:
                for ins in synth['emergent_insights']:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; color: white;">
                        <strong>{ins.ai1} ↔️ {ins.ai2}</strong><br>
                        <em>"{ins.concept1}"</em><br>
                        <small>Rareté: {ins.rarity1:.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("Pas d'insights émergents.")

    def analyze_responses(self):
        analyzer = ConsensusAnalyzer(st.session_state.settings['similarity_threshold'])
        valid = {k: v for k, v in st.session_state.responses.items() if len(v.content) >= st.session_state.settings['min_length']}
        st.session_state.synthesis = analyzer.analyze_responses(valid)
        st.success("Analyse terminée!")

    def load_example(self):
        ex = {
            'ai_0': ResponseData("Claude", "Pour la toux, boire du thé chaud avec du miel aide beaucoup. Le repos est essentiel.", 0.2, 0.8, 4.0),
            'ai_1': ResponseData("ChatGPT", "Le miel et le citron dans de l'eau chaude calment la toux. Dormez bien.", 0.3, 0.7, 2.3),
            'ai_2': ResponseData("Gemini", "Astuce: miel + citron. L'hydratation est clé. Reposez-vous pour guérir.", 0.25, 0.75, 3.0)
        }
        st.session_state.responses = ex
        st.rerun()

    def export_json(self):
        if st.session_state.synthesis:
            data = {
                'timestamp': datetime.now().isoformat(),
                'synthesis': {
                    'consensus': {'concepts': st.session_state.synthesis['consensus']['concepts'], 'confidence': st.session_state.synthesis['consensus']['confidence']},
                    'divergences': [d.__dict__ for d in st.session_state.synthesis['divergences']]
                }
            }
            st.download_button("📥 JSON", json.dumps(data, indent=2, default=str), "nordique_lmc.json", "application/json")

    def export_csv(self):
        if st.session_state.responses:
            df = pd.DataFrame([{'IA': v.name, 'LMC': v.score} for v in st.session_state.responses.values()])
            st.download_button("📊 CSV", df.to_csv(), "nordique_lmc.csv", "text/csv")

    def run(self):
        self.render_sidebar()
        t1, t2 = st.tabs(["📝 Entrées", "📊 Synthèse"])
        with t1: self.render_input_section()
        with t2: self.render_synthesis_section()

# --- 6. POINT D'ENTRÉE ---

if __name__ == "__main__":
    app = NordiqueLMCApp()
    app.run()
