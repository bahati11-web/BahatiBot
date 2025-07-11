import pywikibot
import language_tool_python
import re
import subprocess
import os

# Initialisation
site = pywikibot.Site()
site.login()  # Connexion via user-password.py
print(f"✅ Connecté en tant que : {site.user()}")

tool = language_tool_python.LanguageTool('fr-FR')

def corriger_orthographe(titre):
    """Corrige l’orthographe d’une page si nécessaire."""
    page = pywikibot.Page(site, titre)
    if not page.exists():
        print(f"⚠️ Page inexistante : {titre}")
        return

    original_text = page.text
    matches = tool.check(original_text)
    corrected_text = language_tool_python.utils.correct(original_text, matches)

    if corrected_text != original_text:
        page.text = corrected_text
        try:
            page.save("Correction automatique d'orthographe par BahatiBot")
            print(f"✅ Modifications enregistrées pour : {titre}")
        except Exception as e:
            print(f"❌ Erreur lors de l’enregistrement de {titre} : {e}")
    else:
        print(f"✅ Aucune correction nécessaire pour : {titre}")

def corriger_syntaxe(text):
    """Corrige des erreurs de mise en forme courantes."""
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'==\s*(.*?)\s*==', r'== \1 ==', text)
    return text

def lancer_wpcleaner(page_title):
    """Lance WPCleaner sur une page spécifique."""
    password = os.environ.get('BOT_PASSWORD')
    if not password:
        print("❌ Mot de passe non trouvé dans la variable BOT_PASSWORD.")
        return

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
        print(f"✅ WPCleaner lancé sur : {page_title}")
    except subprocess.CalledProcessError as e:
        print(f"❌ WPCleaner a échoué pour {page_title} : {e}")

def traiter_modifications_recentes(nb=10):
    """Traite les dernières pages modifiées sur le wiki."""
    print(f"🔍 Traitement des {nb} dernières modifications...")
    for change in site.recentchanges(namespaces=[0], total=nb, reverse=True):
        titre = change.get('title')
        print(f"\n➡️ Page : {titre}")
        corriger_orthographe(titre)
        lancer_wpcleaner(titre)

if __name__ == "__main__":
    traiter_modifications_recentes(10)
