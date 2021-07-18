import datetime
import random

from flask import Blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask import g

from . import db

bp = Blueprint("pets", "pets", url_prefix="")

def format_date(d):
    if d:
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        v = d.strftime("%a - %b %d, %Y")
        return v
    else:
        return None

@bp.route("/search/<field>/<value>")
def search(field, value):
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used. 
    if oby == "species":
        oby = "s.name"
    else :
        if oby == "name":
            oby = "p.name"
        elif oby == "bought":
            oby = "p.bought"
        elif oby == "sold":
            oby = "p.sold"
        else :
            oby = "p.id"
    order = request.args.get("order", "asc")
    if order == "asc":
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s,tags_pets tg, tag t where p.species = s.id and tg.pet = p.id and tg.tag = t.id and t.name = ? order by {oby}", [value])
    else:
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s,tags_pets tg , tag t where p.species = s.id and tg.pet = p.id and tg.tag = t.id and t.name = ? order by {oby} desc",[value])
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order = "desc" if order == "asc" else "asc")

@bp.route("/")
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used. 
    if oby == "species":
        oby = "s.name"
    else :
        if oby == "name":
            oby = "p.name"
        elif oby == "bought":
            oby = "p.bought"
        elif oby == "sold":
            oby = "p.sold"
        else :
            oby = "p.id"
    order = request.args.get("order", "asc")
    if order == "asc":
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by {oby}")
    else:
        cursor.execute(f"select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by {oby} desc")
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")


@bp.route("/<pid>")
def pet_info(pid): 
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
    pet = cursor.fetchone()
    cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
    tags = (x[0] for x in cursor.fetchall())
    name, bought, sold, description, species = pet
    data = dict(id = pid,
                name = name,
                bought = format_date(bought),
                sold = format_date(sold),
                description = description, #TODO Not being displayed
                species = species,
                tags = tags)
    return render_template("petdetail.html", **data)

@bp.route("/<pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
        pet = cursor.fetchone()
        cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
        tags = (x[0] for x in cursor.fetchall())
        name, bought, sold, description, species = pet
        data = dict(id = pid,
                    name = name,
                    bought = format_date(bought),
                    sold = format_date(sold),
                    description = description,
                    species = species,
                    tags = tags)
        return render_template("editpet.html", **data)
    elif request.method == "POST":
        description = request.form.get('description')
        sold = request.form.get("sold")
        cursor.execute("select p.bought from pet p where p.id = ?",[pid])
        bought, = cursor.fetchone()
        bought = datetime.datetime.strptime(bought, '%Y-%m-%d').date() 
        if sold :
            sold = bought + datetime.timedelta(days=random.randint(5, 30))
        # TODO Handle sold
        cursor.execute(f"UPDATE pet SET sold = ? , description = ? WHERE id = ?", [sold, description,pid])
        cursor.close()
        conn.commit()
        return redirect(url_for("pets.pet_info", pid=pid), 302)
        
    



