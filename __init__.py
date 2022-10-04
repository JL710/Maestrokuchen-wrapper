import flask
import requests
import bs4
from flask import render_template
from concurrent.futures import ThreadPoolExecutor
import re
import time



app = flask.Flask(__name__)

url = "https://nachhilfe.ericmaestrokaesekuchen.de/"

cache = {"last-fetched": 0, "data": ""}




def get_content(url):
    return requests.get(url).content


expression = re.compile("(\d\d\d)")
def find_three_digit(text: str):
    search = expression.search(text)
    if not search:
        return None
    else:
        return search.group(0)


@app.route("/")
def home():
    # check if data is up to date
    if cache["last-fetched"] > time.time() - 60:
        print("up to date")
        return cache["data"]

    cache["last-fetched"] = time.time()

    # else


    content = get_content(url)

    soup = bs4.BeautifulSoup(content, 'html.parser')
    a_tags = soup.find_all("a")



    # python stuff
    python_a_tags = [tag for tag in a_tags if tag["href"].startswith("/python")]

    python_dict = {tag.text: url + tag["href"] for tag in python_a_tags}
    threads = {}
    with ThreadPoolExecutor(max_workers=50) as e:
        for title, source in python_dict.items():
            threads[title] = e.submit(get_content, source)

        python_dict = {key: thread.result() for key, thread in threads.items()}

    python_dict = {item[0]: item[1].decode("cp437") for item in python_dict.items()}    
    

    # try to group by number
    python_data = []
    last_number = None
    for index, key in enumerate(python_dict.keys()):
        if last_number == None or last_number != find_three_digit(key):
            python_data.append([])
        python_data[-1].append({"title": key, "content": python_dict[key], "index": index})
        last_number = find_three_digit(key)

    
    # data stuff
    data_a_tags = [tag for tag in a_tags if tag["href"].startswith("/daten")]
    data_dict = {tag.text: url + tag["href"] for tag in data_a_tags}


    cache["data"] = render_template("template.html", python_data=python_data, data_dict=data_dict)

    return cache["data"]






if __name__ == "__main__":
    app.run()



