#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   ⚛️ PROTON-CALC TOOL — Moteur Mathématique & Générateur de Code pour IA     ║
║   Auteur : Aissa Mohammedi (DGK)                                             ║
║   Licence : NEXUS-PROTON-1.0                                                 ║
║                                                                              ║
║   Permet à l'IA de :                                                         ║
║   • Calculer des expressions complexes avec une précision absolue.           ║
║   • Générer du code Python mathématiquement correct.                         ║
║   • Vérifier que son code produit le bon résultat.                           ║
║   • Résoudre des systèmes d'équations et des statistiques.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import math
import cmath
import statistics
import ast
import operator
from typing import Any, Dict, List, Union, Callable
from fractions import Fraction
import re          # [v1.1] remplacement sûr par frontières de mots
import subprocess  # [v1.1] exécution isolée en sous-processus
import sys         # [v1.1] sys.executable pour le sous-processus
import tempfile    # [v1.1] dossier d'exécution jetable
import os          # [v1.1] chemins du dossier jetable

# ══════════════════════════════════════════════════════════════════════════════
# [v1.1] PATCH QUALITÉ — boucle DGK ⇄ IA, tout prouvé par exécution
#   1. Générateur : regex par frontières de mots (v1.0 corrompait exp/1e-9/mean)
#   2. ^ = puissance partout, aligné sur le générateur (xor reste via xor(a, b))
#   3. verify_python_code : sous-processus isolé + timeout + sortie comparée
# ══════════════════════════════════════════════════════════════════════════════
# SÉCURITÉ : OPÉRATEURS AUTORISÉS (AST)
# ══════════════════════════════════════════════════════════════════════════════


