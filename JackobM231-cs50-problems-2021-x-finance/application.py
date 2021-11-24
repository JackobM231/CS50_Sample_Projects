import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Query for informations on main page---
    main_table = db.execute("SELECT operations.symbol, operations.name, SUM(operations.shares_num) AS shares_num, SUM(operations.price_sum) AS price_sum\
    FROM operations\
    INNER JOIN junction ON junction.operation_id = operations.id\
    INNER JOIN users ON junction.user_id = users.id\
    WHERE users.id = ?\
    GROUP BY symbol\
    ORDER BY operations.time", session.get("user_id"))

    # Current values of user's stocks---
    total = 0
    for i in range(len(main_table)):
        main_table[i]["current_value"] = lookup(main_table[i]["symbol"])["price"]
        main_table[i]["shares_value"] = main_table[i]["current_value"] * main_table[i]["shares_num"]
        total += main_table[i]["shares_value"]

    # Query for user's avilable money---
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]

    # Redirect user to main page---
    return render_template("index.html", main_table=main_table, total=total, cash=cash, usd=usd)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)---
    if request.method == "POST":

        # Ensure symbol was submitted and there is such symbol in db---
        if not request.form.get("symbol") or not lookup(request.form.get("symbol")):
            return apology("lack of symbol or symbol not recognized", 400)
            
        # Ensure amount of shares was numeric and positive---
        try:
            int(request.form.get("shares"))
        except:
            return apology("amount of shares should be numeric and positive", 400)
        
       # Ensure amount of shares was numeric and positive---
        if isinstance(request.form.get("shares"), float) or int(request.form.get("shares")) < 0:
            return apology("amount of shares should be numeric and positive", 400)

        shares = int(request.form.get("shares"))
        cost = float(lookup(request.form.get("symbol"))["price"])
        price = shares * cost
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"])

        # Ensure user has enough money to buy shares---
        if price > cash:
            return apology("not enough resorces on the accont", 400)
            
        else:

            symbol = request.form.get("symbol")
            name = lookup(symbol)["name"]
            total = round((cash - price), 2)
            time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            # Buying is 1 selling is 0---
            operation = 1

            # Updating the tables after the operation is performed---
            db.execute("INSERT INTO operations (symbol, name, cost, shares_num, price_sum, total, time, operation_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                        symbol, name, cost, shares, round(price, 2), total, time, operation)

            # Determining the id of the operation---
            operation_id = int(db.execute("SELECT id FROM operations WHERE time = ? AND total = ?", time, total)[0]["id"])

            # Determining the id of the user---
            user_id = int(session.get("user_id"))

            # Update amoun of cash on the account---
            db.execute("UPDATE users SET cash = ? WHERE id = ? ", total, user_id)

            # Create connection between two tables (users and operations)---
            db.execute("INSERT INTO junction (user_id, operation_id) VALUES(?, ?)", user_id, operation_id)

            # Query for informations on bought page---
            main_table = db.execute("SELECT operations.symbol, operations.name, operations.cost, operations.shares_num, operations.price_sum, operations.total, operations.time \
            FROM operations \
            INNER JOIN junction ON junction.operation_id = operations.id \
            INNER JOIN users ON junction.user_id = users.id \
            WHERE users.id = ? \
            ORDER BY operations.time DESC", session.get("user_id"))

            # Redirect user to bought---
            return render_template("bought.html", main_table=main_table, usd=usd)

    # User reached route via GET (as by clicking a link or via redirect)---
    else:
        # Query database for available cash for this user---
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]
        return render_template("buy.html", cash=cash, usd=usd)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Query for informations---
    main_table = db.execute("SELECT operations.symbol, operations.name, operations.cost, operations.shares_num, operations.price_sum, operations.time, operations.operation_type \
    FROM operations\
    INNER JOIN junction ON junction.operation_id = operations.id\
    INNER JOIN users ON junction.user_id = users.id\
    WHERE users.id = ?\
    ORDER BY operations.time DESC", session.get("user_id"))
    
    # Query for cost of investments---
    operations_cost = db.execute("SELECT operations.price_sum, operations.operation_type\
    FROM operations\
    INNER JOIN junction ON junction.operation_id = operations.id\
    INNER JOIN users ON junction.user_id = users.id\
    WHERE users.id = ?", session.get("user_id"))
    
    print(operations_cost)
    
    result = 0
    for operation in operations_cost:
        if operation["operation_type"] == 1:
            result -= operation["price_sum"]
        else:
            result += operation["price_sum"]
    
    # Redirect user to main page---
    return render_template("history.html", main_table=main_table, result=result, usd=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)---
    if request.method == "POST":
        
        # Ensure symbol was submitted---
        if not request.form.get("symbol"):
            return apology("Must provide username", 400)        
        
        # Ensure symbol was in data base---
        if lookup(request.form.get("symbol")) == None:
            return apology("Unknown company's symbol", 400)
            
        company = lookup(request.form.get("symbol"))
        company["price"] = usd(company["price"])
        return render_template("quoted.html", company=company)

    # User reached route via GET (as by clicking a link or via redirect)---
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id---
    session.clear()

    # User reached route via POST (as by submitting a form via POST)---
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted---
        if not username:
            return apology("must provide username", 400)

        # Ensure username wasn't already taken---
        elif db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("username is already taken", 400)

        # Ensure password was submitted---
        elif not password:
            return apology("must provide password", 400)

        # Ensure password is same as confirmation---
        elif not password == confirmation:
            return apology("passwords are different from each other", 400)

        else:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)---
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)---
    if request.method == "POST":

        # Ensure symbol was submitted and user has such shares---
        symbol = request.form.get("symbol")
        query = db.execute("SELECT operations.symbol\
        FROM operations\
        INNER JOIN junction ON junction.operation_id = operations.id\
        INNER JOIN users ON junction.user_id = users.id\
        WHERE users.id = ?\
        GROUP BY symbol ", session.get("user_id"))

        user_symbols = []
        for i in range(len(query)):
            user_symbols.append(query[i]["symbol"])

        if not symbol or not symbol in user_symbols:
            return apology("lack of symbol or you don't have such shares", 400)

        # Ensure user has such shares---
        table = db.execute("SELECT operations.symbol, SUM(operations.shares_num) AS shares_num\
        FROM operations\
        INNER JOIN junction ON junction.operation_id = operations.id\
        INNER JOIN users ON junction.user_id = users.id\
        WHERE users.id = ? AND operations.symbol = ?\
        GROUP BY symbol\
        ORDER BY operations.time", session.get("user_id"), symbol)[0]
        
        # Ensure amount of shares was submitted---
        if not request.form.get("shares"):
            return apology("lack of amount of shares", 400)
        
        # Ensure amount of shares was numeric and positive---
        try:
            int(request.form.get("shares"))
        except:
            return apology("amount of shares should be numeric and positive", 400)
        
       # Ensure amount of shares was numeric and positive---
        if isinstance(request.form.get("shares"), float) or int(request.form.get("shares")) < 0:
            return apology("amount of shares should be numeric and positive", 400)

        # Ensure user has sufficient amount of shares---
        shares = int(request.form.get("shares"))*(-1)

        if (shares * (-1)) > table["shares_num"]:
            return apology("insufficient amount of shares", 400)

        # Sell operation
        else:
            name = lookup(symbol)["name"]
            cost = float(lookup(request.form.get("symbol"))["price"])
            price = shares * cost
            cash = float(db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"])
            total = round((cash + price * (-1)), 2)
            time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            # Buying is 1 selling is 0---
            operation = 0

            # Updating the tables after the operation is performed---
            db.execute("INSERT INTO operations (symbol, name, cost, shares_num, price_sum, total, time, operation_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                        symbol, name, cost, shares, round(price, 2), total, time, operation)

            # Determining the id of the operation---
            operation_id = int(db.execute("SELECT id FROM operations WHERE time = ? AND total = ?", time, total)[0]["id"])

            # Determining the id of the user---
            user_id = int(session.get("user_id"))

            # Update amoun of cash on the account---
            db.execute("UPDATE users SET cash = ? WHERE id = ? ", total, user_id)

            # Create connection between two tables (users and operations)---
            db.execute("INSERT INTO junction (user_id, operation_id) VALUES(?, ?)", user_id, operation_id)

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)---
    else:
       # Query for informations on main page---
        main_table = db.execute("SELECT operations.symbol, operations.name, SUM(operations.shares_num) AS shares_num\
        FROM operations\
        INNER JOIN junction ON junction.operation_id = operations.id\
        INNER JOIN users ON junction.user_id = users.id\
        WHERE users.id = ?\
        GROUP BY symbol\
        ORDER BY operations.time", session.get("user_id"))

        # Current values of user's stocks---
        total = 0
        for i in range(len(main_table)):
            main_table[i]["current_value"] = lookup(main_table[i]["symbol"])["price"]
            main_table[i]["shares_value"] = main_table[i]["current_value"] * main_table[i]["shares_num"]
            total += main_table[i]["shares_value"]

        # Query for user's avilable money---
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]

        # Redirect user to sell page---
        return render_template("sell.html", main_table=main_table, total=total, cash=cash, usd=usd)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
