### Selected Examples of Comparative Blocks for Analysis

These examples are extracted from `tmp/mdf_compliance_report.txt` and represent various combinations of single-language and multi-language comparative linguistic data.

#### Single-Language Blocks

**Example 1: Simple Entry (Western Abenaki)**
```text
[Western Abenaki [abe] |8d8`kanar| `son frère cadet'.]
```

**MDF Recommendation:**
```text
\lf Western Abenaki [abe]
\lv 8d8`kanar
\ln son frère cadet
```

**Example 2: Multiple Lexemes (Western Abenaki)**
```text
[Western Abenaki [abe] |tsamak8| `aiguille pour faire des nattes ou des raquettes'; |tsañkkañdi| `aiguille françoise'.]
```

**MDF Recommendation:**
```text
\lf Western Abenaki [abe]
\lv tsamak8
\le aiguille pour faire des nattes ou des raquettes
\lv tsañkkañdi
\le aiguille françoise
```
*(Note: Using \le or \ln depends on if the gloss is considered National/Regional or just English translation in context. For French in Abenaki records, \ln is often appropriate.)*

**Example 3: Reference with Metadata (Western Abenaki)**
```text
[Western Abenaki [abe] |arikkañn.| `D'une odeur forte, comme pourri, &c.'    R.364/495a.]
```

**MDF Recommendation:**
```text
\lf Western Abenaki [abe]
\lv arikkañn.
\le D'une odeur forte, comme pourri, &c.
\rf R.364/495a.
```

#### Multi-Language Blocks

**Example 4: Narragansett & Cree**
```text
[Narragansett [xnt] |Auchaûi.| `Hee is gone to hunt or fowle.', |Ntauchâumen.| `I goe afowling or hunting.'; |Auchaûtuck.| `Let us hunt.', |Nowetauchaûmen.| `I will hunt with you.'    R.W.88,164; 164.
Cree |ach|, `he is active, diligent'.]
```

**MDF Recommendation:**
```text
\lf Narragansett [xnt]
\lv Auchaûi.
\le Hee is gone to hunt or fowle.
\lv Ntauchâumen.
\le I goe afowling or hunting.
\lv Auchaûtuck.
\le Let us hunt.
\lv Nowetauchaûmen.
\le I will hunt with you.
\rf R.W.88,164; 164.
\lf Cree
\lv ach
\le he is active, diligent
```

**Example 5: Three Languages (Narragansett, Cree, Delaware)**
```text
[Narragansett [xnt] |ayátche| `as often as'
Cree |it-tússu-uk| `they are so many'; |hè it-túsechick| `as many as they are'
Delaware [del] |endchi| `so much as, as many'; |endchen| `so often as'    Zeisb.]
```

**MDF Recommendation:**
```text
\lf Narragansett [xnt]
\lv ayátche
\le as often as
\lf Cree
\lv it-tússu-uk
\le they are so many
\lv hè it-túsechick
\le as many as they are
\lf Delaware [del]
\lv endchi
\le so much as, as many
\lv endchen
\le so often as
\rf Zeisb.
```

**Example 6: Cree & Western Abenaki**
```text
[Cree |káht-ow| `he hides it'; |káht-tayoo| `he hides him'.
Western Abenaki [abe] |nekañda8añ|, |nekañ8ta8añ| `je le lui cache'; |nekañd8n| `je cache cela'.]
```

**MDF Recommendation:**
```text
\lf Cree
\lv káht-ow
\le he hides it
\lv káht-tayoo
\le he hides him
\lf Western Abenaki [abe]
\lv nekañda8añ
\ln je le lui cache
\lv nekañ8ta8añ
\ln je le lui cache
\lv nekañd8n
\ln je cache cela
```

**Example 7: Extensive Multi-Language (5+ sources)**
```text
[Algonquian [alg] |ATIS,o| `être mûr (en parlant des fruits), être teint (en parlant des étoffes', |Atiten minan| `les bluets sont mûrs'    Cq.69a.
Cree |Utitä'o| or |utitä'wun| `It is ripe, it is dyed, it is tanned'    Frs.497a.
Miami-Illinois [mia] |atete8i, atete8ara| `fruits murs'    M.82/83a.
Delaware [del] |@`tíhte∙w| II `it is ripe'; |atíhteew| II, |atúsuw| AI `be ripe'    G.1982.26, no.69; O'M.43b.
Nask. |atiihtaaw| II `it is ripe (fruit or berries)', |atiihtaapiyuw| AI `the berries (anim) change colour'    McK&J.1.28b.
Sh. |hatte| `it is ripe'    D.-V.429.]
```

**MDF Recommendation:**
```text
\lf Algonquian [alg]
\lv ATIS,o
\le être mûr (en parlant des fruits), être teint (en parlant des étoffes
\lv Atiten minan
\le les bluets sont mûrs
\rf Cq.69a.
\lf Cree
\lv Utitä'o
\lv utitä'wun
\le It is ripe, it is dyed, it is tanned
\rf Frs.497a.
\lf Miami-Illinois [mia]
\lv atete8i
\lv atete8ara
\le fruits murs
\rf M.82/83a.
\lf Delaware [del]
\lv @`tíhte∙w
\le II `it is ripe'
\lv atíhteew
\le II
\lv atúsuw
\le AI `be ripe'
\rf G.1982.26, no.69; O'M.43b.
\lf Nask.
\lv atiihtaaw
\le II `it is ripe (fruit or berries)'
\lv atiihtaapiyuw
\le AI `the berries (anim) change colour'
\rf McK&J.1.28b.
\lf Sh.
\lv hatte
\le it is ripe
\rf D.-V.429.
```
*(Note: Complex glosses or partial lexeme indicators like II/AI are preserved in \le for linguistic clarity.)*

**Example 8: Large Geographic Spread (Abenaki, Alg, Cree, Ojibwe, etc.)**
```text
[Western Abenaki [abe] |Éida8i8i| v. |épemai8i| `au bout, aux 2 bouts de q^q^ ch.'    R.P12/552b.
Algonquian [alg] |EITA| `de chaque côté, des deux côtés'    Cq.98b.
Cree +|AYITAW| (ad.) `des deux côtés, des deux bords'; |aye'tow| `At both ends'    Lac.D.328b-329a; Frs.67a.
EOjib. |eye∙yi∙tuwaye?i∙| `at both sides, at both ends', |eye∙yi∙tuwinikk| `on both arms'    B.1957.240b.
Miami-Illinois [mia] |Eita8agame| `des deux costés de la riviere', |Eita8i8ntchi| `des deux costés'    Grv.149/113a.
M.-P. |ehetuwiw| P `on both sides'    LeS.17a.]
```

**MDF Recommendation (with POS Parsing):**
```text
\lf Western Abenaki [abe]
\lv Éida8i8i
\lv épemai8i
\le au bout, aux 2 bouts de q^q^ ch.
\rf R.P12/552b.
\lf Algonquian [alg]
\lv EITA
\le de chaque côté, des deux côtés
\rf Cq.98b.
\lf Cree
\lv AYITAW
\ps adv
\le des deux côtés, des deux bords
\lv aye'tow
\le At both ends
\rf Lac.D.328b-329a; Frs.67a.
\lf EOjib.
\lv eye∙yi∙tuwaye?i∙
\le at both sides, at both ends
\lv eye∙yi∙tuwinikk
\le on both arms
\rf B.1957.240b.
\lf Miami-Illinois [mia]
\lv Eita8agame
\le des deux costés de la riviere
\lv Eita8i8ntchi
\le des deux costés
\rf Grv.149/113a.
\lf M.-P.
\lv ehetuwiw
\ps p
\le on both sides
\rf LeS.17a.
```

#### Blocks with Citation/Reference Logic

**Example 9: Citation at Start (Narragansett)**
```text
[Narragansett [xnt] |Kuttattaúamish aûke| `I would buy land of you.'    R.W.157/r.165.]
```

**MDF Recommendation:**
```text
\lf Narragansett [xnt]
\lv Kuttattaúamish aûke
\le I would buy land of you.
\rf R.W.157/r.165.
```

**Example 10: Referencing Modern Authorities (with POS Terms)**
```text
[Western Abenaki [abe] |atíé|, |atíak| `chien'    R.112/413a; |atié|    A.114.
WAbn. |adia| `A dog'    Lrnt.35; Day "obsolescent".]
```

**MDF Recommendation (with POS Parsing):**
```text
\lf Western Abenaki [abe]
\lv atíé
\lv atíak
\ln chien
\rf R.112/413a; A.114.
\lf WAbn.
\lv adia
\ps n
\le A dog
\rf Lrnt.35; Day "obsolescent".
```

**Example 11: Multiple Dialects/Notes (with POS Terms)**
```text
[Narragansett [xnt] |Aquíe| `Leave off or doe not.'; |Aquie assókish| `Be not foolish.'    R.W.39;41.√
Quiripi [qyp] |matta eakquino| `it ceaseth not'    Pier.15.40.]
```

**MDF Recommendation (with POS Parsing):**
```text
\lf Narragansett [xnt]
\lv Aquíe
\le Leave off or doe not.
\lv Aquie assókish
\le Be not foolish.
\rf R.W.39;41.
\lf Quiripi [qyp]
\lv matta eakquino
\ps v
\le it ceaseth not
\rf Pier.15.40.
```
*(Note: terms like v.i., v.t., n., adj., etc., can be parsed into \ps.)*
