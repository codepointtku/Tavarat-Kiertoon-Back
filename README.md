# Tavarat-Kiertoon-Back

Backend for City of Turku Tavarat Kiertoon internal recycling platform.

## Formatting

Make sure you have the VSCode extension called Python

Open VSCode settings with ctrl + , and then search "python":

"Python › Linting: Pylint Enabled" **ticked**

"Python › Formatting: Provider" **black**

Or alternatively add the following settings into settings.json, which you can open with ctrl + shift + p, then search "open settings":

```json
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
```

Formatting hotkey: `shift + alt + f`

Import sorting hotkey: `shift + alt + o`

### Formatting on save

Open VSCode settings and configure these settings:

"Editor: Default Formatter" **Python**

"Editor: Format On Save" **ticked**

Do note that if you switch between languages you also have to change the default formatter and you don't get automatic import sorting on save.

You can add the following settings into settings.json to format for Python specifically:

```json
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
```

## Docker

You need to be in the same folder as docker-compose.yml and to have Docker running on your computer for the commands to work.

`docker-compose up -d` starts and stays open in the background.

`docker-compose up --build -d` builds new images.

`docker-compose down` closes.

### How to update

`docker-compose down --rmi all` closes if open and removes the images.

On the next start Docker will rebuild the images using the new code.
