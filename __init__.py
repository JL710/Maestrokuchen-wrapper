import flask
import requests
import bs4
from flask import render_template
from concurrent.futures import ThreadPoolExecutor
import re



app = flask.Flask(__name__)


url = "https://nachhilfe.ericmaestrokaesekuchen.de/"



def get_content(url):
    return requests.get(url).content


expression = re.compile("(\d\d\d)")
def find_three_digit(text: str) -> int|None:
    search = expression.search(text)
    if not search:
        return None
    else:
        return search.group(0)


@app.route("/")
def home():
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

    python_dict = {item[0]: item[1].decode("ansi") for item in python_dict.items()}    
    

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

    return render_template("template.html", python_data=python_data, data_dict=data_dict)






if __name__ == "__main__":
    app.run()



