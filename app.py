from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient, ASCENDING, errors
from bson.json_util import dumps


app = Flask(__name__)
client = MongoClient("db", port=27017)
db = client.product_db
db.product_db.create_index([("id", ASCENDING)], unique=True)


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/table")
def table():
    _items = db.product_db.find().sort("id")
    items = [item for item in _items]
    message = check_content(items)
    if request.is_json:
        return dumps(items)
    else:
        return render_template("table.html", items=items, mycontent=message)


@app.route("/add")
def add():
    return render_template("add.html")


@app.route("/new", methods=['POST', 'GET'])
def new():
    if request.is_json:
        data = request.get_json()
        parameters = [data["memory"], data["ram"], data["color"]]
        item_doc = {
            "id": data["id"],
            "name": data["name"],
            "desc": data["desc"],
            "par": parameters
        }
    else:
        parameters = [request.form["memory"], request.form["ram"], request.form["color"]]
        item_doc = {
            "id": request.form["id"],
            "name": request.form["name"],
            "desc": request.form["desc"],
            "par": parameters
        }
    page = "add.html"
    if item_doc["id"] == "" or item_doc["name"] == "" or item_doc["desc"] == "" or parameters[0] == "" or \
            parameters[1] == "" or parameters[2] == "":
        message = "Заполните все поля!"
        if request.is_json:
            return {"0": "Fill in all the fields!"}
        else:
            return render_template(page, mycontent=message)
    if not parameters[0].isdigit() or not parameters[1].isdigit():
        message = "Значение памяти должно быть заполнено целыми числами."
        if request.is_json:
            return {"0": "Memory value should be filled with integers."}
        else:
            return render_template(page, mycontent=message)
    try:
        db.product_db.insert_one(item_doc)
        message = "Товар успешно добавлен!"
        if request.is_json:
            return {"1": "Product successfully added!"}
        else:
            return render_template(page, mycontent=message)
    except errors.DuplicateKeyError:
        message = "В базе имеется товар с данным id. Проверьте введённые данные."
        if request.is_json:
            return {"0": "Product with this id already in database. Check input."}
        else:
            return render_template(page, mycontent=message)


@app.route("/remove")
def remove():
    _items = db.product_db.find()
    for item in _items:
        db.product_db.remove(item)
    return redirect(url_for('main'))


@app.route("/filter_by")
def filter_by():
    return render_template("filter_by.html")


@app.route("/find_par", methods=['POST'])
def find_par():
    if request.is_json:
        req_json = request.get_json()
        res = [req_json["find_par1"], req_json["find_par2"], req_json["find_par3"]]
    else:
        res = [request.form["find_par1"], request.form["find_par2"], request.form["find_par3"]]

    id_items = db.product_db.find({"par.0": {"$regex": res[0], "$options": "i"}, "par.1": {"$regex": res[1], "$options": "i"},
                                   "par.2": {"$regex": res[2], "$options": "i"}})
    items = [item for item in id_items]
    message = check_content(items)
    if request.is_json:
        return dumps(items)
    else:
        return render_template("find.html", items=items, mycontent=message)


@app.route("/find_name", methods=['POST'])
def find_name():
    if request.is_json:
        req_json = request.get_json()
        res = req_json["find_name"]
    else:
        res = request.form["find_name"]
    check_filter_param(res)
    name_items = db.product_db.find({"name": {"$regex": res, "$options": "i"}})
    items = [item for item in name_items]
    message = check_content(items)
    if request.is_json:
        return dumps(items)
    else:
        return render_template("find.html", items=items, mycontent=message)


@app.route("/find_prod")
def find_prod():
    return render_template("find_by_id.html")


@app.route("/find_prod_by_id", methods=['POST', 'GET'])
def find_prod_by_id():
    if request.is_json:
        req_json = request.get_json()
        res = req_json["find_id"]
    else:
        res = request.form["find_id"]
    check_filter_param(res)
    items = db.product_db.find({"id": res})
    items = [item for item in items]
    message = check_content(items)
    if request.is_json:
        return dumps(items)
    else:
        return render_template("result.html", items=items, mycontent=message)


def check_content(items):
    items = [item for item in items]
    if len(items) == 0:
        message = "По запросу ничего не было найдено."
    else:
        message = "По запросу было найдено:"
    return message


def check_filter_param(res):
    if res == "":
        message = "Задайте значение для фильтрации!"
        return render_template("filter_by.html", mycontent=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)