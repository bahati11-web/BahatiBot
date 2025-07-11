import os
import pywikibot
import language_tool_python
import re
import subprocess

# Charger la variable d'environnement BOT_PASSWORD
bot_password = os.getenv('BOT_PASSWORD')

# Configuration de Pywikibot
pywikibot.config.usernames['wikipedia']['fr'] = 'Bahatispam'
pywikibot.config.password_file = None
pywikibot.config.passwords = {
    ('wikipedia', 'fr', 'Bahatispam'): (bot_password, None),
}

site = pywikibot.Site('fr', 'wikipedia')

# Connexion sans demande interactive
try:
    site.login()
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

def corriger_syntaxe(text):
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'==\s*(.*?)\s*==', r'== \1 ==', text)
    return text

def lancer_wpcleaner(page_title):
    password = bot_password
    commande = [
        'java', '-jar', 'WPCleaner.jar',
        '-language', 'fr',
        '-user', 'Bahatispam',
        '-password', password,
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
