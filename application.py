from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session
from datetime import datetime
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL ( "sqlite:///data.db" )

@app.route("/")
def index():
    shirts = db.execute("SELECT * FROM shirts ORDER BY team ASC")
    shirtsLen = len(shirts)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = db.execute("SELECT * FROM shirts ORDER BY team ASC")
        shirtsLen = len(shirts)
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route("/buy/")
def buy():
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        shirts = db.execute("SELECT * FROM shirts ORDER BY team ASC")
        shirtsLen = len(shirts)
        return render_template ("index.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/update/")
def update():
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id", id=id)
        goods = db.execute("SELECT * FROM shirts WHERE id = :id", id=id)
        price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal) VALUES (:id, :qty, :team, :image, :price, :subTotal)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from cart")
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, team, image, quantity) VALUES(:uid, :id, :team, :image, :quantity)", uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"] )
    db.execute("DELETE from cart")
    shoppingCart = []
    return redirect('/')

@app.route("/remove/", methods=["GET"])
def remove():
    out = int(request.args.get("id"))
    db.execute("DELETE from cart WHERE id=:id", id=out)
    totItems, total, display = 0, 0, 0
    shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    display = 1
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/new/", methods=["GET"])
def new():
    return render_template("new.html")

@app.route("/logged/", methods=["POST"] )
def logged():
    user = request.form["username"].lower()
    pwd = request.form["password"]
    if user == "" or pwd == "":
        return render_template ( "login.html" )
    query = "SELECT * FROM users WHERE username = :user AND password = :pwd"
    rows = db.execute ( query, user=user, pwd=pwd )
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now( )
        session['uid'] = rows[0]["id"]
    if 'user' in session:
        return redirect ( "/" )
    return render_template ( "login.html", msg="Wrong username or password." )

@app.route("/history/")
def history():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    myShirts = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShirtsLen = len(myShirts)
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)

@app.route("/logout/")
def logout():
    db.execute("DELETE from cart")
    session.clear()
    return redirect("/")

@app.route("/register/", methods=["POST"] )
def registration():
    username = request.form["username"]
    password = request.form["password"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = username )
    if len( rows ) > 0:
        return render_template ( "new.html", msg="Username already exists!" )
    new = db.execute ( "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                    username=username, password=password, fname=fname, lname=lname, email=email )
    return render_template ( "login.html" )

@app.route("/cart/")
def cart():
    if 'user' in session:
        totItems, total, display = 0, 0, 0
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)