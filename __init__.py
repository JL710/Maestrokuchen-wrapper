import flask
import requests
import bs4
from flask import render_template
from concurrent.futures import ThreadPoolExecutor



app = flask.Flask(__name__)


url = "https://nachhilfe.ericmaestrokaesekuchen.de/"



def get_content(url):
    return requests.get(url).content



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
    
    python_dict = {index: item for index, item in enumerate(python_dict.items())}



    # data stuff
    data_a_tags = [tag for tag in a_tags if tag["href"].startswith("/daten")]
    data_dict = {tag.text: url + tag["href"] for tag in data_a_tags}

    return render_template("template.html", python_dict=python_dict, data_dict=data_dict)






if __name__ == "__main__":
    app.run()