class SafeMathEvaluator:
    """
    Évaluateur mathématique sécurisé basé sur l'AST.
    Aucun accès à __builtins__, ni à os, sys, etc.
    """

    # Opérateurs binaires autorisés
    _BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        # [v1.1] ^ = PUISSANCE, aligné sur le générateur et la notation math.
        # (v1.0 : ^ = xor → 2^10 = 8 alors que le générateur faisait 2**10 = 1024.
        #  Le vrai xor reste accessible via la fonction xor(a, b).)
        ast.BitXor: operator.pow,
    }

    # Opérateurs unaires autorisés
    _UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
    }

    # Fonctions autorisées
    _FUNCTIONS = {
        # Trigonométrie
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "degrees": math.degrees, "radians": math.radians,
        # Exponentielles et logarithmes
        "sqrt": math.sqrt, "exp": math.exp,
        "log": math.log, "log10": math.log10, "log2": math.log2,
        # Arrondis et troncature
        "floor": math.floor, "ceil": math.ceil, "trunc": math.trunc,
        "round": round, "abs": abs,
        # Statistiques
        "mean": statistics.mean, "median": statistics.median,
        "mode": statistics.mode, "stdev": statistics.stdev,
        "variance": statistics.variance,
        # Suites et combinatoires
        "factorial": math.factorial, "perm": math.perm, "comb": math.comb,
        "gcd": math.gcd, "lcm": math.lcm,
        # Divers
        "min": min, "max": max, "sum": sum, "pow": pow,
        # [v1.1] xor explicite (depuis que ^ = puissance) + fractions exactes
        "xor": operator.xor,
        "frac": Fraction,
    }

    # Constantes autorisées
    _CONSTANTS = {
        "pi": math.pi, "e": math.e, "tau": math.tau,
        "inf": math.inf, "nan": math.nan,
    }

    @classmethod
    def evaluate(cls, expression: str) -> Any:
        """Évalue une expression mathématique."""
        try:
            tree = ast.parse(expression, mode='eval')
            return cls._eval_node(tree.body)
        except Exception as e:
            return f"Erreur : {str(e)}"

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Any:
        """Évalue un nœud AST récursivement."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in cls._CONSTANTS:
                return cls._CONSTANTS[node.id]
            raise ValueError(f"Nom inconnu : {node.id}")
        elif isinstance(node, ast.BinOp):
            op = cls._BIN_OPS.get(type(node.op))
            if not op:
                raise ValueError(f"Opérateur non supporté : {type(node.op).__name__}")
            return op(cls._eval_node(node.left), cls._eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = cls._UNARY_OPS.get(type(node.op))
            if not op:
                raise ValueError(f"Opérateur unaire non supporté : {type(node.op).__name__}")
            return op(cls._eval_node(node.operand))
        elif isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            func = cls._FUNCTIONS.get(func_name)
            if not func:
                raise ValueError(f"Fonction non supportée : {func_name}")
            args = [cls._eval_node(arg) for arg in node.args]
            return func(*args)
        elif isinstance(node, ast.List):
            return [cls._eval_node(e) for e in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(cls._eval_node(e) for e in node.elts)
        else:
            raise ValueError(f"Nœud non supporté : {type(node).__name__}")


# ══════════════════════════════════════════════════════════════════════════════
# MOTEUR DE VÉRIFICATION MATHÉMATIQUE
# ══════════════════════════════════════════════════════════════════════════════


class MathVerifier:
    """
    Permet à l'IA de vérifier que le résultat d'un code Python
    correspond à un calcul mathématique.
    """

    @staticmethod
    def verify_expression(expression: str, expected_result: Union[int, float, str], tolerance: float = 1e-9) -> Dict[str, Any]:
        """Vérifie qu'une expression donne le bon résultat."""
        actual = SafeMathEvaluator.evaluate(expression)
        if isinstance(actual, str) and actual.startswith("Erreur"):
            return {"valid": False, "error": actual, "expression": expression}

        try:
            expected = float(expected_result)
            actual_float = float(actual)
            diff = abs(actual_float - expected)
            if diff <= tolerance:
                return {
                    "valid": True,
                    "expression": expression,
                    "actual": actual,
                    "expected": expected,
                    "diff": diff
                }
            else:
                return {
                    "valid": False,
                    "expression": expression,
                    "actual": actual,
                    "expected": expected,
                    "diff": diff,
                    "error": f"Écart trop grand : {diff}"
                }
        except ValueError:
            return {"valid": actual == expected_result, "actual": actual, "expected": expected_result}

    @staticmethod
    def verify_python_code(code: str, test_input: str = "", expected_output: str = "", timeout: int = 5) -> Dict[str, Any]:
        """
        [v1.1] Vérifie QU'UN code Python produit LA BONNE SORTIE.
        - Analyse syntaxique (AST)
        - Scan mots dangereux par frontières de mots ("opened" n'est plus flaggé)
        - Exécution réelle en sous-processus isolé (timeout, dossier jetable)
        - Comparaison de la sortie avec expected_output
        (v1.0 : exec avec __builtins__ vide → print/len/range n'existaient plus,
        donc TOUT code réaliste échouait, et expected_output était ignoré.)
        """
        # 1. Analyse syntaxique (vérifie que le code est valide)
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {"valid": False, "error": f"Erreur de syntaxe : {e}"}

        # 2. Vérification de sécurité (frontières de mots, pas de sous-chaînes)
        dangerous = ["eval", "exec", "system", "popen", "__import__", "open"]
        for word in dangerous:
            if re.search(r"\b" + re.escape(word) + r"\b", code):
                return {"valid": False, "error": f"Mot-clé dangereux détecté : {word}"}

        # 3. Exécution réelle en sous-processus isolé
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "candidate.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            try:
                proc = subprocess.run(
                    [sys.executable, path],
                    input=test_input,
                    capture_output=True, text=True, timeout=timeout, cwd=td,
                )
            except subprocess.TimeoutExpired:
                return {"valid": False, "error": f"Timeout : code > {timeout}s"}
            except Exception as e:
                return {"valid": False, "error": f"Erreur d'exécution : {e}"}

        # 4. Le code a-t-il planté ?
        if proc.returncode != 0:
            last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "?"
            return {"valid": False, "error": f"Crash (code {proc.returncode}) : {last}"}

        # 5. La sortie correspond-elle à l'attendu ?
        stdout = proc.stdout.strip()
        if expected_output and expected_output not in stdout:
            return {"valid": False, "executed": True, "stdout": stdout,
                    "expected": expected_output,
                    "error": "Sortie différente du résultat attendu"}
        return {"valid": True, "executed": True, "stdout": stdout,
                "message": "Code exécuté, sortie conforme"}


# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR DE CODE MATHÉMATIQUE
# ══════════════════════════════════════════════════════════════════════════════


# [v1.1] Remplacement SÛR par frontières de mots — plus de sous-chaînes !
# v1.0 : "e" cassait "math.exp" → "math.math.exp", "1e-9" → "1math.e-9",
#        "mean" → "mmath.ean". Le \b du regex ne touche ni les nombres (1e-9),
#        ni l'intérieur des mots, et (?<!\.) évite de re-qualifier "math.sqrt".
_RE_MATH_TOKENS = [
    "sinh", "cosh", "tanh", "asin", "acos", "atan", "degrees", "radians",
    "sqrt", "exp", "log10", "log2", "log", "sin", "cos", "tan",
    "floor", "ceil", "trunc",
    "mean", "median", "mode", "stdev", "variance",
    "pi", "tau", "e",
]
_RE_NS_STATS = {"mean", "median", "mode", "stdev", "variance"}
_RE_QUALIFY = re.compile(
    r"(?<!\.)\b(" + "|".join(sorted(set(_RE_MATH_TOKENS), key=len, reverse=True)) + r")\b"
)


