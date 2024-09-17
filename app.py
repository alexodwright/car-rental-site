from flask import Flask, render_template, session, url_for, redirect, g, request
from flask_session import Session
from database import get_db, close_db
from forms import RegistrationForm, LoginForm, VehicleFilter, InsertCar, DeleteCar, DetailsForm, ReviewForm, ChangePasswordForm, UpdateCarForm, ChangePFPForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

'''
My website has two types of users: regular and admins.
Regular users can be created through the usual register page.
Extra admin accounts can be created from the administration page which is only accessible by other admins.
Admin accounts have features such as: insert new cars into the database, delete cars from the database, update the price of existing cars and create new admin accounts.
There is an admin account created upon creation of the users database. The email is 'admin@admin.mail.ie' and the password is 'super-secret-password'. I know, super secure!
'''


UPLOAD_PATH = os.getcwd() + "/static"
app = Flask(__name__)   
app.config["SECRET_KEY"] = "my-secret-key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)
app.teardown_appcontext(close_db)
methods = ["GET", "POST"]

@app.before_request
def load_logged_in_user():
    db = get_db()
    g.user = session.get('user_id', None)
    if g.user is not None:
        g.is_admin = db.execute("SELECT is_admin FROM users WHERE user_id = ?", (g.user, )).fetchone()['is_admin']
        g.pfp = db.execute('SELECT pfp FROM users WHERE user_id = ?', (g.user, )).fetchone()['pfp']

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def admin_required_wrapped_view(*args, **kwargs):
        if g.is_admin == 0:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return admin_required_wrapped_view

    
@app.route("/", methods=methods)
def registration():
    form = RegistrationForm()
    db = get_db()
    if form.validate_on_submit():
        fname = form.fname.data.strip()
        lname = form.lname.data.strip()
        email = form.email.data.strip()
        password = generate_password_hash(form.password.data)
        check_query = """
                    SELECT *
                    FROM users
                    WHERE email = ?
                    """
        check_user = db.execute(check_query, (email, )).fetchone()
        if check_user is None: 
            query = """
                    INSERT INTO users (fname, lname, email, password)
                    VALUES (?, ?, ?, ?)
                    """
            db.execute(query, (fname, lname, email, password))
            db.commit()
            return redirect(url_for('login'))
        else:
            form.email.errors.append("User already exists!")
    return render_template("registration.html", form=form)

@app.route("/login", methods=methods)
def login():
    form = LoginForm()
    db = get_db()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        query = """
                SELECT *
                FROM users
                WHERE email = ?
                """
        res = db.execute(query, (email, )).fetchone()
        if res is None:
            form.email.errors.append("User does not exist!")
        else:
            if check_password_hash(res["password"], password):
                session["user_id"] = res["user_id"]
                check_admin = db.execute('SELECT is_admin FROM users WHERE user_id = ?', (session['user_id'],)).fetchone()['is_admin']
                next_page = request.args.get('next')
                if check_admin == 1:
                    if not next_page:
                        next_page = url_for('admin')
                else:
                    if not next_page:
                        next_page = url_for('vehicles')
                return redirect(next_page)
            else:
                form.password.errors.append("Wrong Password!")
            session.modified = True
    return render_template("login.html", form=form)

