from datetime import date
import pandas as pd
import streamlit as st

from acces_donnees import (
    ajouter_societe,
    lister_bilans,
    lister_cours,
    lister_societes,
    lire_societe,
)
from indicateurs import (
    CalculImpossible,
    endettement,
    liquidite,
    marge_nette,
    moyenne_mobile,
    rendement,
)
from modeles import Societe

# Configuration globale de la page (mode large pour bien respirer)
st.set_page_config(
    page_title="Analyse Financière & Boursière", page_icon="📈", layout="wide"
)

# Masquer les éléments natifs de Streamlit pour un rendu plus "sur mesure"
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    </style>
""",
    unsafe_allow_html=True,
)


# ---------- Fonctions de formatage ----------
def montant(valeur, devise):
  texte = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
  return f"{texte} {devise}"


def nombre(valeur, decimales=2):
  return f"{valeur:.{decimales}f}".replace(".", ",")


# ---------- Barre latérale (Navigation & Filtres) ----------
st.sidebar.header("🏢 Gestion des Sociétés")

societes = lister_societes()

if not societes:
  st.error("Aucune société trouvée dans la base de données.")
else:
  # Optionnel : Filtrer par secteur d'activité proprement
  secteurs = sorted(list(set(s.secteur_activite for s in societes)))
  secteur_filtre = st.sidebar.selectbox(
      "Filtrer par secteur", ["Tous"] + secteurs
  )

  if secteur_filtre != "Tous":
    societes_filtrees = [
        s for s in societes if s.secteur_activite == secteur_filtre
    ]
  else:
    societes_filtrees = societes

  options_societes = {s.nom: s.id for s in societes_filtrees}

  if not options_societes:
    st.sidebar.warning("Aucune société pour ce secteur.")
    societe_id = None
  else:
    nom_selectionne = st.sidebar.selectbox(
        "Sélectionner une entreprise", list(options_societes.keys())
    )
    societe_id = options_societes[nom_selectionne]

  st.sidebar.divider()

  # Action rapide dans la sidebar pour ajouter une société
  with st.sidebar.expander("➕ Ajouter une société"):
    with st.form("form_ajout_rapide", clear_on_submit=True):
      n_nom = st.text_input("Nom")
      n_symbole = st.text_input("Symbole (ex: AAPL)")
      n_secteur = st.text_input("Secteur")
      n_pays = st.text_input("Pays", value="France")
      n_devise = st.text_input("Devise", value="EUR")
      submitted = st.form_submit_button("Enregistrer")

      if submitted:
        if n_nom and n_symbole:
          try:
            nouvelle_soc = Societe(
                id=None,
                nom=n_nom,
                symbole_boursier=n_symbole,
                secteur_activite=n_secteur,
                pays=n_pays,
                devise=n_devise,
            )
            ajouter_societe(nouvelle_soc)
            st.success(f"'{n_nom}' ajoutée !")
            st.rerun()
          except Exception as ex:
            st.error(f"Erreur : {ex}")
        else:
          st.error("Nom et symbole obligatoires.")

  # ---------- Corps Principal ----------
  if societe_id:
    societe = lire_societe(societe_id)

    # En-tête de la page claire et moderne
    st.title(f"{societe.nom}")
    st.caption(
        f"**Symbole :** {societe.symbole_boursier} | **Secteur :**"
        f" {societe.secteur_activite} | **Pays :** {societe.pays} | **Devise :**"
        f" {societe.devise}"
    )

    st.markdown("---")

    # Utilisation d'onglets pour structurer l'information sans surcharger l'écran
    tab_indicateurs, tab_cours, tab_bilans = st.tabs([
        "📊 Indicateurs Clés",
        "📈 Cours & Moyenne Mobile",
        "📁 Historique des Bilans",
    ])

    bilans = lister_bilans(societe.id)

    # --- ONGLET 1 : INDICATEURS ---
    with tab_indicateurs:
      if not bilans:
        st.info("Aucun bilan disponible pour calculer les indicateurs.")
      else:
        dernier = bilans[-1]
        st.subheader(f"Synthèse financière de l'année {dernier.annee}")

        # Affichage sous forme de cartes métriques claires
        col1, col2, col3 = st.columns(3)

        with col1:
          try:
            marge = (
                marge_nette(dernier.resultat_net, dernier.chiffre_affaires) * 100
            )
            col1.metric("Marge Nette", f"{nombre(marge)} %")
          except CalculImpossible as e:
            col1.warning(f"Marge nette non calculable")

        with col2:
          try:
            liq = liquidite(dernier.actifs_courants, dernier.passifs_courants)
            col2.metric("Liquidité", nombre(liq))
          except CalculImpossible as e:
            col2.warning("Liquidité non calculable")

        with col3:
          try:
            endet = endettement(dernier.dettes_totales, dernier.capitaux_propres)
            col3.metric("Endettement", nombre(endet))
          except CalculImpossible as e:
            col3.warning("Endettement non calculable")

        st.markdown("")
        st.info(
            "💡 **Rappel :** Les indicateurs sont calculés automatiquement à"
            f" partir du dernier exercice comptable clos ({dernier.annee})."
        )

    # --- ONGLET 2 : COURS & MOYENNE MOBILE ---
    with tab_cours:
      st.subheader("Évolution boursière et tendance")

      col_p1, col_p2, col_p3 = st.columns(3)
      date_debut = col_p1.date_input("Du", value=date(2000, 1, 1))
      date_fin = col_p2.date_input("Au", value=date.today())
      fenetre = col_p3.slider(
          "Fenêtre de moyenne mobile (jours)", min_value=2, max_value=30, value=5
      )

      cours = lister_cours(societe.id, date_debut, date_fin)

      if not cours:
        st.info("Aucun cours boursier enregistré sur cette période.")
      else:
        df_cours = pd.DataFrame([
            {"Date": c.date_cours, "Cours Clôture": float(c.cours_cloture)}
            for c in cours
        ])
        df_cours.set_index("Date", inplace=True)

        valeurs_cloture = [c.cours_cloture for c in cours]
        try:
          moyennes = moyenne_mobile(valeurs_cloture, fenetre)
          jours_mm = [c.date_cours for c in cours[fenetre - 1 :]]
          df_mm = pd.DataFrame(
              {
                  "Date": jours_mm,
                  f"Moyenne Mobile ({fenetre}j)": [float(m) for m in moyennes],
              }
          )
          df_mm.set_index("Date", inplace=True)
          df_graph = df_cours.join(df_mm)
        except CalculImpossible:
          df_graph = df_cours

        # Affichage propre du graphique
        st.line_chart(df_graph, use_container_width=True)

        if len(cours) >= 2:
          avant, apres = cours[-2], cours[-1]
          try:
            rend = rendement(avant.cours_cloture, apres.cours_cloture)
            st.metric(
                f"Dernier rendement (au {apres.date_cours:%d/%m/%Y})",
                f"{rend:+.2f} %".replace(".", ","),
            )
          except CalculImpossible:
            pass

    # --- ONGLET 3 : BILANS ---
    with tab_bilans:
      st.subheader("Détail comptable pluriannuel")
      if not bilans:
        st.info("Aucun bilan enregistré.")
      else:
        data_bilans = []
        for b in bilans:
          data_bilans.append({
              "Année": b.annee,
              "Chiffre d'affaires": montant(b.chiffre_affaires, societe.devise),
              "Résultat net": montant(b.resultat_net, societe.devise),
              "Actifs courants": montant(b.actifs_courants, societe.devise),
              "Passifs courants": montant(b.passifs_courants, societe.devise),
              "Dettes totales": montant(b.dettes_totales, societe.devise),
              "Capitaux propres": montant(b.capitaux_propres, societe.devise),
          })
        st.dataframe(
            pd.DataFrame(data_bilans), use_container_width=True, hide_index=True
        )