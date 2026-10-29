# coding_ai_math
logique mathemaque de coding grace a cette outils votre agent ne fera plus erreur
# ⚛️ PROTON-CALC TOOL (v1.1)

> **Moteur Mathématique & Générateur de Code Souverain pour l'IA.**
> *"Data without type is a rumor. Data with type is a truth."*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-NEXUS--PROTON--1.0-00ff9d?style=for-the-badge)](#)
[![Sovereignty](https://img.shields.io/badge/Local--First-100%25-00d4ff?style=for-the-badge)](#)

---

## 🧬 Qu'est-ce que PROTON-CALC ?

Les modèles de langage (LLM) sont statistiquement doués pour le texte, mais **mathématiquement faillibles**. Ils hallucinent des résultats, génèrent du code qui plante, et sont incapables de vérifier leurs propres erreurs.

**PROTON-CALC** est le remède. C'est un outil déterministe conçu pour être branché sur une IA (via Function Calling). Il permet à votre agent de :
1. **Calculer** des expressions avec une précision absolue (pas de floating-point errors).
2. **Générer** du code Python mathématiquement correct, prêt à être exécuté.
3. **Vérifier** si un code produit *réellement* le bon résultat (via une exécution isolée).

---

## 🚀 Nouveautés de la v1.1 (Le Patch Qualité)

Cette version corrige les failles critiques de la v1.0 pour garantir une boucle **DGK ⇄ IA** sans erreur :

- **Remplacement Regex Sécurisé** : Fini les corruptions de texte. `mean` ne devient plus `mmath.ean`, et `1e-9` reste un nombre valide.
- **`^` = Puissance** : Aligné sur la notation mathématique standard et sur le générateur de code. (`2^10` donne bien `1024`, et non `8`).
- **Vérification par Sous-Processus** : Le code généré n'est plus exécuté avec `exec` dans le processus principal. Il est isolé dans un sous-processus avec un `timeout` de 5 secondes, empêchant tout blocage ou accès non autorisé.
- **Scan par Frontières de Mots** : Les mots dangereux (`open`, `system`) sont détectés via `\b`, ce qui empêche les faux positifs (le mot "opened" n'est plus bloqué).

---

## 🛠️ Installation

```bash
git clone https://github.com/Aissamohammedi88/proton-calc.git
cd proton-calc
# Aucune dépendance externe requise
python3 proton_calc.py
