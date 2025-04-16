# 📬 Gmail Archiváló Script (Python)

Ez a Python-script az összes beérkező Gmail levelet **archiválja** azáltal, hogy eltávolítja róluk az `INBOX` címkét. A levelek így **megmaradnak**, de eltűnnek a beérkező mappából — vagyis archiválódnak.

---

## ⚙️ Funkciók

- 🔐 Google OAuth2 hitelesítés
- 📥 Összes beérkező levél lekérése
- 📦 Archiválás: `INBOX` címke eltávolítása
- 🛠 API használat: `gmail.modify` scope-on keresztül

---

## 📋 Követelmények

- Python 3.6+
- Gmail fiók
- Google Cloud projekt
- Engedélyezett Gmail API

---

## 📦 Telepítés

1. Klónozd a repót vagy másold le a `gmail_archiver.py` scriptet.
2. Telepítsd a szükséges csomagokat:

   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

---
🔐 Google Cloud beállítások
1. Google Cloud Console
Lépj be: console.cloud.google.com

Hozz létre egy új projekt.

2. Gmail API engedélyezése
Menj: APIs & Services > Library

Keresd meg: Gmail API

Kattints: Enable

3. OAuth hitelesítés beállítása
Menj: APIs & Services > Credentials

Kattints: + Create Credentials > OAuth Client ID

App típusa: Desktop App

Töltsd le a kapott credentials.json fájlt és helyezd el a scripted mellé.

4. Tesztelők hozzáadása
Menj a OAuth consent screen menüpontra

Töltsd ki az alapadatokat (app név, e-mail)

Görgess le a Test users részhez és:

Add hozzá azt a Gmail-címet, amivel tesztelni (futtatni) szeretnéd a scriptet!

---


🧪 Használat
Futtasd a scriptet:

```bash

python gmail_archiver.py
```
Az első futás során:

Megnyílik a böngésző

Jelentkezz be a Gmail fiókoddal

Engedélyezd az app számára a Gmail hozzáférést

Ha a hitelesítés sikeres:

Létrejön egy token.json fájl

A script lekéri az összes INBOX címkével rendelkező levelet

És eltávolítja róluk az INBOX címkét → tehát archiválja őket

---


📁 Fájlok

Fájl	Leírás
gmail_archiver.py	A fő script, amit futtatni kell
credentials.json	Google OAuth2 kliensfájl a Cloud Console-ból
token.json	A felhasználói hitelesítés tokenje

---

⚠️ Megjegyzések
A levelek nem törlődnek, csak az INBOX címke kerül eltávolításra.

Ezután a levelek a "Minden levél" (All Mail) nézetben maradnak meg.

Ha sok e-mail van (pl. több ezer), a folyamat eltarthat egy ideig.

---

❓ Hibakeresés
🔴 403 access_denied hiba
➡️ Valószínűleg nem adtad hozzá a Gmail címedet a Test users listához a Google Cloud Console-ban.

🔴 ModuleNotFoundError: No module named 'google'
➡️ Telepítsd a szükséges csomagokat:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

🧠 Fejlesztési lehetőségek
📅 Csak régi levelek archiválása (pl. 2022 előtti)

✅ Csak olvasott levelek archiválása

⭐ Csillagozott vagy fontos levelek kivételével archiválás

🗂 Feldolgozás batch-ekben (100-asával) nagy fiókok esetén