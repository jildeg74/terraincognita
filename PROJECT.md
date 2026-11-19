# Terra Incognita — dossier du projet

Ce document permet à n'importe qui (le propriétaire, une IA de n'importe quelle entreprise, un programmeur, un technicien) de reprendre le projet sans rien savoir de son histoire. Les règles de mise à jour du contenu sont dans `AGENT.md`, la contribution dans `CONTRIBUTING.md`. Ce fichier-ci explique **le pourquoi, le comment et où tout se trouve**.

> Tenir ce document à jour à chaque changement important (section « Journal » en bas).

---

## 1. Ce qu'est le projet

**Terra Incognita** (https://terraincognita.ca) est une carte vivante de ce que l'humanité ne sait pas encore : les grandes questions scientifiques ouvertes de tous les domaines, reliées entre elles. Pour chaque question : ce qu'on sait, ce qui bloque, les pistes actuelles, des sous-questions de recherche, les sources (avec leur type), et à quel point on est proche d'une réponse.

- **Public visé** : toute la planète (étudiants, enseignants, journalistes, chercheurs, curieux, financeurs).
- **Éditeur** : Juvason, entreprise basée à Montréal (Canada). Contact public : contact@juvason.com.
- **Né le** 18 novembre 2026, conçu et construit avec Claude (Anthropic).

## 2. Principes non négociables

1. **Rien de faux, rien d'inventé.** Chaque affirmation vient d'une source réellement ouverte et lue. Dans le doute, on ne change rien.
2. **Vérification indépendante.** Tout lot de changements est revérifié par un second agent (ou une personne) qui ne l'a pas écrit, avant publication.
3. **Mondial.** Pensé pour 8 milliards de personnes, pas pour un pays. Sept langues : en, fr, zh, es, hi, ar, pt.
4. **Indépendant.** Le projet ne dépend d'aucune IA, entreprise ou personne. Tout ce qu'il faut pour continuer est dans ce dépôt.
5. **Vie privée du propriétaire.** Aucun nom personnel, adresse personnelle ou donnée personnelle sur le site ni dans le dépôt. Le nom « Juvason », la ville (Montréal, Canada) et contact@juvason.com peuvent apparaître. Le nom d'utilisateur GitHub est visible sur GitHub seulement, jamais sur le site.
6. **Pas de publicité, pas de cookies de suivi, pas de comptes utilisateurs.**

## 3. État au 18 novembre 2026

- 100 questions, 7 domaines (Physique & cosmos, Vie & médecine, Esprit & cerveau, Mathématiques, IA, Terre & climat, Humanité).
- 99/100 avec au moins une étude relue par des pairs ou une référence académique (la seule exception : coût énergétique de l'IA, où il n'existe encore que des prépublications).
- 273 sous-questions, toutes en 7 langues.
- ~715 pages : la carte, une page par question et par langue, une liste et une page « À propos » par langue.
- Aucune question encore relue par un spécialiste humain.
- Points encore à vérifier : `OPEN_ISSUES.md`.

## 4. Architecture technique

```
data/questions/<id>.json   une question = un fichier (SOURCE DE VÉRITÉ)
data/changes/<date>.json   journal daté des changements
data/digests/<mois>.json   bilan mensuel « Ce qui a bougé ce mois-ci »
page/index.html            modèle de la carte (canvas, panneau, formulaires)
tools/validate.py          contrôle les données (langues, sources, liens…)
tools/build_site.py        construit site/ depuis data/ + page/
tools/build_pages.py       pages par question, liste, à propos (×7 langues)
tools/strings.json         textes des pages générées, 7 langues
tools/og.png               image d'aperçu des liens partagés (1200×630)
tools/logo/                logo (SVG source + PNG 32, 180, 512, 1024) : points reliés, un point en pointillé doré = l'inconnu
site/                      site public généré (ne pas éditer à la main)
.github/workflows/build.yml  valide + reconstruit site/ à chaque push
```

- **Construire** : `python3 tools/validate.py` puis `python3 tools/build_site.py page/index.html data/questions data/changes site data/digests` (Python 3 + Node.js nécessaires).
- La carte charge seulement la langue du visiteur (`site/q/<lang>.json`) ; `site/data.json` contient tout (téléchargeable, CC BY 4.0).
- Statut d'une question `n` : 0 horizon lointain, 1 pistes sérieuses, 2 percée en vue, **3 résolue** (avec `"solved": "AAAA-MM-JJ"`). Une question résolue n'est jamais supprimée : elle reste sur la carte comme « territoire conquis ».
- Licences : données et textes CC BY 4.0, code MIT (`LICENSE`). Citation : `CITATION.cff`.

## 5. Services et comptes

| Service | Rôle | Détails |
|---|---|---|
| GitHub | Dépôt (source de vérité) + contrôle automatique | `jildeg74/terraincognita`, branche `main` |
| Netlify | Hébergement, HTTPS, formulaires | Équipe JUVASON, **plan payant** depuis le 18/11/2026. Projet `dainty-frangipane-ab7989`. Publie `site/` à chaque push sur `main`. Domaine principal : terraincognita.ca (www redirige). Certificat Let's Encrypt automatique. |
| GoDaddy | Nom de domaine terraincognita.ca | Acheté le 18/11/2026 pour **2 ans → renouveler avant novembre 2028**. DNS : A `@` → 75.2.60.5 ; CNAME `www` → dainty-frangipane-ab7989.netlify.app |
| Netlify Forms | Formulaires « propose » (questions, corrections, relecteurs) et « newsletter » | Détection activée ; chaque envoi arrive par courriel à contact@juvason.com |
| Claude (Anthropic) | Veille hebdomadaire automatique | Tâche planifiée « Veille Terra Incognita », chaque **lundi 6 h 37 (heure de Toronto)**, rapport en français. Elle suit `AGENT.md`. Peut être remplacée par n'importe quel autre agent ou humain. |
| Google Search Console | Indexation Google, pays des visiteurs | Propriété « Domaine » terraincognita.ca, sitemap `https://terraincognita.ca/sitemap.xml` |
| Zenodo | Archive à vie + DOI pour citer les données | Relié au dépôt ; créer une release GitHub (v1.1, v2.0…) pour archiver une nouvelle version, par exemple une fois par an ou après un gros changement |

**Leçon apprise (18/11/2026)** : sur Netlify, chaque publication consomme des crédits. Une douzaine de petites publications le même jour a épuisé le plan gratuit et bloqué les mises à jour. **Regrouper les changements en un seul envoi** ; en régime normal, seule la veille du lundi publie (~4-5 fois par mois).

## 6. Fonctionnement courant

- **Chaque semaine** : la veille revérifie ~25 questions (un quart de la carte), règle d'abord `OPEN_ISSUES.md`, met à jour textes et sources dans les 7 langues, fait vérifier par un second agent indépendant, valide, construit, publie, et envoie un rapport.
- **Début de chaque mois** : bilan mensuel dans `data/digests/`, et jusqu'à 5 nouvelles questions (règles dans `AGENT.md`, « Growing the map ») : environ 160 questions après un an.
- **Messages du public** : arrivent à contact@juvason.com via Netlify. Les propositions sérieuses sont traitées comme une mise à jour normale (source obligatoire).
- **Ajouter une question** : voir `AGENT.md` (question réellement ouverte, reconnue dans la littérature, au moins une étude ou référence, 7 langues, liens dans les deux sens).
- **Ajouter une langue** : ajouter la langue dans `UI` et `LANGS` (page/index.html), dans `tools/strings.json`, dans `LANGS` de `tools/build_pages.py` et `tools/validate.py`, puis traduire toutes les questions et sous-questions, avec vérification. Décision du 18/11/2026 : ne pas ajouter de langue tant que les visiteurs ne le demandent pas (voir les pays dans Search Console). Ordre envisagé : russe, puis bengali et indonésien, idéalement avec un relecteur humain.

## 7. Décisions prises et pourquoi

- **Un projet mondial et utile, pas local** : demande explicite du propriétaire.
- **7 langues** : grande partie de l'humanité couverte (dont 5 langues officielles de l'ONU), tout en restant vérifiable. Hindi et arabe : les plus difficiles à contrôler → relecteurs humains souhaités.
- **Site statique** (pas de base de données ni de comptes) : rapide, peu coûteux, robuste, facile à reprendre.
- **GitHub comme source de vérité** plutôt qu'un service lié à une IA : indépendance.
- **Netlify payant** plutôt que changer d'hébergeur : garde les formulaires sans rien refaire.
- **Une page par question** : liens partageables et visibilité dans Google.
- **Chargement d'une seule langue** : page d'accueil ~4× plus légère pour les connexions lentes.

