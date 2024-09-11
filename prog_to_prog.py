import subprocess

# Contenu du programme à écrire
program_code = """
def greet():
    print('Bonjour, ceci est un programme généré !')

greet()
"""

# Écrire le programme dans un fichier
with open('generated_program.py', 'w') as file:
    file.write(program_code)

# Exécuter le programme généré et capturer la sortie et les erreurs
result = subprocess.run(['python', 'generated_program.py'], capture_output=True, text=True)

# Vérifier si le programme a rencontré une erreur
if result.returncode != 0:
    print("Une erreur s'est produite lors de l'exécution du programme généré :")
    print(result.stderr)
else:
    print("Résultat de l'exécution du programme généré :")
    print(result.stdout)