@app.route("/vehicles", methods=methods)
def vehicles():
    db = get_db()
    form = VehicleFilter()
    params = []
    favourites = []
    sort_choices = form.sort_by.choices
    sort_choices_sql = ["model", "model DESC", "price DESC", "price"]
    sort_by_dict = {k: v for k, v in zip(sort_choices, sort_choices_sql)}
    sort_by = sort_choices[0]
    get_brands = """
                SELECT DISTINCT brand
                FROM cars
                ORDER BY brand
                """
    slider = {}
    slider['value'] = 0
    slider['max'] = db.execute("SELECT MAX(price) FROM cars").fetchone()["MAX(price)"]
    brands = db.execute(get_brands).fetchall()
    brands = [car['brand'] for car in brands]
    form.brand.choices += brands
    get_cars = """
                SELECT *
                FROM cars
                """
    if form.validate_on_submit():
        brand = form.brand.data
        max_price = form.price_range.data
        slider['value'] = max_price
        sort_by = form.sort_by.data
        if brand != "All":
            get_cars += "WHERE brand = ?"
            params.append(brand)
        if max_price != 0 and brand != "All":
            get_cars += "AND price <= ?"
            params.append(max_price)
        elif max_price != 0 and brand == "All":
            get_cars += "WHERE price <= ?"
            params.append(max_price)
    get_cars += f"ORDER BY {sort_by_dict[sort_by]}"
    cars = db.execute(get_cars, tuple(params)).fetchall()
    if g.user is not None:
        check_favourites = db.execute('SELECT car_id FROM favourites WHERE user_id = ?', (g.user,)).fetchall()
        favourites = [car['car_id'] for car in check_favourites]
    return render_template("vehicles.html", cars=cars, form=form, slider=slider, favourites=favourites)

@app.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for('login'))

@app.route("/checkout")
@login_required
def checkout():
    db = get_db()
    checkout = None
    total: int = 0
    if 'cart' in session:
        checkout_car_ids = tuple(session['cart'])
        if len(checkout_car_ids) == 1:
            checkout_car_ids = f"({checkout_car_ids[0]})"
        get_checkout = f"""
                        SELECT *
                        FROM cars
                        WHERE car_id IN {checkout_car_ids}
                        """
        checkout = db.execute(get_checkout).fetchall()
        for car in checkout:
            total += car['price'] * session['cart'][car['car_id']]
    return render_template('checkout.html', checkout=checkout, total=total)

@app.route("/add_to_cart/<int:car_id>/<int:days>")
@login_required
def add_to_cart(car_id, days):
    if 'cart' not in session:
        session['cart'] = {}
    if car_id not in session['cart']:
        session["cart"][car_id] = days
    else:
        session["cart"][car_id] += days
    session.modified = True
    return redirect(url_for("checkout"))

@app.route("/decrease_quantity/<int:car_id>/<int:days>")
def decrease_quantity(car_id, days):
    session['cart'][car_id] -= days
    if session['cart'][car_id]==0:
        del session['cart'][car_id]
    session.modified = True
    return redirect(url_for('checkout'))

@app.route("/view_details/<int:car_id>", methods=methods)
def view_details(car_id):
    form = DetailsForm()
    favourites = []
    db = get_db()
    get_car = """
            SELECT *
            FROM cars
            WHERE car_id = ?
            """
    car = db.execute(get_car, (car_id, )).fetchone()
    get_reviews = '''
                SELECT r.content, u.fname, u.lname, u.pfp
                FROM reviews AS r JOIN users AS u
                ON u.user_id = r.user_id
                WHERE car_id = ?
                LIMIT 3
                '''
    reviews = db.execute(get_reviews, (car_id, )).fetchall()
    if g.user is not None:
        check_favourites = db.execute('SELECT car_id FROM favourites WHERE user_id = ?', (g.user,)).fetchall()
        favourites = [car['car_id'] for car in check_favourites]
    if form.validate_on_submit():
        days = form.days.data
        return redirect(url_for('add_to_cart', car_id=car_id, days=days))
    return render_template("details.html", car=car, form=form, reviews=reviews, favourites=favourites)

@app.route("/account")
@login_required
def account():
    db = get_db()
    get_user = """
            SELECT *
            FROM users
            WHERE user_id = ?
            """
    user = db.execute(get_user, (g.user, )).fetchone()

    orders = db.execute("""
                        SELECT o.transaction_id, c.brand, c.model, o.days, c.car_id, c.image
                        FROM orders AS o JOIN users AS u JOIN cars AS c
                        ON o.user_id = u.user_id AND o.car_id = c.car_id
                        WHERE u.user_id = ?""", (g.user,)).fetchall()
    ids: list[int] = []
    for order in orders:
        if order['transaction_id'] not in ids:
            ids.append(order['transaction_id'])
    # to have the most recent order at the top
    ids = ids[::-1]
    favourites = db.execute('SELECT f.car_id, c.model, c.brand, c.image, c.price FROM favourites AS f JOIN cars AS c ON c.car_id = f.car_id WHERE f.user_id = ?', (g.user, )).fetchall()
    return render_template("account.html", user=user, orders=orders, ids=ids, favourites=favourites)

