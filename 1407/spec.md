> **Full spec and artifacts: [`1407/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1407/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1407/` — implementation plan, card catalogue, dependency contracts, research, designs, audit findings

# [SPEC] Restore Enter-key search triggering in Records search box

## Intent and Executive Summary

**Problem Statement:** Dans la page Records, appuyer sur Entrée dans la boîte de recherche ne déclenche plus la recherche ; seul le bouton 🔍 fonctionne.

**Root Cause / Motivation:** Le commit 907843d (correctif du champ d'effacement) a introduit une clé de widget suffixée `search_query_input_{_search_input_key}` et a fait perdre, collatéralement, l'attachement `on_change=on_search_change` du text_input. La callback `on_search_change` a survécu mais lit désormais une clé obsolète et non-suffixée — code mort.

**Approach Chosen:** Corriger `on_search_change` pour lire dynamiquement la clé suffixée courante (commit de `search_query`, reset de `current_page` à 1), ré-attacher `on_change` au text_input, et reworder le placeholder — en laissant intact le chemin du bouton 🔍.

**Alternatives Considered & Why Discarded:** Réintroduire l'ancien pattern diff+rerun (écrire la valeur du widget puis `st.rerun()`) — rejeté : Streamlit interdit à une callback d'écrire dans sa propre clé de widget (APIException), et la contrainte de l'issue l'exclut explicitement.

**Key Design Decisions:** La callback effectue un commit pur d'état (lecture dynamique du suffixe, écriture de `search_query` et `current_page`, sans rerun explicite) — compromis : conforme à la convention des widgets frères de la page, au prix de ne pas reproduire le pattern des boutons.

**User Intent / Original Prompt:** « Wire Enter key to execute the search in the Records sidebar text_input » — restaurer le comportement d'avant la régression.

## Not Included

- **Synchronisation URL/query-params** — aucune n'existe dans records.py aujourd'hui ; hors périmètre.
- **Debounce, autocomplete, gestion IME** — aucun changement demandé.
- **Modes de recherche, pagination, seuil sémantique** — inchangés ; la callback est agnostique au mode.
- **Couche service / données de production** — aucune modification (C-1).

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | Appuyer Entrée dans le text_input de recherche déclenche la recherche : `search_query` est commité depuis la clé suffixée courante et `current_page` est réinitialisé à 1 | behavioral | Playwright live-browser (standard of record, docs/development/ui_testing_standard.md) + AppTest in-process pour le wiring |
| SC-2 | Après un effacement (❌), appuyer Entrée ne re-commite aucune requête obsolète : l'état vide persiste | behavioral | Playwright — effacer puis Entrée, vérifier absence de re-search |
| SC-3 | Le clic sur 🔍 produit exactement un commit de la requête, comportement identique à avant le changement | behavioral | Playwright — clic bouton, un seul déclenchement ; AppTest garde-fou de régression |
| SC-4 | Le placeholder n'instruit plus d'utiliser Entrée, et la suite pytest passe sans régression (sélecteur E2E mis à jour dans le même cycle) | behavioral | Playwright rendu du placeholder + run complet de la suite pytest |

## Requirements

1. R-1. Le text_input de recherche SHALL déclencher la recherche quand l'utilisateur appuie sur Entrée (callback `on_change` attachée).
2. R-2. La callback `on_search_change` SHALL lire la valeur via la clé suffixée dynamique `search_query_input_{st.session_state.get('_search_input_key', 0)}`.
3. R-3. Le chemin Entrée SHALL commiter la requête exactement comme le bouton 🔍 : écriture de `search_query`, reset de `current_page` à 1 — sans travail d'URL.
4. R-4. La callback SHALL uniquement écrire l'état backing (`search_query`, `current_page`) — elle SHALL NOT écrire dans sa propre clé de widget.
5. R-5. Le système SHALL NOT réintroduire le pattern diff+rerun dans la callback.
6. R-6. Le placeholder SHALL utiliser une formulation neutre, sans instruction Entrée.
7. R-7. Après un effacement (incrément du compteur `_search_input_key`), la callback SHALL lire le suffixe courant — aucune requête obsolète ne SHALL être committée.
8. R-8. Le déclenchement SHALL fonctionner dans tous les modes de recherche (Headword, Gloss, Lexeme, FTS, Semantic Gloss, Semantic All).
9. R-9. Le sélecteur E2E couplé à l'aria-label du placeholder SHALL être mis à jour dans le même cycle que R-6.
10. R-10. Les chaînes de requête (caractères Unicode IPA, diacritiques) SHALL transiter sans normalisation ni altération.

## Items

### Item 1 (SC-1): Entrée exécute la recherche (ré-attachement + lecture suffixée)

- RED: AppTest in-process — assert que le text_input porte `on_change` et que le déclenchement committe `search_query` + reset de page (échoue avant le changement)
- GREEN: `on_search_change` corrigée (lecture dynamique suffixée, reset de page) + `on_change=on_search_change` sur le text_input
- verify: Playwright live-browser — taper une requête, Entrée, résultats filtrés rendus (captures sous tmp/1407/artifacts/)
- commit: un cycle RED→GREEN→COMMIT

### Item 2 (SC-2): Pas de re-search parasite après effacement

- RED: AppTest séquence effacer-puis-Entrée — assert que l'état vide persiste (échoue si lecture obsolète)
- GREEN: couvert par la lecture dynamique du suffixe de l'item 1 ; le test garde l'interaction
- verify: Playwright — effacer puis confirmer absence de re-search
- commit: un cycle RED→GREEN→COMMIT (dépend de l'item 1)

### Item 3 (SC-3): Chemin bouton 🔍 inchangé — pas de double commit

- RED: AppTest clic-bouton épinglant le comportement actuel à un seul commit (garde-fou : le test existe et passe avant ET après)
- GREEN: vérifier l'absence de delta comportemental sur le chemin bouton
- verify: Playwright — le clic bouton exécute la recherche exactement une fois
- commit: un cycle RED→GREEN→COMMIT (ordonné après l'item 1 pour contexte de vérification)

### Item 4 (SC-4): Placeholder neutre + zéro régression

- RED: assertion string — placeholder ≠ « Enter text... » (échoue avant le changement)
- GREEN: formulation neutre (ex. « Search... ») + mise à jour du sélecteur aria-label du test E2E dans le même cycle
- verify: Playwright rendu du placeholder ; run complet de la suite pytest
- commit: un cycle RED→GREEN→COMMIT

## Dependencies

- **docs/development/ui_testing_standard.md** — standard of record pour toute preuve user-visible ; à lire avant l'implémentation. Statut : satisfait (document existant).
- **docs/lessons-learned/** — contraintes Unicode/normalisation linguistique applicables (R-10). Statut : satisfait.
- **src/frontend/pages/records.py** — surface unique de changement. Statut : existant.
- **test/ui/test_semantic_search_ui_flow_e2e.py** — couplage sélecteur/aria-label (R-9). Statut : existant.

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1 | Phase 1 |
| R-2 | SC-1 | Phase 1 |
| R-3 | SC-1, SC-3 | Phase 1 |
| R-4 | SC-1 | Phase 1 |
| R-5 | SC-1 | Phase 1 |
| R-6 | SC-4 | Phase 1 |
| R-7 | SC-2 | Phase 1 |
| R-8 | SC-1, SC-2, SC-3 | Phase 1 |
| R-9 | SC-4 | Phase 1 |
| R-10 | SC-1, SC-2, SC-3 | Phase 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|-------------|
| records.py (page Records) | code | src/frontend/pages/records.py | Lecture directe (callback morte, clé suffixée, chemins bouton/effacement) |
| Historique git 83d7420 / 907843d | code/history | git show | Lecture des diffs confirmant la régression |
| Standard UI testing | doc | docs/development/ui_testing_standard.md | Lecture directe |
| AGENTS.md (contraintes linguistiques) | doc | AGENTS.md | Lecture directe |
| Test E2E couplé | code | test/ui/test_semantic_search_ui_flow_e2e.py | Grep du sélecteur aria-label |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

- **SC-1:** Vérifier le wiring Entrée via AppTest + Playwright coûte un cycle de test — le défaut autrement ne se découvre qu'à l'usage, quand l'utilisateur tape Entrée et que rien ne se passe. Sauter la vérification coûte une régression UX invisible en CI — la confiance dans la fonctionnalité s'effondre.
- **SC-2:** Vérifier la séquence effacement-puis-Entrée coûte un scénario de test — sauter laisse un bug de requête obsolète qui réapparaît dès qu'un utilisateur efface puis recherche. La correction a posteriori coûte plus cher que le test.
- **SC-3:** Épingler le comportement du bouton coûte un garde-fou de régression — sauter, et un double-commit ou un changement silencieux du bouton passe inaperçu jusqu'au signalement utilisateur.
- **SC-4:** Vérifier placeholder + suite complète coûte un run pytest et une capture Playwright — sauter, et le sélecteur E2E cassé fait échouer la suite pour tout le monde. La correction est l'unique métrique.

## Edge Cases

- **Entrée sur champ vide** — Condition : l'utilisateur appuie sur Entrée sans rien saisir. Comportement attendu : commit d'une chaîne vide (identique au bouton 🔍 avec champ vide), pas d'exception.
- **Entrée après effacement** — Condition : compteur `_search_input_key` incrémenté, widget recréé vide. Comportement attendu : la callback lit le suffixe courant, aucune requête obsolète n'est committée.
- **Blur sans Entrée** — Condition : l'utilisateur quitte le champ sans Entrée après modification. Comportement attendu : `on_change` se déclenche aussi au blur — même sémantique que le commit bouton, acceptable et cohérent.
- **Caractères Unicode / IPA** — Condition : requête contenant ə, ʃ, tʃ, diacritiques, ∞. Comportement attendu : transmission verbatim, aucune normalisation.
- **Clic 🔍 immédiat après Entrée** — Condition : les deux chemins écrivent `search_query`. Comportement attendu : écritures idempotentes (même valeur), état final identique, pas de double rerun parasite.
- **Échec de l'app live en E2E** — Condition : SNEA_E2E non défini ou app absente du :8501. Comportement attendu : les tests E2E skippent par design — jamais comptés comme PASS.

<!-- SPDX-FileCopyrightText: 2026 Michael Conrad -->
<!-- SPDX-License-Identifier: MIT -->
<!-- Provenance: AI-generated -->

*Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)*
