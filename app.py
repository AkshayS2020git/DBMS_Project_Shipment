from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL connection config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQLReebok@21",
    database="project"
)
cursor = db.cursor()

# Home/Login page
@app.route('/')
def index():
    return render_template('login.html')

# Admin login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin123':
        session['role'] = 'admin'
        return redirect('/admin_dashboard')
    else:
        flash('Invalid admin credentials', 'danger')
        return redirect('/')

# User login
@app.route('/user_login', methods=['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE username=%s AND passwrd=%s", (username, password))
    user = cursor.fetchone()

    if user:
        # user[0] = user_id (int), user[4] = username
        session['user_id'] = user[0]
        session['username'] = user[4]
        session['role'] = 'user'
        return redirect('/user_dashboard')
    else:
        flash('Invalid user credentials', 'danger')
        return redirect('/')

# Register new user
@app.route('/register_user', methods=['POST'])
def register_user():
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form['passwrd']
    email = request.form['email']
    phone = request.form['phone']

    try:
        cursor.execute("INSERT INTO users (user_id, username, passwrd, email, phone_number) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, username, password, email, phone))
        db.commit()
        flash('Registration successful! Please login.', 'success')
    except mysql.connector.Error as err:
        flash(f'Registration failed: {err}', 'danger')

    return redirect('/')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin_dashboard.html')

# User dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect('/')
    return render_template('user_dashboard.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Admin routes
@app.route('/create_shipment', methods=['POST'])
def create_shipment():
    if session.get('role') != 'admin':
        return redirect('/')
    
    shipment_id = request.form['shipment_id']
    order_id = request.form['order_id']
    origin = request.form['origin']
    destination = request.form['destination']
    status = request.form['status']
    
    try:
        cursor.execute(
            "INSERT INTO shipments (shipment_id, order_id, origin, destination, status) VALUES (%s, %s, %s, %s, %s)",
            (shipment_id, order_id, origin, destination, status)
        )
        db.commit()
        flash('Shipment created successfully!', 'success')
    except Exception as e:
        flash(f'Failed to create shipment: {e}', 'danger')
    
    return redirect('/admin_dashboard')


@app.route('/read_shipments')
def read_shipments():
    if session.get('role') != 'admin':
        return redirect('/')
    
    cursor.execute("SELECT * FROM shipments")
    shipments = cursor.fetchall()
    return render_template('admin_dashboard.html', shipments=shipments)


@app.route('/update_shipment', methods=['POST'])
def update_shipment():
    if session.get('role') != 'admin':
        return redirect('/')
    
    shipment_id = request.form['shipment_id']
    new_status = request.form['new_status']
    
    try:
        cursor.execute("UPDATE shipments SET status = %s WHERE shipment_id = %s", (new_status, shipment_id))
        db.commit()
        flash('Shipment status updated!', 'success')
    except Exception as e:
        flash(f'Failed to update shipment: {e}', 'danger')
    
    return redirect('/admin_dashboard')


@app.route('/delete_shipment', methods=['POST'])
def delete_shipment():
    if session.get('role') != 'admin':
        return redirect('/')
    
    shipment_id = request.form['shipment_id']
    
    try:
        cursor.execute("DELETE FROM shipments WHERE shipment_id = %s", (shipment_id,))
        db.commit()
        flash('Shipment deleted!', 'success')
    except Exception as e:
        flash(f'Failed to delete shipment: {e}', 'danger')
    
    return redirect('/admin_dashboard')


# User routes
@app.route('/create_order', methods=['POST'])
def create_order():
    if session.get('role') != 'user':
        return redirect('/')
    
    order_id = request.form['order_id']
    user_id = session.get('user_id')  
    
    status = request.form['status']
    
    try:
        cursor.execute("INSERT INTO orders (order_id, user_id, status) VALUES (%s, %s, %s)",
                       (order_id, user_id, status))
        db.commit()
        flash('Order placed successfully!', 'success')
    except Exception as e:
        flash(f'Failed to place order: {e}', 'danger')
    
    return redirect('/user_dashboard')


@app.route('/my_shipments')
def my_shipments():
    if session.get('role') != 'user':
        return redirect('/')
    
    username = session.get('username')
    cursor.execute("SELECT * FROM shipments WHERE order_id IN (SELECT order_id FROM orders WHERE user_id = %s)", (username,))
    shipments = cursor.fetchall()
    return render_template('user_dashboard.html', shipments=shipments)

if __name__ == '__main__':
    app.run(debug=True)
