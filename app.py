import pandas as pd
import streamlit as st

def trier_par_poids(df, colonne_poids):
    try:
        df[colonne_poids] = df[colonne_poids].astype(float)
    except ValueError as e:
        raise ValueError(f"Erreur lors de la conversion des poids en float. Vérifiez vos données.") from e
    liste_eleves = df.to_records(index=False)
    liste_tries = sorted(liste_eleves, key=lambda x: x[colonne_poids])
    df_trie = pd.DataFrame.from_records(liste_tries, columns=df.columns)
    return df_trie

def creer_groupes(df, mixte=True, ecart_max_poids=10, taille_groupe=4):
    # Trier par poids
    df = trier_par_poids(df, 'Poids')

    # Si non mixte, séparer par sexe
    if not mixte:
        filles = df[df['Sexe'] == 'F']
        garcons = df[df['Sexe'] == 'M']
        groupes = []
        
        # Créer des groupes pour chaque sexe
        for groupe in [filles, garcons]:
            groupes += creer_sous_groupes(groupe, taille_groupe, ecart_max_poids)
    else:
        groupes = creer_sous_groupes(df, taille_groupe, ecart_max_poids)

    return groupes

def creer_sous_groupes(df, taille_groupe, ecart_max_poids):
    groupes = []
    groupe = []

    for _, eleve in df.iterrows():
        if len(groupe) < taille_groupe:
            if not groupe or abs(eleve['Poids'] - groupe[0]['Poids']) <= ecart_max_poids:
                groupe.append(eleve)
            else:
                groupes.append(pd.DataFrame(groupe))
                groupe = [eleve]
        else:
            groupes.append(pd.DataFrame(groupe))
            groupe = [eleve]
    
    if groupe:
        groupes.append(pd.DataFrame(groupe))
    
    return groupes

# Streamlit interface
st.title("Création de Groupes d'Elèves")

# Téléchargement du fichier CSV
uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

if uploaded_file:
    # Afficher le contenu du fichier CSV
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        st.write("Voici les données importées :")
        st.dataframe(df)
        
        # Vérifier si le fichier est vide
        if df.empty:
            st.error("Le fichier est vide ou mal formaté.")
        
        # Options
        mixte = st.checkbox("Groupes mixtes", value=True)
        ecart_max_poids = st.slider("Écart maximal de poids", min_value=1, max_value=50, value=10)
        taille_groupe = st.slider("Taille du groupe", min_value=2, max_value=10, value=4)

        if st.button("Créer les groupes"):
            groupes = creer_groupes(df, mixte, ecart_max_poids, taille_groupe)
            
            # Afficher les résultats
            st.write(f"**Groupes créés** (taille de groupe : {taille_groupe}, écart max poids : {ecart_max_poids}kg):")
            for i, groupe in enumerate(groupes):
                st.write(f"Groupe {i+1}:")
                st.dataframe(groupe[['Prénom', 'Sexe', 'Poids']])
                
            # Sauvegarder les résultats dans un fichier CSV
            output = uploaded_file.name.replace('.csv', '_groupes.csv')
            with open(output, 'w') as f:
                f.write('Groupe;Prénom;Sexe;Poids\n')
                for i, groupe in enumerate(groupes):
                    for _, eleve in groupe.iterrows():
                        f.write(f"{i+1};{eleve['Prénom']};{eleve['Sexe']};{eleve['Poids']}\n")
            
            # Permettre de télécharger le fichier des groupes
            st.download_button(
                label="Télécharger les groupes",
                data=open(output, 'rb'),
                file_name=output,
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
