## News video website
It's a [Demo website](http://140.238.65.147:5000). Not for commercial purposes!
The main goal is to have the main news sites' videos in one place.
New news video links are uploaded and checked at the moment the user chooses a channel. This process is very fast because asyncio library are used.

New channel scrapers can be easily added. The new scraper should be imported only in one place (in scraper.py).


### Install all required libraries:
requires python 3.8 or greater

```
pip install -r requirements.txt
```

### Running the code:

* **debug mode** - app.run(debug=True, host='localhost', port=8000) in app_async.py:
```
python3 app_async.py
```

* **production** - app.run(host='0.0.0.0', port=int("5000")) in app_async.py:
```
gunicorn --workers=2 app_async:app --bind 0.0.0.0:5000
```
