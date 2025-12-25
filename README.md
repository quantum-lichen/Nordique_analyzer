# 🧠 Nordique LMC

**Analyse Multi-IA par Complexité Minimale (Least Model Complexity)**

Application Streamlit pour synthétiser et analyser le consensus entre multiples réponses d'IA basée sur la théorie **CEML** (Cognitive Entropy Minimization Law).

---

## 🎯 Qu'est-ce que c'est?

**Nordique LMC** permet d'analyser et de comparer les réponses de plusieurs IA (Claude, ChatGPT, Gemini, etc.) pour identifier:

- ✅ **Consensus** - Ce sur quoi toutes les IA sont d'accord
- 🔀 **Divergences** - Les perspectives uniques de chaque IA
- 💡 **Insights** - Affirmations clés par IA
- ✨ **Émergences** - Concepts rares partagés entre 2 IA

---

## 🔬 Théorie: CEML

L'application utilise la théorie **CEML** (Cognitive Entropy Minimization Law):

```
J(s) = C(s|Ω) / (H(s) + ε)
```

Où:
- **J(s)** = Score LMC (Least Model Complexity)
- **C(s|Ω)** = Cohérence contextuelle [0-1]
- **H(s)** = Entropie de Shannon [0-1]
- **ε** = Constante de régularisation (défaut: 0.1)

**Plus le score est élevé, meilleure est la réponse** (cohérente ET concise).

---

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation rapide

```bash
# Cloner le repo
git clone https://github.com/quantum-lichen/nordique-lmc.git
cd nordique-lmc

# Installer dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

L'app sera disponible à `http://localhost:8501`

---

## 💻 Utilisation

### 1. Configurer

Dans la barre latérale:
- Choisissez le nombre d'IA à analyser (2-8)
- Sélectionnez un préréglage ou ajustez manuellement:
  - **ε (epsilon)**: Régularisation
  - **Seuil similarité**: Pour consensus
  - **Longueur min**: Texte minimum à analyser

### 2. Entrer les Réponses

Pour chaque IA:
- Nommez l'IA (Claude, ChatGPT, etc.)
- Collez la réponse complète
- Les scores (H, C, LMC) se calculent automatiquement

### 3. Analyser

Cliquez sur **"🔍 Analyser Consensus"** pour générer la synthèse multi-IA.

### 4. Explorer les Résultats

#### 🤝 Consensus
- **Concepts partagés**: Mots clés présents dans ≥50% des réponses
- **Affirmations consensus**: Claims similaires entre IA (avec % confiance)

#### 🔀 Divergences
- Concepts uniques à chaque IA
- Score de divergence

#### 💡 Insights
- Catégorisés par thème:
  - Structure
  - Processus
  - Impact
  - Relation

#### ✨ Insights Émergents
- Concepts rares partagés entre exactement 2 IA
- Indique connexions non évidentes

### 5. Exporter

- **JSON**: Synthèse complète + réponses
- **CSV**: Tableau des scores par IA

---

## 📊 Préréglages

| Preset | ε | Seuil | Longueur | Usage |
|--------|---|-------|----------|-------|
| **Standard** | 0.10 | 0.45 | 100 | Usage général |
| **Académique** | 0.05 | 0.50 | 200 | Textes scientifiques |
| **Créatif** | 0.20 | 0.40 | 100 | Contenu créatif |
| **Strict** | 0.01 | 0.60 | 150 | Maximum rigueur |

---

## 🏗️ Architecture

```
nordique-lmc/
├── app.py                  # Application Streamlit principale
├── utils/
│   ├── lmc_calculator.py   # Calculs LMC (H, C, score)
│   └── consensus_analyzer.py  # Analyse consensus/divergences
├── requirements.txt        # Dépendances Python
├── README.md              # Cette doc
└── .gitignore
```

### Classes Principales

#### `LMCCalculator`
```python
from utils.lmc_calculator import LMCCalculator

lmc = LMCCalculator(epsilon=0.1)

# Calculer entropie
H = lmc.calculate_entropy(text)

# Calculer cohérence
C = lmc.calculate_coherence(text)

# Score LMC
score = lmc.calculate_lmc_score(text)

# Extraire affirmations
claims = lmc.extract_claims(text)
```

#### `ConsensusAnalyzer`
```python
from utils.consensus_analyzer import ConsensusAnalyzer, ResponseData

analyzer = ConsensusAnalyzer(similarity_threshold=0.45)

# Préparer réponses
responses = {
    'ai_0': ResponseData(name='Claude', content='...', H=0.5, C=0.7, score=1.4),
    'ai_1': ResponseData(name='ChatGPT', content='...', H=0.4, C=0.8, score=2.0)
}

# Analyser
synthesis = analyzer.analyze_responses(responses)

# Résultats
consensus = synthesis['consensus']
divergences = synthesis['divergences']
insights = synthesis['insights']
emergent = synthesis['emergent_insights']
```