## 8. À faire / pistes

- [x] Google Search Console : propriété « Domaine » terraincognita.ca validée (via GoDaddy), sitemap envoyé le 18/11/2026.
- [x] Zenodo relié à GitHub le 18/11/2026 : chaque « release » GitHub est archivée avec un DOI (v1.0 publiée le 18/11/2026). DOI : 10.5281/zenodo.24356516 (https://doi.org/10.5281/zenodo.24356516).
- [ ] Choisir un outil d'envoi du bilan mensuel par courriel (les adresses sont collectées dans Netlify > Forms > newsletter) — avant début décembre 2026.
- [ ] Recruter des chercheurs relecteurs par domaine (affichés « Relu par » avec leur institution).
- [ ] Revenus envisagés : subventions (science ouverte), accès aux données/API pour organisations, rapports sur mesure.
- [ ] Plus tard : agents « chercheurs » qui proposent de nouvelles questions, toujours avec vérification.

## 9. Journal

- **2026-11-19** — Points ouverts réglés (12 sur 13) : 16 fiches corrigées en 7 langues (connectome, régénération, cellule virtuelle, énergie sombre, climat, productivité, sources de matière-antimatière, nourrir 10 milliards, dispersion humaine, addiction, intelligence-bio, 5 problèmes Clay). Chiffre « zettaoctet » retiré, traductions ar/hi de l'énergie sombre corrigées. Vérifié par un agent indépendant (16/16 acceptées). Reste ouvert : coût énergétique de l'IA, et 3 points relevés pendant la vérification (voir `OPEN_ISSUES.md`).
- **2026-11-18** — Logo « points reliés » (icône d'onglet, écran d'accueil, profils de réseaux sociaux).
- **2026-11-18** — Rubrique « Pourquoi c'est important » ajoutée aux 100 questions (7 langues), rédigée par 4 agents, vérifiée par 4 vérificateurs indépendants (54 acceptées telles quelles, 46 corrigées, 0 rejetée).
- **2026-11-18** — Lisible par les IA : `llms.txt` à la racine, données structurées schema.org (Dataset sur l'accueil, WebPage + Question + citations sur chaque page).
- **2026-11-18** — Règle de croissance : jusqu'à 5 nouvelles questions par mois, vérifiées.
- **2026-11-18** — Version v1.0 archivée sur Zenodo, DOI 10.5281/zenodo.24356516. Search Console validé, sitemap envoyé.
- **2026-11-18** — Création. 100 questions en 7 langues, site en ligne sur terraincognita.ca. Rattrapage par 4 agents + 4 vérificateurs indépendants : études relues ajoutées (39 → 99/100), 273 sous-questions, une dizaine d'affirmations corrigées ou retirées. Dépôt GitHub devenu source de vérité, règles `AGENT.md`, contrôle automatique. Pages par question, liste, à propos, éditeur Juvason. Formulaires Netlify activés (→ contact@juvason.com). Plan Netlify payant après épuisement des crédits gratuits. Questions résolues, image d'aperçu, chargement par langue, historique par question.