@app.route("/change_pfp", methods=methods)
@login_required
def change_pfp():
    db = get_db()
    form = ChangePFPForm()
    user = db.execute("SELECT fname, lname, user_id FROM users WHERE user_id = ?", (g.user, )).fetchone()
    if form.validate_on_submit():
        filename = f"{user['fname']}{user['lname']}{user['user_id']}.jpg"
        file = request.files[form.pfp.name].read()
        with open(UPLOAD_PATH + f"/{filename}", "wb") as image:
            image.write(file)
        db.execute('UPDATE users SET pfp = ? WHERE user_id = ?', (filename, g.user))
        db.commit()
        g.pfp = filename
        return redirect('account')
    return render_template("changepfp.html", form=form)

@app.route("/change_password", methods=methods)
@login_required
def change_password():
    db = get_db()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        new_password = form.new_password.data
        current_password = db.execute('SELECT password FROM users WHERE user_id = ?', (g.user, )).fetchone()['password']
        if check_password_hash(current_password, old_password):
            db.execute('UPDATE users SET password = ?', (generate_password_hash(new_password), ))
            db.commit()
            return redirect("account")
        else:
            form.old_password.errors.append("Old password incorrect!")
    return render_template("changepassword.html", form=form)

@app.route("/buynow")
@login_required
def buynow():
    db = get_db()
    transaction_id = db.execute("SELECT MAX(transaction_id) as t_id FROM orders").fetchone()['t_id']
    # grouping the cars by order number - i.e. cars ordered in one transaction with each other
    if transaction_id is None:
        transaction_id = 0
    else:
        transaction_id += 1
    if 'cart' in session:
        for car in session['cart']:
            insert_order = '''
                            INSERT INTO orders (transaction_id, user_id, car_id, days)
                            VALUES (?, ?, ?, ?)
                            '''
            db.execute(insert_order, (transaction_id, g.user, car, session['cart'][car]))
            db.commit()
    session['cart'].clear()
    session.modified = True
    return redirect('account')

@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template('admin.html')

@app.route("/change_car", methods=methods)
@login_required
@admin_required
def change_car():
    db = get_db()
    form = UpdateCarForm()
    if form.validate_on_submit():
        brand = form.brand.data
        model = form.model.data
        price = form.price.data
        new_price = form.new_price.data
        params = []
        check = db.execute('SELECT * FROM cars WHERE brand = ? AND model = ? AND price = ?', (brand, model, price)).fetchone()
        query = '''
                UPDATE cars
                '''
        if check is not None:
            if form.new_image.data:
                filename = f"{brand}{model}.jpg"
                # avoid overwriting other files already in the static folder
                if filename in os.listdir(UPLOAD_PATH):
                    filename = filename.strip(".jpg")
                    filename += "1.jpg"
                if ' ' in filename:
                    filename = filename.replace(' ', '_')
                image_data = request.files[form.new_image.name].read()
                with open(UPLOAD_PATH + f"/{filename}", "wb") as image:
                    image.write(image_data)
            if form.new_image.data and form.new_price.data:
                query += " SET image = ?, price = ?"
                params += [filename, new_price]
            else:
                query += "SET price = ?"
                params.append(new_price)
            params += [brand, model, price]
            query += " WHERE brand = ? AND model = ? AND price = ?"
            db.execute(query, tuple(params))
            db.commit()
        else:
            form.brand.errors.append("Car with these details does not exist!")
        return redirect('admin')
    return render_template("updatecar.html", form=form)