---

## 🧪 Exemple d'Usage

```python
import streamlit as st
from utils.lmc_calculator import LMCCalculator
from utils.consensus_analyzer import ConsensusAnalyzer, ResponseData

# Init
lmc = LMCCalculator()
analyzer = ConsensusAnalyzer()

# Réponses
text1 = "Le miel aide à calmer la toux..."
text2 = "Pour la toux, boire du thé chaud..."

# Calculer scores
H1 = lmc.calculate_entropy(text1)
C1 = lmc.calculate_coherence(text1)
score1 = C1 / (H1 + 0.1)

responses = {
    'ai_0': ResponseData(name='IA1', content=text1, H=H1, C=C1, score=score1),
    'ai_1': ResponseData(name='IA2', content=text2, H=..., C=..., score=...)
}

# Analyser
synthesis = analyzer.analyze_responses(responses)

# Afficher
st.json(synthesis['consensus'])
```

---

## 📚 Théorie CEML

### Entropie (H)

Mesure la **complexité** informationnelle du texte via l'entropie de Shannon:

```
H = -Σ p(x) log₂ p(x)
```

- Plus l'entropie est élevée, plus le texte est complexe/imprévisible
- Normalisée à [0-1]

### Cohérence (C)

Mesure la **structure** du texte via plusieurs facteurs:

```
C = 0.25·repetition + 0.35·length + 0.30·content + 0.10·negation
```

- **Répétition**: Taux de mots répétés (structure argumentative)
- **Longueur**: Cohérence des phrases
- **Contenu**: Ratio mots de contenu vs stopwords
- **Négation**: Bonus pour complexité logique

### Score LMC

```
LMC = C / (H + ε)
```

**Principe**: Une bonne réponse est **cohérente** (C élevé) mais **concise** (H bas).

**Interprétation**:
- `LMC < 1.0`: Réponse complexe/décousue
- `LMC ≈ 1.0-2.0`: Réponse équilibrée
- `LMC > 2.0`: Réponse très cohérente et concise (optimal)

---

## 🔗 Liens

- **Lichen Universe**: [GitHub](https://github.com/quantum-lichen/Lichen-Universe-Unified-V2)
- **Théorie CEML**: [Documentation](https://github.com/quantum-lichen/Lichen-Universe-Unified-V2/tree/main/CEML)
- **Manifest**: [manifest.json](https://quantum-lichen.github.io/Lichen-Universe-Unified-V2/manifest.json)

---

## 🤝 Contribution

Les contributions sont bienvenues!

```bash
# Fork le repo
git clone https://github.com/ton-username/nordique-lmc.git

# Créer branche
git checkout -b feature/ma-fonctionnalite

# Commit
git commit -m "Ajout: ma fonctionnalité"

# Push
git push origin feature/ma-fonctionnalite

# Créer Pull Request
```

---

## 📜 License

Apache License 2.0 - Voir [LICENSE](LICENSE)

---

## 👤 Auteur

**Bryan Ouellette** ([Lichen Architect](https://github.com/quantum-lichen))

- Email: lmc.theory@gmail.com
- Bluesky: [@symbion.bsky.social](https://bsky.app/profile/symbion.bsky.social)

---

## 🙏 Remerciements

- **Claude AI** (Anthropic) - Développement & Recherche
- **Théorie CEML** - Foundation mathématique
- **Lichen Universe** - Écosystème parent

---

## 📊 Statistiques

```python
{
  "version": "1.0.0",
  "language": "Python 3.8+",
  "framework": "Streamlit",
  "lines_of_code": "~1000",
  "classes": 3,
  "functions": 20+,
  "ai_supported": "8 max",
  "export_formats": ["JSON", "CSV"]
}
```

---

**🧠 Nordique LMC - Où la collaboration devient consensus**

💚 Fait avec amour pour l'IA éthique et collaborative

---

## 🚀 Déploiement

### Streamlit Cloud

1. Push le repo sur GitHub
2. Va sur [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect ton repo
4. Deploy! ✨

### Heroku

```bash
# Créer app
heroku create nordique-lmc

# Deploy
git push heroku main

# Ouvrir
heroku open
```

### Docker

```bash
# Build
docker build -t nordique-lmc .

# Run
docker run -p 8501:8501 nordique-lmc
```

---

**Happy Analyzing! 🎉**
