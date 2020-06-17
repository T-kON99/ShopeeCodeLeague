# Shopee Code League Announcer

This is a tool to filter given user Gmail credential and fetch out any email sent by Shopee Code League's email and filter the available
workshops to discord instead. Only confirmed workshop will be announced.

## Setting Up

### Fetching Files

```bash
git clone https://github.com/T-kON99/ShopeeCodeLeague.git ShopeeCodeLeague
```

### Installating Dependencies

```bash
cd ShopeeCodeLeague
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Running

```bash
python ShopeeCodeLeague.py
```

### Footnotes

1. You can use `cron` job to schedule this at a regular interval. Alternatively you can set up Google pub/sub API to `watch` your gmail instead, but that is not what this project is for.
2. Alternatively you can use [pythonanywhere](https://www.pythonanywhere.com/) to host this project and run `./announce.sh` instead. Do set the permission to be an executeable script with `chmod +x ./announce.sh`. 
3. Replace the dir specified in `./announce.sh` to your respective dir.