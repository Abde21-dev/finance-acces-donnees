from datetime import date
import pandas as pd
import streamlit as st
import re

from acces_donnees import (
    ajouter_societe,
    lister_bilans,
    lister_cours,
    lister_societes,
    lire_societe,
    modifier_societe,
    supprimer_societe,
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

# ---------- Fonctions de validation des entrées ----------
def valider_champ_texte(valeur: str) -> bool:
    """Vérifie qu'un champ texte ne contient pas de balises HTML ou de caractères suspects."""
    if not valeur:
        return False
    # Interdit formellement les chevrons (< et >) souvent utilisés pour les injections
    if "<" in valeur or ">" in valeur:
        return False
    # Autorise lettres, chiffres, espaces et quelques ponctuations courantes
    pattern = r"^[\w\sàâäéèêëîïôöùûüçœæ\-\'\.\&\(\)]+$"
    return bool(re.match(pattern, valeur, re.UNICODE))

def valider_symbole_devise(valeur: str) -> bool:
    """Vérifie que le symbole boursier ou la devise est au bon format (lettres majuscules/chiffres)."""
    pattern = r"^[A-Z0-9]{1,10}$"
    return bool(valeur and re.match(pattern, valeur))

# ---------- Fonctions de formatage ----------
def montant(valeur, devise):
  texte = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
  return f"{texte} {devise}"


def nombre(valeur, decimales=2):
  return f"{valeur:.{decimales}f}".replace(".", ",")


# ---------- Barre latérale (Navigation & Mode) ----------
st.sidebar.header("🏢 Navigation & Gestion")

societes = lister_societes()

if not societes:
  st.warning("Aucune société trouvée dans la base de données.")
  mode = "📋 Vue d'ensemble de toutes les sociétés"
else:
  mode = st.sidebar.radio(
      "Mode d'affichage",
      [
          "Entreprise spécifique",
          "📋 Vue d'ensemble de toutes les sociétés",
      ],
  )

# ---------- VUE GLOBALE : TOUTES LES SOCIÉTÉS ----------
if mode == "📋 Vue d'ensemble de toutes les sociétés":
  st.title("📋 Vue d'ensemble de toutes les sociétés")
  st.markdown("---")

  if societes:
    data_all = []
    for s in societes:
      data_all.append({
          "ID": s.id,
          "Nom": s.nom,
          "Symbole": s.symbole_boursier,
          "Secteur": s.secteur_activite,
          "Pays": s.pays,
          "Devise": s.devise,
      })
    df_societes = pd.DataFrame(data_all)

    # Filtrer par secteur d'activité proprement
    secteurs_tous = sorted(list(set(df_societes["Secteur"])))
    filtre_secteur_global = st.selectbox(
        "Filtrer par secteur d'activité", ["Tous"] + secteurs_tous
    )

    if filtre_secteur_global != "Tous":
      df_societes = df_societes[
          df_societes["Secteur"] == filtre_secteur_global
      ]

    st.dataframe(df_societes, use_container_width=True, hide_index=True)
  else:
    st.info("Aucune donnée à afficher.")

  # Formulaire d'ajout sécurisé et filtré
  st.subheader("➕ Ajouter une nouvelle société")
  with st.form("form_ajout_global", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      n_nom = st.text_input("Nom de la société").strip()
      n_symbole = st.text_input("Symbole boursier (ex: AAPL)").strip().upper()
      n_secteur = st.text_input("Secteur d'activité").strip()
    with col2:
      n_pays = st.text_input("Pays", value="France").strip()
      n_devise = st.text_input("Devise (ex: EUR, USD)", value="EUR").strip().upper()

    submitted = st.form_submit_button("Enregistrer la société")
    if submitted:
      if not n_nom or not n_symbole or not n_secteur or not n_pays or not n_devise:
        st.error("⚠️ Tous les champs du formulaire doivent être remplis.")
      elif not valider_champ_texte(n_nom) or not valider_champ_texte(n_secteur) or not valider_champ_texte(n_pays):
        st.error("⚠️ Caractères non autorisés détectés (balises HTML ou symboles < et > interdits).")
      elif not valider_symbole_devise(n_symbole) or not valider_symbole_devise(n_devise):
        st.error("⚠️ Le symbole et la devise doivent contenir uniquement des lettres majuscules et des chiffres (max 10).")
      else:
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
          st.success(f"Société '{n_nom}' ajoutée avec succès !")
          st.rerun()
        except Exception:
          st.error(
              "Erreur lors de l'ajout (le symbole boursier existe peut-être"
              " déjà)."
          )

else:
  # ---------- MODE ENTREPRISE SPÉCIFIQUE ----------
  secteurs = sorted(list(set(s.secteur_activite for s in societes)))
  secteur_filtre = st.sidebar.selectbox("Filtrer par secteur", ["Tous"] + secteurs)

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

  # Action rapide dans la sidebar pour ajouter une société (avec filtrage/validation)
  with st.sidebar.expander("➕ Ajouter une société"):
    with st.form("form_ajout_rapide", clear_on_submit=True):
      n_nom = st.text_input("Nom").strip()
      n_symbole = st.text_input("Symbole (ex: AAPL)").strip().upper()
      n_secteur = st.text_input("Secteur").strip()
      n_pays = st.text_input("Pays", value="France").strip()
      n_devise = st.text_input("Devise", value="EUR").strip().upper()
      submitted = st.form_submit_button("Enregistrer")

      if submitted:
        if not n_nom or not n_symbole or not n_secteur or not n_pays or not n_devise:
          st.error("⚠️ Tous les champs sont obligatoires.")
        elif not valider_champ_texte(n_nom) or not valider_champ_texte(n_secteur) or not valider_champ_texte(n_pays):
          st.error("⚠️ Caractères non autorisés détectés.")
        elif not valider_symbole_devise(n_symbole) or not valider_symbole_devise(n_devise):
          st.error("⚠️ Format de symbole ou devise invalide.")
        else:
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
          except Exception:
            st.error("Erreur : Symbole déjà existant ou problème technique.")

  # ---------- Corps Principal (Entreprise Sélectionnée) ----------
  if societe_id:
    societe = lire_societe(societe_id)

    st.title(f"{societe.nom}")
    st.caption(
        f"**Symbole :** {societe.symbole_boursier} | **Secteur :**"
        f" {societe.secteur_activite} | **Pays :** {societe.pays} | **Devise :**"
        f" {societe.devise}"
    )

    # --- Section Modifier / Supprimer ---
    with st.expander("⚙️ Modifier ou Supprimer cette société"):
      with st.form("form_modification"):
        m_nom = st.text_input("Nom", value=societe.nom).strip()
        m_symbole = st.text_input("Symbole boursier", value=societe.symbole_boursier).strip().upper()
        m_secteur = st.text_input("Secteur d'activité", value=societe.secteur_activite).strip()
        m_pays = st.text_input("Pays", value=societe.pays).strip()
        m_devise = st.text_input("Devise", value=societe.devise).strip().upper()

        btn_modif = st.form_submit_button("Enregistrer les modifications")
        if btn_modif:
          if not m_nom or not m_symbole or not m_secteur or not m_pays or not m_devise:
            st.error("Tous les champs doivent être remplis.")
          elif not valider_champ_texte(m_nom) or not valider_champ_texte(m_secteur) or not valider_champ_texte(m_pays):
            st.error("⚠️ Caractères non autorisés détectés.")
          elif not valider_symbole_devise(m_symbole) or not valider_symbole_devise(m_devise):
            st.error("⚠️ Format de symbole ou devise invalide.")
          else:
            try:
              societe_maj = Societe(
                  id=societe.id,
                  nom=m_nom,
                  symbole_boursier=m_symbole,
                  secteur_activite=m_secteur,
                  pays=m_pays,
                  devise=m_devise,
              )
              modifier_societe(societe.id, societe_maj)
              st.success("Société mise à jour avec succès !")
              st.rerun()
            except Exception:
              st.error("Erreur lors de la mise à jour (conflit potentiel de symbole).")

      if st.button("🗑️ Supprimer cette société", type="primary"):
        try:
          supprimer_societe(societe.id)
          st.success("Société supprimée avec succès !")
          st.rerun()
        except Exception:
          st.error("Impossible de supprimer : des bilans ou données sont rattachés.")

    st.markdown("---")

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

        col1, col2, col3 = st.columns(3)

        with col1:
          try:
            marge = (
                marge_nette(dernier.resultat_net, dernier.chiffre_affaires) * 100
            )
            col1.metric("Marge Nette", f"{nombre(marge)} %")
          except CalculImpossible:
            col1.warning("Marge nette non calculable")

        with col2:
          try:
            liq = liquidite(dernier.actifs_courants, dernier.passifs_courants)
            col2.metric("Liquidité", nombre(liq))
          except CalculImpossible:
            col2.warning("Liquidité non calculable")

        with col3:
          try:
            endet = endettement(dernier.dettes_totales, dernier.capitaux_propres)
            col3.metric("Endettement", nombre(endet))
          except CalculImpossible:
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