class MathCodeGenerator:
    """
    Transforme un calcul ou une formule mathématique en code Python propre.
    """

    @staticmethod
    def generate_from_expression(expression: str) -> str:
        """Génère le code pour une expression mathématique. [v1.1] regex sûr."""
        py_expr = expression.replace("^", "**")  # ^ = puissance (aligné évaluateur v1.1)

        # [v1.1] Détection + qualification par frontières de mots
        found = _RE_QUALIFY.findall(py_expr)
        needs_math = any(t not in _RE_NS_STATS for t in found)
        needs_stats = any(t in _RE_NS_STATS for t in found)

        def _qualify(match):
            token = match.group(1)
            ns = "statistics" if token in _RE_NS_STATS else "math"
            return f"{ns}.{token}"

        py_expr = _RE_QUALIFY.sub(_qualify, py_expr)

        code = ""
        if needs_math:
            code += "import math\n"
        if needs_stats:
            code += "import statistics\n"
        if needs_math or needs_stats:
            code += "\n"

        code += f"# Formule : {expression}\n"
        code += f"resultat = {py_expr}\n"
        code += f"print(f'Résultat : {{resultat}}')\n"
        return code

    @staticmethod
    def generate_matrix_code(rows: int, cols: int, matrix: List[List[float]]) -> str:
        """Génère le code pour créer et manipuler une matrice."""
        code = f"""# Matrice {rows}x{cols}
import numpy as np

matrice = np.array({matrix})

print(f"Forme        : {{matrice.shape}}")
print(f"Somme        : {{matrice.sum()}}")
print(f"Moyenne      : {{matrice.mean()}}")
print(f"Transposée   :\\n{{matrice.T}}")
"""
        return code

    @staticmethod
    def generate_statistics_code(values: List[float]) -> str:
        """Génère le code pour analyser des statistiques."""
        code = f"""# Statistiques sur {len(values)} valeurs
import statistics

valeurs = {values}

moyenne    = statistics.mean(valeurs)
mediane    = statistics.median(valeurs)
ecart_type = statistics.stdev(valeurs) if len(valeurs) > 1 else 0
variance   = statistics.variance(valeurs) if len(valeurs) > 1 else 0
minimum    = min(valeurs)
maximum    = max(valeurs)

print(f"Moyenne    : {{moyenne}}")
print(f"Médiane    : {{mediane}}")
print(f"Écart-type : {{ecart_type}}")
print(f"Variance   : {{variance}}")
print(f"Min / Max  : {{minimum}} / {{maximum}}")
"""
        return code

    @staticmethod
    def generate_fibonacci_code(n: int) -> str:
        """Génère le code pour la suite de Fibonacci."""
        return f"""# Suite de Fibonacci ({n} termes)
def fibonacci(n):
    suite = [0, 1]
    for i in range(2, n):
        suite.append(suite[-1] + suite[-2])
    return suite[:n]

resultat = fibonacci({n})
print(f"F({{n}}) = {{resultat}}")
"""

    @staticmethod
    def generate_prime_code(n: int) -> str:
        """Génère le code pour les nombres premiers."""
        return f"""# Nombres premiers jusqu'à {n}
def est_premier(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

premiers = [i for i in range(2, {n} + 1) if est_premier(i)]
print(f"Premiers jusqu'à {n} : {{premiers}}")
print(f"Total : {{len(premiers)}} nombres premiers")
"""

    @staticmethod
    def generate_factorial_code(n: int) -> str:
        """Génère le code pour le factoriel."""
        return f"""# Factoriel de {n}
import math

resultat = math.factorial({n})
print(f"{n}! = {{resultat}}")
"""


# ══════════════════════════════════════════════════════════════════════════════
# OUTIL UNIFIÉ POUR L'IA (PROTON-CALC TOOL)
# ══════════════════════════════════════════════════════════════════════════════


