// Couche d'accès aux données du front.
// TEMPORAIRE : les fonctions renvoient des données fictives au format de la future API.
// Quand l'API FastAPI sera prête, seul ce fichier changera (appels fetch).

const SOCIETES = [
  { id: 1, nom: "Solaria Énergie",   symbole_boursier: "SOLR", secteur_activite: "Énergie",     pays: "France",   devise: "EUR" },
  { id: 2, nom: "Nordia Banque",     symbole_boursier: "NRDB", secteur_activite: "Finance",     pays: "Belgique", devise: "EUR" },
  { id: 3, nom: "Medivita Santé",    symbole_boursier: "MDVT", secteur_activite: "Santé",       pays: "Suisse",   devise: "EUR" },
  { id: 4, nom: "Pixelwave Studios", symbole_boursier: "PXLW", secteur_activite: "Technologie", pays: "Canada",   devise: "EUR" },
];

// [année, CA, résultat net, actifs courants, passifs courants, dettes totales, capitaux propres, total actifs]
const BILANS = {
  1: [[2023, 1200000000, 85000000, 420000000, 310000000, 980000000, 720000000, 1700000000],
      [2024, 1310000000, 97000000, 455000000, 330000000, 1010000000, 790000000, 1800000000],
      [2025, 1275000000, 64000000, 440000000, 345000000, 1050000000, 830000000, 1880000000]],
  2: [[2023, 540000000, 72000000, 2100000000, 1850000000, 3900000000, 600000000, 4500000000],
      [2024, 575000000, 81000000, 2250000000, 1980000000, 4100000000, 650000000, 4750000000],
      [2025, 590000000, 78000000, 2300000000, 2050000000, 4200000000, 700000000, 4900000000]],
  3: [[2023, 210000000, 18500000, 95000000, 60000000, 140000000, 180000000, 320000000],
      [2024, 198000000, -24000000, 82000000, 71000000, 165000000, 155000000, 320000000],
      [2025, 226000000, 9500000, 90000000, 66000000, 160000000, 170000000, 330000000]],
  4: [[2023, 48000000, -6200000, 31000000, 12000000, 18000000, 42000000, 60000000],
      [2024, 67000000, 4100000, 38000000, 14500000, 21000000, 47000000, 68000000],
      [2025, 89000000, 11300000, 49000000, 17000000, 24000000, 58000000, 82000000]],
};

const DATES = ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13",
               "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"];

const COURS = {
  1: { prix: [42.10, 42.85, 41.90, 43.20, 43.75, 43.10, 44.05, 44.60, 43.95, 45.10],
       volumes: [1215000, 1340000, 1580000, 1420000, 1190000, 1265000, 1480000, 1525000, 1310000, 1690000] },
  2: { prix: [18.40, 18.25, 18.70, 18.95, 18.60, 18.80, 19.15, 19.05, 19.40, 19.30],
       volumes: [812000, 765000, 904000, 958000, 721000, 786000, 990000, 845000, 1035000, 878000] },
  3: { prix: [65.20, 63.80, 64.50, 62.90, 61.75, 62.40, 63.10, 64.25, 63.60, 64.90],
       volumes: [298000, 412000, 336000, 455000, 507000, 361000, 324000, 389000, 301000, 347000] },
  4: { prix: [7.12, 7.45, 7.38, 7.80, 8.05, 7.92, 8.30, 8.15, 8.62, 8.48],
       volumes: [2050000, 2380000, 1960000, 2710000, 3020000, 2240000, 2890000, 2105000, 3340000, 2570000] },
};

// Simule le délai d'une vraie requête réseau et renvoie une copie des données
function reponse(valeur) {
  return new Promise((resoudre) => setTimeout(() => resoudre(structuredClone(valeur)), 150));
}

export async function getSocietes(secteur = "") {
  const liste = secteur ? SOCIETES.filter((s) => s.secteur_activite === secteur) : SOCIETES;
  return reponse([...liste].sort((a, b) => a.nom.localeCompare(b.nom)));
}

export async function getSociete(id) {
  const societe = SOCIETES.find((s) => s.id === id);
  if (!societe) throw new Error(`Aucune société avec l'identifiant ${id}.`);
  return reponse(societe);
}

export async function ajouterSociete(societe) {
  if (SOCIETES.some((s) => s.symbole_boursier === societe.symbole_boursier)) {
    throw new Error(`Le symbole ${societe.symbole_boursier} est déjà utilisé.`);
  }
  const nouvelle = { id: Math.max(...SOCIETES.map((s) => s.id)) + 1, ...societe };
  SOCIETES.push(nouvelle);
  return reponse(nouvelle);
}

export async function getBilans(id) {
  const lignes = BILANS[id] ?? [];
  return reponse(lignes.map(([annee, ca, rn, ac, pc, dt, cp, ta]) => ({
    annee,
    chiffre_affaires: ca,
    resultat_net: rn,
    actifs_courants: ac,
    passifs_courants: pc,
    dettes_totales: dt,
    capitaux_propres: cp,
    total_actifs: ta,
  })));
}

export async function getCours(id, debut = "0000-01-01", fin = "9999-12-31") {
  const cours = COURS[id];
  if (!cours) return reponse([]);
  const lignes = DATES.map((date_cours, i) => ({
    date_cours,
    cours_cloture: cours.prix[i],
    volume_echange: cours.volumes[i],
  }));
  return reponse(lignes.filter((c) => c.date_cours >= debut && c.date_cours <= fin));
}

// FICTIF : plus tard, l'API renverra ces résultats calculés par indicateurs.py
export async function getIndicateurs(id, fenetre = 5) {
  const bilans = await getBilans(id);
  const cours = await getCours(id);
  const resultat = {
    annee: null, marge_nette: null, liquidite: null, endettement: null,
    rendement: null, moyenne_mobile: [], erreurs: {},
  };

  const dernier = bilans.at(-1);
  if (!dernier) {
    resultat.erreurs.bilan = "Aucun bilan enregistré pour cette société.";
  } else {
    resultat.annee = dernier.annee;
    if (dernier.chiffre_affaires === 0) resultat.erreurs.marge_nette = "Marge nette impossible : chiffre d'affaires nul.";
    else resultat.marge_nette = dernier.resultat_net / dernier.chiffre_affaires;

    if (dernier.passifs_courants === 0) resultat.erreurs.liquidite = "Liquidité impossible : passifs courants nuls.";
    else resultat.liquidite = dernier.actifs_courants / dernier.passifs_courants;

    if (dernier.capitaux_propres <= 0) resultat.erreurs.endettement = "Endettement non significatif : capitaux propres nuls ou négatifs.";
    else resultat.endettement = dernier.dettes_totales / dernier.capitaux_propres;
  }

  if (cours.length < 2) {
    resultat.erreurs.rendement = "Rendement impossible : moins de deux cours enregistrés.";
  } else {
    const [avant, apres] = cours.slice(-2).map((c) => c.cours_cloture);
    resultat.rendement = (apres - avant) / avant * 100;
  }

  if (cours.length < fenetre) {
    resultat.erreurs.moyenne_mobile = `Moyenne mobile impossible : ${cours.length} cours disponibles pour une fenêtre de ${fenetre} jours.`;
  } else {
    for (let i = fenetre - 1; i < cours.length; i++) {
      const tranche = cours.slice(i - fenetre + 1, i + 1);
      const somme = tranche.reduce((total, c) => total + c.cours_cloture, 0);
      resultat.moyenne_mobile.push({ date_cours: cours[i].date_cours, moyenne: somme / fenetre });
    }
  }
  return resultat;
}