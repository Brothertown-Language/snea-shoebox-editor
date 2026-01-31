# Copyright (c) 2026 Brothertown Language
import solara

@solara.component
def Page():
    with solara.Column():
        solara.Title("SNEA Shoebox Editor")
        solara.Markdown("# SNEA Online Shoebox Editor")
        solara.Info("Welcome to the concurrent editor for SNEA linguistic records.")

@solara.component
def Layout(children):
    return solara.AppLayout(children=children)