class ProtonCalcTool:
    """
    L'outil ultime que l'IA peut appeler pour :
    - Calculer (avec une précision parfaite)
    - Vérifier (si son code est correct)
    - Générer (du code mathématique propre)
    """

    def __init__(self):
        self.evaluator = SafeMathEvaluator()
        self.verifier = MathVerifier()
        self.generator = MathCodeGenerator()

    @staticmethod
    def get_tool_schema() -> List[Dict]:
        """Schéma pour l'intégration dans une IA (OpenAI/Anthropic)."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calc_evaluate",
                    "description": "Évalue une expression mathématique avec une précision absolue. Exemples : 'sin(pi/2)', '2^10 + sqrt(16)', 'log(100)'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "L'expression à calculer"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calc_verify",
                    "description": "[v1.1] Vérifie une expression OU un code Python. Code multi-lignes : exécution en sous-processus isolé (timeout 5s), sortie comparée au résultat attendu.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "L'expression ou le code Python à vérifier"},
                            "expected_result": {"type": "string", "description": "Le résultat attendu"},
                            "test_input": {"type": "string", "description": "[v1.1] Entrée stdin optionnelle pour le code multi-lignes"}
                        },
                        "required": ["code", "expected_result"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calc_generate",
                    "description": "Génère du code Python à partir d'une expression mathématique.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "L'expression mathématique à convertir en code"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calc_statistics",
                    "description": "Génère le code d'analyse statistique pour une liste de valeurs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "values": {"type": "array", "items": {"type": "number"}, "description": "Liste de valeurs"}
                        },
                        "required": ["values"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calc_matrix",
                    "description": "Génère le code de manipulation d'une matrice.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rows": {"type": "integer", "default": 3},
                            "cols": {"type": "integer", "default": 3},
                            "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}
                        },
                        "required": ["matrix"]
                    }
                }
            }
        ]

    def execute_tool(self, name: str, args: Dict) -> Dict:
        """Exécute un outil par son nom."""
        if name == "calc_evaluate":
            expr = args.get("expression", "")
            result = SafeMathEvaluator.evaluate(expr)
            return {"expression": expr, "result": str(result)}
        elif name == "calc_verify":
            code = args.get("code", "")
            expected = args.get("expected_result", "")
            test_input = args.get("test_input", "")
            # [v1.1] Routage : vraie vérification de code si c'en est un
            if "\n" in code or "print" in code or "=" in code:
                return self.verifier.verify_python_code(code, test_input, expected)
            result = self.verifier.verify_expression(code, expected)
            return result
        elif name == "calc_generate":
            expr = args.get("expression", "")
            code = self.generator.generate_from_expression(expr)
            return {"code": code}
        elif name == "calc_statistics":
            values = args.get("values", [])
            code = self.generator.generate_statistics_code(values)
            return {"code": code}
        elif name == "calc_matrix":
            matrix = args.get("matrix", [[1, 2], [3, 4]])
            rows = len(matrix)
            cols = len(matrix[0]) if rows > 0 else 0
            code = self.generator.generate_matrix_code(rows, cols, matrix)
            return {"code": code}

        return {"error": f"Outil inconnu : {name}"}


# ══════════════════════════════════════════════════════════════════════════════
# DÉMO
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("⚛️ PROTON-CALC TOOL - Démo\n")

    # 1. Calculs
    print("1. Calculs mathématiques :")
    expr = "sqrt(16) + sin(pi/2) + log(100, 10)"
    res = SafeMathEvaluator.evaluate(expr)
    print(f"   {expr} = {res}")

    # 2. Génération de code
    print("\n2. Génération de code :")
    code = MathCodeGenerator.generate_from_expression(expr)
    print(code)

    # 3. Vérification
    print("3. Vérification :")
    print(f"   2 + 2 = 4 ? {MathVerifier.verify_expression('2 + 2', 4)}")
    print(f"   sin(pi/2) = 1 ? {MathVerifier.verify_expression('sin(pi/2)', 1)}")

    # 4. Statistiques
    print("\n4. Statistiques :")
    stats_code = MathCodeGenerator.generate_statistics_code([10, 20, 30, 40, 50])
    print(stats_code)

    # 5. [v1.1] Preuves du patch — exécution réelle, pas de promesse
    print("\n5. Preuves v1.1 (les 3 écarts corrigés) :")
    print(f"   2^10 = {SafeMathEvaluator.evaluate('2^10')}   (^ = puissance, aligné)")
    print(f"   xor(12, 10) = {SafeMathEvaluator.evaluate('xor(12, 10)')}   (xor explicite conservé)")
    code = MathCodeGenerator.generate_from_expression("exp(2)")
    ligne = [l for l in code.splitlines() if l.strip().startswith('resultat')][0].strip()
    print(f"   gen('exp(2)') ligne saine : {ligne}")
    r = MathVerifier.verify_python_code("print(42)", "", "999")
    print(f"   verify_code(print(42), attendu 999) -> valid={r['valid']}   (doit être False)")
    r = MathVerifier.verify_python_code("print(42)", "", "42")
    print(f"   verify_code(print(42), attendu 42)  -> valid={r['valid']}   (doit être True)")
    code = MathCodeGenerator.generate_from_expression("mean([10, 20, 30])")
    ligne = [l for l in code.splitlines() if l.strip().startswith('resultat')][0].strip()
    print(f"   gen('mean([10, 20, 30])') ligne saine : {ligne}")

