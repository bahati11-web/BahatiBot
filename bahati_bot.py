import os
import pywikibot
import language_tool_python
import re
import subprocess

# Récupérer le mot de passe dans la variable d'environnement
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
if not BOT_PASSWORD:
    print("Erreur : la variable d'environnement BOT_PASSWORD n'est pas définie.")
    exit(1)

# Config Pywikibot pour l'utilisateur et mot de passe
pywikibot.config.usernames['wikipedia']['fr'] = 'Bahatispam'
pywikibot.config.passwords = {
    ('wikipedia', 'fr', 'Bahatispam'): (BOT_PASSWORD, None),
}
pywikibot.config.password_file = None  # Ne pas utiliser de fichier password

site = pywikibot.Site('fr', 'wikipedia')

try:
    site.login()  # Connexion sans demander de mot de passe en console
    print(f"Connecté en tant que : {site.user()}")
except Exception as e:
    print(f"Erreur lors de la connexion : {e}")
    exit(1)

tool = language_tool_python.LanguageTool('fr-FR')

def corriger_orthographe(titre):
    page = pywikibot.Page(site, titre)
    if not page.exists():
        print(f"Page '{titre}' inexistante.")
        return
    original_text = page.text
    matches = tool.check(original_text)
    corrected_text = language_tool_python.utils.correct(original_text, matches)
    if corrected_text != original_text:
        page.text = corrected_text
        page.save("Correction automatique d'orthographe par BahatiBot")
        print(f"Modifications enregistrées pour la page : {titre}")
    else:
        print(f"Aucune correction nécessaire pour : {titre}")

def lancer_wpcleaner(page_title):
    commande = [
        'java', '-jar', 'WPCleaner.jar',
        '-language', 'fr',
        '-user', 'Bahatispam',
        '-password', BOT_PASSWORD,
        '-action', 'fix',
        '-page', page_title,
        '-config', 'config.properties'
    ]
    try:
        subprocess.run(commande, check=True)
        print(f"WPCleaner lancé avec succès sur : {page_title}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du lancement de WPCleaner sur {page_title} : {e}")

def traiter_modifications_recentes(nb=10):
    for change in site.recentchanges(namespaces=[0], total=nb, reverse=True):
        titre = change.get('title')
        print(f"Traitement de la page : {titre}")
        corriger_orthographe(titre)
        lancer_wpcleaner(titre)

if __name__ == "__main__":
    traiter_modifications_recentes(10)
