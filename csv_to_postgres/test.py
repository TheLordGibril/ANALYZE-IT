def test_encodage_fichier(fichier):
    try:
        with open(fichier, encoding='utf-8') as f:
            lignes = f.readlines()
        print("Fichier lu en UTF-8 sans erreur.")
    except UnicodeDecodeError as e:
        print("Erreur d'encodage détectée :", e)
        print("Essai avec encodage 'latin1'...")
        try:
            with open(fichier, encoding='latin1') as f:
                lignes = f.readlines()
            print("Fichier lu en latin1 sans erreur.")
        except Exception as e2:
            print("Erreur aussi avec latin1 :", e2)

if __name__ == "__main__":
    test_encodage_fichier('../etl/datasets/final_dataset.csv')