@app.route("/create_admin", methods=methods)
@login_required
@admin_required
def create_admin():
    db = get_db()
    form = RegistrationForm()
    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        check_query = """
                    SELECT *
                    FROM users
                    WHERE email = ?
                    """
        check_user = db.execute(check_query, (email, )).fetchone()
        if check_user is None: 
            query = """
                    INSERT INTO users (fname, lname, email, password, is_admin)
                    VALUES (?, ?, ?, ?, 1)
                    """
            db.execute(query, (fname, lname, email, password))
            db.commit()
        else:
            form.email.errors.append("User with email already exists!")
        return redirect("admin")
    return render_template("createadmin.html", form=form)

@app.route("/insert_car", methods=methods)
@login_required
@admin_required
def insert_car():
    db = get_db()
    form = InsertCar()
    if form.validate_on_submit():
        brand = form.brand.data
        model = form.model.data
        price = form.price.data
        description = form.description.data
        params = [brand, model, price, description]
        check = db.execute('SELECT * FROM cars WHERE brand = ? AND model = ? AND price = ?', (brand, model, price)).fetchone()
        if check is None:
            if form.image.data:
                filename = f"{brand}{model}.jpg"
                # avoid overwriting files already in static
                if filename in os.listdir(UPLOAD_PATH):
                    filename.strip(".jpg")
                    filename += "1.jpg"
                file = request.files[form.image.name].read()
                with open(UPLOAD_PATH + f"/{filename}", "wb") as image:
                    image.write(file)
                query = '''
                        INSERT INTO cars (brand, model, price, description, image)
                        VALUES (?, ?, ?, ?, ?)
                        '''
                params.append(filename)
            else: 
                query = '''
                        INSERT INTO cars (brand, model, price, description)
                        VALUES (?, ?, ?, ?)
                        '''
            db.execute(query, params)
            db.commit()
        else:
            form.brand.errors.append("Car with these details already exists")
        return redirect(url_for('admin'))
    return render_template("insertcar.html", form=form)

@app.route("/delete_car", methods=methods)
@login_required
@admin_required
def delete_car():
    db = get_db()
    form = DeleteCar()
    if form.validate_on_submit():
        brand = form.brand.data
        model = form.model.data
        query = '''
                DELETE
                FROM cars
                WHERE brand = ?
                AND model = ?
                '''
        db.execute(query, (brand, model))
        db.commit()
        return redirect('admin')
    return render_template("deletecar.html", form=form)

@app.route("/review/<int:car_id>", methods=methods)
@login_required
def review(car_id):
    db = get_db()
    form = ReviewForm()
    get_car = """
            SELECT *
            FROM cars
            WHERE car_id = ?
            """
    car = db.execute(get_car, (car_id, )).fetchone()
    if form.validate_on_submit():
        content = form.content.data
        query = '''
                INSERT INTO reviews (user_id, car_id, content)
                VALUES (?, ?, ?)
                '''
        db.execute(query, (g.user, car_id, content))
        db.commit()
        return redirect(url_for('account'))
    return render_template("reviews.html", form=form, car=car)

@app.route("/favourite/<int:car_id>/<string:return_site>", methods=methods)
@login_required
def favourite(car_id, return_site):
    db = get_db()
    check = db.execute('SELECT * FROM favourites WHERE car_id = ? AND user_id = ?', (car_id, g.user)).fetchone()
    if check is not None:
        query = '''
                DELETE
                FROM favourites
                WHERE car_id = ?
                AND user_id = ?
                '''
        db.execute(query, (car_id, g.user))
        db.commit()
    else:
        query = '''
                INSERT INTO favourites (car_id, user_id)
                VALUES (?, ?)
                '''
        db.execute(query, (car_id, g.user))
        db.commit()
    if return_site == 'view_details':
        return redirect(url_for(return_site, car_id=car_id))
    return redirect(url_for(return_site))

@app.route("/delete_account")
@login_required
def delete_account():
    db = get_db()
    db.execute("DELETE FROM users WHERE user_id = ?", (g.user, ))
    db.execute("DELETE FROM reviews WHERE user_id = ?", (g.user, ))
    db.execute("DELETE FROM orders WHERE user_id = ?", (g.user, ))
    db.execute("DELETE FROM favourites WHERE user_id = ?", (g.user, ))
    db.commit()
    session.clear()
    session.modified = True
    return redirect(url_for('login'))