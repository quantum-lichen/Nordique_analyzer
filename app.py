"""
Nordique LMC - Analyse Multi-IA par Complexité Minimale
Application Streamlit pour synthèse et consensus multi-modèles
Basé sur la théorie CEML: J(s) = C(s|Ω) / (H(s) + ε)
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
import sys
sys.path.append('.')

from utils.lmc_calculator import LMCCalculator
from utils.consensus_analyzer import ConsensusAnalyzer, ResponseData


# Configuration page
st.set_page_config(
    page_title="Nordique LMC",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
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
    }
    .consensus-high {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .consensus-medium {
        background: #f59e0b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .consensus-low {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


class NordiqueLMCApp:
    """Application principale Nordique LMC"""
    
    def __init__(self):
        self.init_session_state()
        self.lmc = LMCCalculator()
        self.analyzer = ConsensusAnalyzer()
        
        # Presets
        self.presets = {
            'Standard': {'epsilon': 0.1, 'similarity_threshold': 0.45, 'min_length': 100},
            'Académique': {'epsilon': 0.05, 'similarity_threshold': 0.5, 'min_length': 200},
            'Créatif': {'epsilon': 0.2, 'similarity_threshold': 0.4, 'min_length': 100},
            'Strict': {'epsilon': 0.01, 'similarity_threshold': 0.6, 'min_length': 150}
        }
        
        # IA par défaut
        self.default_ai_names = [
            'Claude', 'ChatGPT', 'Gemini', 'Perplexity', 
            'Llama', 'Mistral', 'GPT-4', 'Grok'
        ]
    
    def init_session_state(self):
        """Initialise les variables de session"""
        if 'responses' not in st.session_state:
            st.session_state.responses = {}
        if 'num_ais' not in st.session_state:
            st.session_state.num_ais = 3
        if 'settings' not in st.session_state:
            st.session_state.settings = {'epsilon': 0.1, 'similarity_threshold': 0.45, 'min_length': 100}
        if 'synthesis' not in st.session_state:
            st.session_state.synthesis = None
        if 'history' not in st.session_state:
            st.session_state.history = []
    
    def render_sidebar(self):
        """Rendu de la barre latérale"""
        with st.sidebar:
            st.title("🧠 Nordique LMC")
            st.markdown("**Analyse Multi-IA par Complexité Minimale**")
            st.markdown("---")
            
            # Configuration
            st.header("⚙️ Configuration")
            
            # Preset
            preset = st.selectbox(
                "Préréglage",
                options=list(self.presets.keys()),
                index=0
            )
            
            if st.button("📋 Appliquer Preset"):
                st.session_state.settings = self.presets[preset].copy()
                st.success(f"Preset '{preset}' appliqué!")
            
            st.markdown("---")
            
            # Paramètres avancés
            with st.expander("🔧 Paramètres Avancés"):
                st.session_state.settings['epsilon'] = st.slider(
                    "Epsilon (ε)",
                    min_value=0.001,
                    max_value=0.5,
                    value=st.session_state.settings['epsilon'],
                    step=0.001,
                    help="Régularisation pour éviter division par zéro"
                )
                
                st.session_state.settings['similarity_threshold'] = st.slider(
                    "Seuil de similarité",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.settings['similarity_threshold'],
                    step=0.05,
                    help="Seuil pour considérer deux claims similaires"
                )
                
                st.session_state.settings['min_length'] = st.number_input(
                    "Longueur minimale",
                    min_value=50,
                    max_value=500,
                    value=st.session_state.settings['min_length'],
                    step=50,
                    help="Longueur minimale de texte pour analyse"
                )
            
            st.markdown("---")
            
            # Nombre d'IA
            st.header("🤖 Nombre d'IA")
            st.session_state.num_ais = st.number_input(
                "Combien d'IA analyser?",
                min_value=2,
                max_value=8,
                value=st.session_state.num_ais,
                step=1
            )
            
            if st.button("🔄 Réinitialiser"):
                st.session_state.responses = {}
                st.session_state.synthesis = None
                st.success("Réinitialisé!")
            
            st.markdown("---")
            
            # Export
            st.header("💾 Export")
            if st.session_state.synthesis:
                if st.button("📥 Télécharger JSON"):
                    self.export_json()
                if st.button("📊 Télécharger CSV"):
                    self.export_csv()
            
            st.markdown("---")
            
            # Info
            st.markdown("""
            ### 📖 À propos
            
            **Nordique LMC** analyse le consensus et les divergences entre multiples IA.
            
            **Basé sur CEML:**
            ```
            J(s) = C(s) / (H(s) + ε)
            ```
            
            **Légende:**
            - **H**: Entropie (complexité)
            - **C**: Cohérence (structure)
            - **J**: Score LMC
            
            Plus le score est élevé, meilleure est la réponse.
            """)
    
    def render_input_section(self):
        """Section d'entrée des réponses"""
        st.header("📝 Réponses des IA")
        
        # Exemple
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Entrez les réponses de chaque IA ci-dessous:")
        with col2:
            if st.button("💡 Charger Exemple"):
                self.load_example()
        
        st.markdown("---")
        
        # Inputs pour chaque IA
        cols = st.columns(min(st.session_state.num_ais, 3))
        
        for i in range(st.session_state.num_ais):
            col_idx = i % len(cols)
            
            with cols[col_idx]:
                key = f"ai_{i}"
                
                # Nom de l'IA
                ai_name = st.text_input(
                    f"Nom IA {i+1}",
                    value=st.session_state.responses.get(key, {}).get('name', self.default_ai_names[i]),
                    key=f"name_{key}"
                )
                
                # Contenu
                content = st.text_area(
                    f"Réponse {ai_name}",
                    value=st.session_state.responses.get(key, {}).get('content', ''),
                    height=200,
                    key=f"content_{key}",
                    placeholder=f"Entrez la réponse de {ai_name}..."
                )
                
                # Calculer scores si contenu suffisant
                if len(content) >= st.session_state.settings['min_length']:
                    H = self.lmc.calculate_entropy(content)
                    C = self.lmc.calculate_coherence(content)
                    score = C / (H + st.session_state.settings['epsilon'])
                    
                    # Stocker
                    st.session_state.responses[key] = ResponseData(
                        name=ai_name,
                        content=content,
                        H=H,
                        C=C,
                        score=score
                    )
                    
                    # Afficher métriques
                    st.metric("Score LMC", f"{score:.3f}")
                    
                    col_h, col_c = st.columns(2)
                    with col_h:
                        st.metric("H (Entropie)", f"{H:.3f}")
                    with col_c:
                        st.metric("C (Cohérence)", f"{C:.3f}")
                
                elif content:
                    st.warning("⚠️ Texte trop court pour analyse")
        
        st.markdown("---")
        
        # Bouton analyse
        valid_responses = sum(1 for r in st.session_state.responses.values() 
                            if len(r.content) >= st.session_state.settings['min_length'])
        
        if valid_responses >= 2:
            if st.button("🔍 Analyser Consensus", type="primary", use_container_width=True):
                self.analyze_responses()
        else:
            st.info(f"ℹ️ Besoin d'au moins 2 réponses valides (actuellement: {valid_responses})")
    
    def render_synthesis_section(self):
        """Section de synthèse"""
        if not st.session_state.synthesis:
            st.info("ℹ️ Effectuez une analyse pour voir la synthèse")
            return
        
        synth = st.session_state.synthesis
        
        st.header("🎯 Synthèse Multi-IA")
        
        # Métriques globales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence = synth['consensus']['confidence']
            color = 'green' if confidence > 0.7 else 'orange' if confidence > 0.4 else 'red'
            st.markdown(f"""
            <div class="metric-card">
                <h3>Confiance Consensus</h3>
                <h1 style="color:{color}">{confidence:.1%}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            n_concepts = len(synth['consensus']['concepts'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Concepts Partagés</h3>
                <h1>{n_concepts}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            n_claims = len(synth['consensus']['claims'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Affirmations Consensus</h3>
                <h1>{n_claims}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🤝 Consensus",
            "🔀 Divergences",
            "💡 Insights",
            "✨ Émergents"
        ])
        
        with tab1:
            self.render_consensus_tab(synth)
        
        with tab2:
            self.render_divergences_tab(synth)
        
        with tab3:
            self.render_insights_tab(synth)
        
        with tab4:
            self.render_emergent_tab(synth)
    
    def render_consensus_tab(self, synth):
        """Rendu tab consensus"""
        st.subheader("🤝 Consensus Multi-IA")
        
        # Concepts
        st.markdown("### 📚 Concepts Partagés")
        if synth['consensus']['concepts']:
            concepts_df = pd.DataFrame({
                'Concept': synth['consensus']['concepts'][:20],
                'Rang': range(1, min(21, len(synth['consensus']['concepts'])+1))
            })
            st.dataframe(concepts_df, use_container_width=True)
        else:
            st.info("Aucun concept partagé trouvé")
        
        st.markdown("---")
        
        # Claims
        st.markdown("### 📋 Affirmations Consensus")
        if synth['consensus']['claims']:
            for claim in synth['consensus']['claims'][:10]:
                confidence_class = (
                    'consensus-high' if claim.confidence > 0.7 else
                    'consensus-medium' if claim.confidence > 0.4 else
                    'consensus-low'
                )
                
                st.markdown(f"""
                <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="{confidence_class}">{claim.confidence:.0%} confiance</span>
                        <span style="color: #6b7280;">Support: {claim.support}/{len(st.session_state.responses)} IA</span>
                    </div>
                    <p style="margin-top: 0.5rem;">{claim.claim}</p>
                    <p style="color: #6b7280; font-size: 0.875rem;">IA: {', '.join(claim.ais)}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune affirmation consensus trouvée")
    
    def render_divergences_tab(self, synth):
        """Rendu tab divergences"""
        st.subheader("🔀 Divergences des IA")
        
        if synth['divergences']:
            for div in synth['divergences']:
                with st.expander(f"🤖 {div.ai} (Score: {div.score:.3f})"):
                    st.markdown("**Concepts uniques:**")
                    concepts_str = ", ".join(div.concepts)
                    st.markdown(f"_{concepts_str}_")
        else:
            st.info("Aucune divergence significative détectée")
    
    def render_insights_tab(self, synth):
        """Rendu tab insights"""
        st.subheader("💡 Insights par Catégorie")
        
        for category, concepts in synth['insights'].items():
            if concepts:
                with st.expander(f"📁 {category.capitalize()} ({len(concepts)})"):
                    for concept in concepts[:10]:
                        st.markdown(f"- {concept}")
    
    def render_emergent_tab(self, synth):
        """Rendu tab insights émergents"""
        st.subheader("✨ Insights Émergents")
        
        st.markdown("""
        Concepts **rares** partagés entre exactement **2 IA**.  
        Indique des connexions émergentes non évidentes.
        """)
        
        if synth['emergent_insights']:
            for insight in synth['emergent_insights']:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); 
                            padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; color: white;">
                    <strong>{insight.ai1} ↔️ {insight.ai2}</strong><br>
                    <em>"{insight.concept1}" ≈ "{insight.concept2}"</em><br>
                    <small>Similarité: {insight.similarity:.2%} | Rareté: {insight.rarity1:.2f}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun insight émergent détecté")
    
    def analyze_responses(self):
        """Analyse les réponses"""
        with st.spinner("🔍 Analyse en cours..."):
            # Filtrer réponses valides
            valid_responses = {
                k: v for k, v in st.session_state.responses.items()
                if len(v.content) >= st.session_state.settings['min_length']
            }
            
            # Analyser
            synthesis = self.analyzer.analyze_responses(valid_responses)
            
            # Sauvegarder
            st.session_state.synthesis = synthesis
            
            # Ajouter à l'historique
            history_item = {
                'timestamp': datetime.now().isoformat(),
                'synthesis': synthesis,
                'settings': st.session_state.settings.copy()
            }
            st.session_state.history.append(history_item)
            
            st.success("✅ Analyse terminée!")
    
    def load_example(self):
        """Charge un exemple"""
        example_responses = {
            'ai_0': ResponseData(
                name="Claude",
                content="Pour soulager la toux, il est important de rester bien hydraté en buvant beaucoup de liquides chauds comme du thé ou du bouillon. Un humidificateur peut aider à humidifier les voies respiratoires. Le miel a des propriétés apaisantes naturelles. Le repos est essentiel pour permettre au corps de récupérer. Si la toux persiste plus de quelques jours ou s'accompagne de fièvre, il faut consulter un médecin.",
                H=0, C=0, score=0
            ),
            'ai_1': ResponseData(
                name="ChatGPT",
                content="Les remèdes pour calmer la toux incluent : boire des boissons chaudes (tisanes, eau tiède avec du miel et du citron), utiliser un humidificateur pour l'air sec, prendre des pastilles pour la gorge, et se reposer suffisamment. Évitez les irritants comme la fumée. Si la douleur persiste ou si vous êtes allergique à certains ingrédients, consultez un professionnel de santé. Pour les enfants, adaptez les dosages et évitez le miel avant 1 an.",
                H=0, C=0, score=0
            ),
            'ai_2': ResponseData(
                name="Gemini",
                content="Voici des astuces de grand-mère pour le confort : Le miel est un classique efficace, surtout avec du citron chaud. L'humidité combat l'air sec qui aggrave la toux. Dormir la tête surélevée aide à drainer. Les pastilles gardent la gorge humide. Important : si la toux persiste ou s'aggrave, consultez un médecin. Ces conseils ne remplacent pas l'avis d'un professionnel de santé.",
                H=0, C=0, score=0
            )
        }
        
        st.session_state.responses = example_responses
        st.session_state.num_ais = 3
        st.success("✅ Exemple chargé!")
        st.rerun()
    
    def export_json(self):
        """Export JSON"""
        if st.session_state.synthesis:
            data = {
                'timestamp': datetime.now().isoformat(),
                'synthesis': st.session_state.synthesis,
                'settings': st.session_state.settings,
                'responses': {
                    k: {
                        'name': v.name,
                        'content': v.content,
                        'H': v.H,
                        'C': v.C,
                        'score': v.score
                    }
                    for k, v in st.session_state.responses.items()
                }
            }
            
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Télécharger JSON",
                data=json_str,
                file_name=f"nordique_lmc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def export_csv(self):
        """Export CSV"""
        if st.session_state.synthesis:
            # Créer DataFrame
            rows = []
            for key, resp in st.session_state.responses.items():
                rows.append({
                    'IA': resp.name,
                    'Entropie_H': resp.H,
                    'Cohérence_C': resp.C,
                    'Score_LMC': resp.score,
                    'Longueur': len(resp.content)
                })
            
            df = pd.DataFrame(rows)
            csv = df.to_csv(index=False)
            
            st.download_button(
                "📊 Télécharger CSV",
                data=csv,
                file_name=f"nordique_lmc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def run(self):
        """Lance l'application"""
        self.render_sidebar()
        
        # Tabs principales
        tab_input, tab_synthesis = st.tabs(["📝 Entrées", "📊 Synthèse"])
        
        with tab_input:
            self.render_input_section()
        
        with tab_synthesis:
            self.render_synthesis_section()


def main():
    """Point d'entrée principal"""
    app = NordiqueLMCApp()
    app.run()


if __name__ == "__main__":
    main()
