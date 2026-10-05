# vscode-custom-template
Visual Studio Code custom templates

Pour appliquer un thème choisi au hasard au workspace courant :

```sh
python3 scripts/random_settings.py
```

Le script crée `.vscode/settings.json` si nécessaire et ne remplace que la propriété
`workbench.colorCustomizations`, en conservant les autres réglages existants.
