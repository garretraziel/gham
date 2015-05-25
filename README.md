GitHub Activity Mining
======================

Dolování budoucí aktivity projektů ze serveru GitHub.

Instalace
---------

Pro instalaci je vhodné použít program virtualenv.

1. (volitelně) vytvořte virtualenv pomocí:

        virtualenv ~/django_virtualenv
        source ~/django_virtualenv/bin/activate

2. Nainstalujte požadované knihovny:

        pip install -r requirements.txt

3. Vytvořte databázi pomocí:

        python manage.py migrate

4. Na adrese https://github.com/settings/developers vytvořte novou aplikaci, callback URL nastavte na

        http://localhost:8000/
   
    Vytvořte soubor `gham/localsettings.py`, do proměnné `SOCIAL_AUTH_GITHUB_KEY` uložte `Client ID`,
    do proměnné `SOCIAL_AUTH_GITHUB_SECRET` uložte `Client Secret` (tyto hodnoty by měly být zobrazeny v administraci
    aplikace, kterou jste právě vytvořili).

5. Spusťte aplikaci pomocí:

        python manage.py runserver

6. Aplikace běží na http://localhost:8000.

Použití
-------

Po přihlášení přes servery GitHubu můžete v nabídce vlevo přidat název repozitáře ze serveru GitHub, pro který se mají
spočítat statistiky. Stahování statistik trvá nějakou dobu - odkaz na repozitář je po tu dobu označen šedou barvou.
Po stáhnutí statistik se tento odkaz automaticky zpřístupní.
