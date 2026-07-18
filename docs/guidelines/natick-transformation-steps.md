# Natick Record Transformation Steps

This document lists the discrete transformation stages performed by the `NatickProcessor` in `scripts/natick/process_natick_records.py`.

## Pipeline Execution Order

1. `parse_records`: Split source text into `NatickRecord` objects.
2. `convert_tabs_to_spaces`: Replace tabs with 4 spaces.
3. `discard_section_markers`: Remove `||a||`, `||ch||`, etc.
4. `remove_blank_lines`: Remove blank lines within records.
5. `discard_empty_records`: Discard records that contain no lines.
6. `strip_headword_indentation`: Strip leading spaces from the first line of each record.
7. `convert_lmm_to_lx`: Change `\lmm` on the first line to `\lx`.
8. `tag_pipe_enclosed_headwords`: Tag pipe-enclosed headwords as `\lx`.
9. `clean_headword_tags`: Move headword prefixes to `\nt`.
10. `validate_headwords_identified`: (Validation) Ensure all records start with `\lx`.
11. `identify_languages`: Add `\ln` based on marks like `(Narr.)`.
12. `tag_starred_wampanoag`: Tag `*` as `*Wampanoag [*wam]`.
13. `tag_unstarred_wampanoag`: Tag untagged as `Wampanoag [wam]`.
14. `move_prefix_symbols_to_nt`: Move `?`, `!`, `+` to `\nt`.
15. `add_source_tags`: Add `\so` from page markers.
16. `process_abn_abbreviations`: Western Abenaki [abe].
17. `process_alg_abbreviations`: Algonquian [alg].
18. `process_c_abbreviations`: Wampanoag [wam] (Cotton).
19. `process_cott_abbreviations`: Wampanoag [wam] (Cotton).
20. `process_cotton_abbreviations`: Wampanoag [wam] (Cotton).
21. `process_del_abbreviations`: Delaware [del].
22. `process_etch_abbreviations`: Etchemin [etc].
23. `process_ill_abbreviations`: Miami-Illinois [mia].
24. `process_illin_abbreviations`: Miami-Illinois [mia].
25. `process_mah_abbreviations`: Mahican [mjy].
26. `process_muh_abbreviations`: Mahican [mjy].
27. `process_micm_abbreviations`: Mi'kmaq [mic].
28. `process_menom_abbreviations`: Menominee [mez].
29. `process_men_abbreviations`: Menominee [mez].
30. `process_montagn_abbreviations`: Innu [moe].
31. `process_mnt_abbreviations`: Innu [moe].
32. `process_narr_abbreviations`: Narragansett [xnt].
33. `process_nipm_abbreviations`: Nipmuc [nip].
34. `process_ojib_abbreviations`: Ojibwe [oji].
35. `process_peq_abbreviations`: Mohegan-Pequot [mqm].
36. `process_moh_abbreviations`: Mohegan-Pequot [mqm].
37. `process_powh_abbreviations`: Powhatan [pim].
38. `process_quinnip_abbreviations`: Quiripi [qyp].
39. `process_quir_abbreviations`: Quiripi [qyp].
40. `process_shawn_abbreviations`: Shawnee [sjw].
41. `process_unqu_abbreviations`: Unquachog [unq].
42. `fix_ctg4adj_typo`: Correct `\ctg4Adj`.
43. `remove_ctg_digits`: Strip numbers from `\ctg`.
44. `replace_ctg_tags`: `\ctg` -> `\ps`.
45. `replace_cat_tags`: `\cat` -> `\ps`.
46. `replace_cg_tags`: `\cg` -> `\ps`.
47. `replace_ct_tags`: `\ct` -> `\ps`.
48. `remove_ls_digits`: Strip numbers from `\ls`.
49. `fix_ls_typos`: `\ls` -> `\gls`.
50. `add_homonym_numbers`: Add `\hm` to duplicates.
51. `remove_stars_from_headwords`: Remove `*` if `\ln` exists.
52. `convert_cross_references`: "See |...|" -> `\cf`.
53. `convert_cf_cross_references`: "Cf. |...|" -> `\cf`.
54. `process_abn_abbreviations`: (Repeat)
55. `process_alg_abbreviations`: (Repeat)
56. `process_c_abbreviations`: (Repeat)
57. `process_cott_abbreviations`: (Repeat)
58. `process_cotton_abbreviations`: (Repeat)
59. `process_del_abbreviations`: (Repeat)
60. `process_etch_abbreviations`: (Repeat)
61. `process_ill_abbreviations`: (Repeat)
62. `process_illin_abbreviations`: (Repeat)
63. `process_mah_abbreviations`: (Repeat)
64. `process_muh_abbreviations`: (Repeat)
65. `process_micm_abbreviations`: (Repeat)
66. `process_menom_abbreviations`: (Repeat)
67. `process_men_abbreviations`: (Repeat)
68. `process_montagn_abbreviations`: (Repeat)
69. `process_mnt_abbreviations`: (Repeat)
70. `process_narr_abbreviations`: (Repeat)
71. `process_nipm_abbreviations`: (Repeat)
72. `process_ojib_abbreviations`: (Repeat)
73. `process_peq_abbreviations`: (Repeat)
74. `process_moh_abbreviations`: (Repeat)
75. `process_powh_abbreviations`: (Repeat)
76. `process_quinnip_abbreviations`: (Repeat)
77. `process_quir_abbreviations`: (Repeat)
78. `process_shawn_abbreviations`: (Repeat)
79. `process_unqu_abbreviations`: (Repeat)
80. `process_cree_abbreviations`: Tag 'Cree' as language.
81. `extract_complex_example_sentences`: Extract `|native| 'gloss' source {analysis}`.
82. `extract_example_sentences`: Extract `\xv`, `\xe`, `\so`.
83. `extract_source_analysis`: Analysis -> `\ng`.
84. `process_cng_tags`: Handle changed form/reduplication.
85. `process_suppositive_entries`: Handle "Suppos. of...".
86. `replace_standard_drv_tags`: `\drv` -> `\dv`.
87. `replace_prefixed_drv_tags`: `+drv` -> `\dv`.
88. `replace_midline_drv_tags`: Mid-line `\drv` -> `\dv`.
89: `replace_bracketed_drv_tags`: `\drv[` -> `\dv [`.
90. `convert_from_to_dv`: "From |...|" -> `\dv`.
91. `fix_lm_typos`: `\lm` -> `\lmm`.
92. `fix_mm_typos`: `\mm` -> `\lmm`.
93. `convert_lmm_tagged_to_se`: `\lmm` -> `\se` (tagged).
94. `convert_lmm_indented_to_se`: `\lmm` -> `\se` (indented).
95. `convert_lmm_indented_prefixed_to_se`: `\lmm` -> `\se` (indented/prefixed).
96. `convert_lmm_bang_lemma_to_se`: `!` lemma -> `\se`.
97. `convert_lmm_plus_lemma_to_se`: `+` lemma -> `\se`.
98. `convert_lmm_star_lemma_to_se`: `*` lemma -> `\se`.
99. `convert_lmm_variants_to_se`: Variants -> `\se`.
100. `convert_lmm_standard_to_se`: Standard -> `\se`.
101. `convert_lmm_remaining_to_se`: Remaining -> `\se`.
102. `convert_subentries_to_ge`: Subentry gloss -> `\ge`.
103. `convert_subentries_to_so`: Subentry source -> `\so`.
104. `fix_gls_double_typos`: Correct `\gls\gls`.
105. `remove_gls_digits`: Strip numbers from `\gls`.
106. `update_gloss_tags`: `\gls` -> `\ge`.
107. `remove_src_digits`: Strip numbers from `\src`.
108. `update_source_tags`: `\src` -> `\so`.
109. `convert_rfr_tags`: `\rfr` -> `\nt`.
110. `fix_double_etm_tags`: Correct `\etm\etm`.
111. `convert_etm_to_et`: `\etm` -> `\et`.
112. `fix_cmy_typos`: `\cmy` -> `\cmt`.
113. `remove_cmt_digits`: Strip numbers from `\cmt`.
114. `convert_cmt_to_nt`: `\cmt` -> `\nt`.
115. `convert_rmk_to_nt`: `\rmk` -> `\nt Remark:`.
116. `convert_frh_to_nt`: `\frh` -> `\nt Research needed:`.
117. `convert_iou_to_nt`: `\iou` -> `\nt Follow up needed:`.
118. `convert_dlt_to_nt`: `\dlt` -> `\nt DLT:`.
119. `convert_mn_tags`: `\mn` -> `\nt MN:`.
120. `convert_gl_to_ge`: `\gl` -> `\ge`.
121. `convert_gs_to_ge`: `\gs` -> `\ge`.
122. `convert_pzl_to_nt_puzzle`: `\pzl` -> `\nt Puzzle:`.
123. `convert_rem_to_nt_remark`: `\rem` -> `\nt Remark:`.
124. `convert_rml_to_nt_lemma_remark`: `\rml` -> `\nt Lemma remark:`.
125. `convert_rv_to_nt_review`: `\rv` -> `\nt To review:`.
126. `convert_sc_to_so`: `\sc` -> `\so`.
127. `convert_spl_to_va`: `\spl` -> `\va`.
128. `convert_t_to_ps`: `\t` -> `\ps`.
129. `tg_to_ps`: `\tg` -> `\ps`.
130. `normalize_headword_tags`: All headwords -> `\lx`.
131. `remove_control_characters`: Strip non-printing chars.
132. `extract_variant_lexemes`: Extract variants/comments from headwords.
133. `process_subentry_variants`: Extract variants from subentries.
134. `transform_comparative_blocks`: Transform `[...]` blocks.
135. `transform_standalone_lexemes`: Convert `|...|` to comparative blocks.
136. `remove_all_leading_whitespace`: FINAL: Flush left.
137. `check_mdf_compliance`: FINAL: Verify MDF tags.
138. `save_records`: Write to file.
