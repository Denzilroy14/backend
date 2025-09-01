#This is where backend code exists
from flask import*
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
SPECIFIED_DATE='2025-08-28'

app=Flask(__name__)
CORS(app,origins=['*'])

app.config['UPLOADER'] = os.path.join(app.root_path, 'uploads')
def init_db():
    con=sqlite3.connect('database.db')
    con.execute('CREATE TABLE IF NOT EXISTS registration(name TEXT,age INTEGER,email TEXT,feedback TEXT,image TEXT)')
    con.commit()
init_db()

@app.route('/register',methods=['POST'])
def register():
    name=request.form['name']
    age=request.form['age']
    email=request.form['email']
    feedback=request.form['feedback']
    image=request.files['image']
    date=request.form['date']
    time=request.form['time']

    filename=image.filename
    filepath=os.path.join(app.config['UPLOADER'],filename)
    image.save(filepath)
  
    d=datetime.strptime(date,'%Y-%m-%d')
    
    if d.weekday()==6:
        return jsonify({'message':'No appoinmnets on sundays'})
    elif d==SPECIFIED_DATE:
        return jsonify({'message':'Sorry appoinmnets cannot be booked at this time slot'})
    
    conn=sqlite3.connect('database.db')
    curr=conn.cursor()
    curr.execute('INSERT INTO registration(name,age,email,feedback,image,date,time)VALUES(?,?,?,?,?,?,?)',(name,age,email,feedback,filename,date,time))
    #curr.execute('INSERT INTO registration(date,time)VALUES(?,?) WHERE name=?',(d,time,name,))
    conn.commit()

    return jsonify({'message':'registration successfull'})

@app.route('/admin',methods=['GET'])
def get_users():
    con=sqlite3.connect('database.db')
    cur=con.cursor()
    data=cur.execute('SELECT * FROM registration').fetchall()
    user_list=[]
    for user in data:
        user_list.append({
            'name':user[0],
            'age':user[1],
            'email':user[2],
            'feedback':user[3],
            'image_url':f'https://frontendbackendeg.pythonanywhere.com/register/uploads/{user[4]}',
            'date':user[5],
            'time':user[6]
            })
    return jsonify(user_list)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADER'],filename)

#con=sqlite3.connect('database.db')
#cur=con.cursor()
#cur.execute('UPDATE registration SET time=?,date=? WHERE name=?',('12:34:44','26/08/25','Roy'))
#con.commit()
#for row in cur.execute('PRAGMA table_info(registration)'):
 #   print(row)
#cur.execute('ALTER TABLE registration ADD COLUMN time TEXT')
#con.commit()

if __name__=='__main__':
    if not os.path.exists(app.config['UPLOADER']):
        os.mkdir(app.config['UPLOADER'])
    app.run(debug=True)



























































'''from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# Simulate a database
orders = []

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.json
    orders.append(data)
    return jsonify({'message': 'Order added!'}), 201

if __name__ == '__main__':
    app.run(debug=True)

For a student form

app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute(
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL
        )
    )
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')

    try:
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', (name, email, age))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User added successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id, name, email, age FROM users')
    users = [{'id': row[0], 'name': row[1], 'email': row[2], 'age': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(users)

************************************************************************************************
frontend\src\app.js
import React, { useState, useEffect } from 'react';

function App() {
  const [users, setUsers] = useState([]);
  const [formData, setFormData] = useState({ name: '', email: '', age: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://localhost:5000/api/users')
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    fetch('http://localhost:5000/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...formData, age: parseInt(formData.age, 10) })
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json();
          setError(err.error);
        } else {
          const newUser = await res.json();
          fetch('http://localhost:5000/api/users')
            .then(res => res.json())
            .then(data => setUsers(data));
          setFormData({ name: '', email: '', age: '' });
        }
      });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>User Registration</h1>
      <form onSubmit={handleSubmit}>
        <input name="name" value={formData.name} onChange={handleChange} placeholder="Name" required />
        <input name="email" value={formData.email} onChange={handleChange} placeholder="Email" type="email" required />
        <input name="age" value={formData.age} onChange={handleChange} placeholder="Age" type="number" required />
        <button type="submit">Register</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <h2>Registered Users</h2>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.name} ({u.email}, {u.age} years old)</li>
        ))}
      </ul>
    </div>
  );
}

export default App;

'''