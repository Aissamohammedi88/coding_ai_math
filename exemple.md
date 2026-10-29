 Évaluation Directe (Sécurisée par AST)
python

from proton_calc import SafeMathEvaluator

# Calcul de base
result = SafeMathEvaluator.evaluate("sqrt(16) + sin(pi/2) + log(100, 10)")
print(result) # 7.0

# Gestion des puissances
print(SafeMathEvaluator.evaluate("2^10")) # 1024

2. Génération de Code Propre
python

from proton_calc import MathCodeGenerator

code = MathCodeGenerator.generate_from_expression("exp(2) + mean([10, 20, 30])")
print(code)
# Résultat :
# import math
# import statistics
#
# # Formule : exp(2) + mean([10, 20, 30])
# resultat = math.exp(2) + statistics.mean([10, 20, 30])
# print(f'Résultat : {resultat}')

3. Vérification d'Exécution (Le vrai test)
python

from proton_calc import MathVerifier

# Le code est-il valide ET produit-il le bon résultat ?
check = MathVerifier.verify_python_code(
    code="print(10 * 5)", 
    expected_output="50"
)
print(check["valid"]) # True (Le code s'exécute sans erreur et la sortie correspond)

check_fail = MathVerifier.verify_python_code(
    code="print(10 * 5)", 
    expected_output="999"
)
print(check_fail["valid"]) # False (La sortie ne correspond pas)

🔌 Intégration avec un LLM (OpenAI / Anthropic)

L'outil expose un schéma JSON prêt à être utilisé dans une API de type tools ou functions :
python

from proton_calc import ProtonCalcTool

tool = ProtonCalcTool()
schema = tool.get_tool_schema() # À passer à votre API LLM

Si le LLM décide d'appeler calc_evaluate ou calc_verify, il suffit d'exécuter :
python

response = tool.execute_tool("calc_evaluate", {"expression": "2**10"})
print(response) # {"expression": "2**10", "result": "1024"}
