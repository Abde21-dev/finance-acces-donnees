import {
  getSocietes, getSociete, ajouterSociete, getBilans, getCours, getIndicateurs,
} from "./api.js";

const FENETRE = 5;

const filtreSecteur = document.querySelector("#filtre-secteur");
const listeSocietes = document.querySelector("#liste-societes");
const formSociete = document.querySelector("#form-societe");
const messageForm = document.querySelector("#message-form");
const detailVide = document.querySelector("#detail-vide");
const detail = document.querySelector("#detail");

let societeActive = null;

// ---------- Mise en forme ----------

function montant(valeur, devise) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency", currency: devise, maximumFractionDigits: 0,
  }).format(Number(valeur));
}

function nombre(valeur, decimales = 2) {
  return Number(valeur).toLocaleString("fr-FR", {
    minimumFractionDigits: decimales, maximumFractionDigits: decimales,
  });
}

function dateFr(iso) {
  const [annee, mois, jour] = iso.split("-");
  return `${jour}/${mois}/${annee}`;
}

// Ajoute une cellule à une ligne. textContent : le texte n'est jamais interprété comme du HTML.
function cellule(ligne, texte, classe = "") {
  const td = document.createElement("td");
  td.textContent = texte;
  if (classe) td.className = classe;
  ligne.append(td);
}

// ---------- Liste des sociétés et filtre ----------

async function remplirSecteurs() {
  const societes = await getSocietes();
  const secteurs = [...new Set(societes.map((s) => s.secteur_activite))].sort();
  const choixActuel = filtreSecteur.value;
  filtreSecteur.replaceChildren(new Option("Tous les secteurs", ""));
  for (const secteur of secteurs) filtreSecteur.append(new Option(secteur, secteur));
  filtreSecteur.value = choixActuel;
}

async function afficherListe() {
  const societes = await getSocietes(filtreSecteur.value);
  listeSocietes.replaceChildren();
  for (const societe of societes) {
    const bouton = document.createElement("button");
    bouton.textContent = `${societe.nom} (${societe.symbole_boursier})`;
    bouton.classList.toggle("active", societe.id === societeActive);
    bouton.addEventListener("click", () => afficherDetail(societe.id));
    const li = document.createElement("li");
    li.append(bouton);
    listeSocietes.append(li);
  }
}

// ---------- Détail d'une société ----------

function afficherIndicateurs(ind) {
  document.querySelector("#detail-annee").textContent = ind.annee ? `de ${ind.annee}` : "";

  const valeurs = [
    ["#ind-marge", ind.marge_nette === null ? null : `${nombre(ind.marge_nette * 100)} %`],
    ["#ind-liquidite", ind.liquidite === null ? null : nombre(ind.liquidite)],
    ["#ind-endettement", ind.endettement === null ? null : nombre(ind.endettement)],
  ];
  for (const [selecteur, texte] of valeurs) {
    document.querySelector(selecteur).textContent = texte ?? "—";
  }

  const rendement = document.querySelector("#ind-rendement");
  if (ind.rendement === null) {
    rendement.textContent = "—";
    rendement.className = "";
  } else {
    rendement.textContent = `${ind.rendement >= 0 ? "+" : ""}${nombre(ind.rendement)} %`;
    rendement.className = ind.rendement < 0 ? "negatif" : "positif";
  }

  const listeErreurs = document.querySelector("#ind-erreurs");
  listeErreurs.replaceChildren();
  for (const message of Object.values(ind.erreurs)) {
    const li = document.createElement("li");
    li.textContent = message;
    listeErreurs.append(li);
  }
}

function afficherBilans(bilans, devise) {
  const corps = document.querySelector("#corps-bilans");
  corps.replaceChildren();
  for (const b of bilans) {
    const ligne = document.createElement("tr");
    cellule(ligne, b.annee);
    cellule(ligne, montant(b.chiffre_affaires, devise));
    cellule(ligne, montant(b.resultat_net, devise), Number(b.resultat_net) < 0 ? "negatif" : "");
    cellule(ligne, montant(b.actifs_courants, devise));
    cellule(ligne, montant(b.passifs_courants, devise));
    cellule(ligne, montant(b.dettes_totales, devise));
    cellule(ligne, montant(b.capitaux_propres, devise));
    cellule(ligne, montant(b.total_actifs, devise));
    corps.append(ligne);
  }
}

function afficherCours(cours, moyennes) {
  document.querySelector("#fenetre").textContent = FENETRE;
  const moyenneParDate = new Map(moyennes.map((m) => [m.date_cours, m.moyenne]));
  const corps = document.querySelector("#corps-cours");
  corps.replaceChildren();
  for (const c of cours) {
    const ligne = document.createElement("tr");
    cellule(ligne, dateFr(c.date_cours));
    cellule(ligne, nombre(c.cours_cloture));
    cellule(ligne, Number(c.volume_echange).toLocaleString("fr-FR"));
    const moyenne = moyenneParDate.get(c.date_cours);
    cellule(ligne, moyenne === undefined ? "—" : nombre(moyenne));
    corps.append(ligne);
  }
}

async function afficherDetail(id) {
  societeActive = id;
  afficherListe();
  try {
    const [societe, bilans, cours, indicateurs] = await Promise.all([
      getSociete(id), getBilans(id), getCours(id), getIndicateurs(id, FENETRE),
    ]);
    document.querySelector("#detail-nom").textContent = `${societe.nom} (${societe.symbole_boursier})`;
    document.querySelector("#detail-infos").textContent =
      `${societe.secteur_activite} · ${societe.pays} · ${societe.devise}`;
    afficherIndicateurs(indicateurs);
    afficherBilans(bilans, societe.devise);
    afficherCours(cours, indicateurs.moyenne_mobile);
    detailVide.hidden = true;
    detail.hidden = false;
  } catch (erreur) {
    detail.hidden = true;
    detailVide.hidden = false;
    detailVide.textContent = erreur.message;
  }
}

// ---------- Ajout d'une société ----------

formSociete.addEventListener("submit", async (evenement) => {
  evenement.preventDefault();
  const donnees = Object.fromEntries(
    [...new FormData(formSociete)].map(([cle, valeur]) => [cle, valeur.trim()]),
  );
  donnees.symbole_boursier = donnees.symbole_boursier.toUpperCase();
  donnees.devise = donnees.devise.toUpperCase();

  try {
    const societe = await ajouterSociete(donnees);
    messageForm.textContent = `Société ajoutée : ${societe.nom}.`;
    messageForm.className = "message succes";
    formSociete.reset();
    await remplirSecteurs();
    await afficherListe();
  } catch (erreur) {
    messageForm.textContent = erreur.message;
    messageForm.className = "message erreur";
  }
});

// ---------- Démarrage ----------

filtreSecteur.addEventListener("change", afficherListe);
await remplirSecteurs();
await afficherListe();