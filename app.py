import sqlite3
import os
from flask import Flask, request, render_template_string, redirect, session
import pickle
import subprocess

app = Flask(__name__)
app.secret_key = "hardcoded_secret_key_123"  # VULNERABILITY: Hardcoded secret

# VULNERABILITY: SQL Injection possible
def init_db():
    conn = sqlite3.connect('fruits.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fruits (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            is_admin INTEGER
        )
    ''')
    
    # Add sample data
    cursor.execute("DELETE FROM fruits")
    cursor.execute("INSERT INTO fruits VALUES (1, 'Apple', 1.50, 100)")
    cursor.execute("INSERT INTO fruits VALUES (2, 'Banana', 0.75, 150)")
    cursor.execute("INSERT INTO fruits VALUES (3, 'Orange', 2.00, 80)")
    cursor.execute("INSERT INTO fruits VALUES (4, 'Mango', 3.50, 50)")
    
    cursor.execute("DELETE FROM users")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'admin123', 1)")
    cursor.execute("INSERT INTO users VALUES (2, 'user', 'password', 0)")
    
    conn.commit()
    conn.close()

# VULNERABILITY: SQL Injection
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABILITY: SQL Injection - no parameterization
        conn = sqlite3.connect('fruits.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            session['is_admin'] = user[3]
            return redirect('/')
        else:
            error_msg = "Invalid credentials!"
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Fruit Shop</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                .login-container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    width: 100%;
                    max-width: 400px;
                }
                .login-header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .login-header h1 {
                    color: #333;
                    font-size: 28px;
                    margin-bottom: 10px;
                }
                .login-header .icon {
                    font-size: 50px;
                    margin-bottom: 10px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-group label {
                    display: block;
                    color: #555;
                    margin-bottom: 8px;
                    font-weight: 500;
                }
                .form-group input {
                    width: 100%;
                    padding: 12px 15px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 16px;
                    transition: border-color 0.3s;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                .btn-login {
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .btn-login:hover {
                    transform: translateY(-2px);
                }
                .error-msg {
                    background: #fee;
                    color: #c33;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .back-link {
                    text-align: center;
                    margin-top: 20px;
                }
                .back-link a {
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 500;
                }
                .back-link a:hover {
                    text-decoration: underline;
                }
                .hint-box {
                    background: #f0f7ff;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin-top: 20px;
                    border-radius: 5px;
                }
                .hint-box h3 {
                    color: #667eea;
                    font-size: 14px;
                    margin-bottom: 8px;
                }
                .hint-box p {
                    color: #666;
                    font-size: 13px;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="login-header">
                    <div class="icon">🍎</div>
                    <h1>Fruit Shop Login</h1>
                </div>
                {% if error_msg %}
                <div class="error-msg">{{ error_msg }}</div>
                {% endif %}
                <form method="post">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" placeholder="Enter your username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" placeholder="Enter your password" required>
                    </div>
                    <button type="submit" class="btn-login">Login</button>
                </form>
                <div class="hint-box">
                    <h3>🔐 Test Credentials:</h3>
                    <p><strong>Admin:</strong> admin / admin123<br>
                    <strong>User:</strong> user / password<br><br>
                    <strong>SQL Injection Test:</strong><br>
                    Username: <code>admin' OR '1'='1' --</code></p>
                </div>
                <div class="back-link">
                    <a href="/">← Back to Shop</a>
                </div>
            </div>
        </body>
        </html>
    ''', error_msg=error_msg)

# VULNERABILITY: XSS (Cross-Site Scripting)
@app.route('/')
def index():
    conn = sqlite3.connect('fruits.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fruits")
    fruits = cursor.fetchall()
    conn.close()
    
    search = request.args.get('search', '')
    username = session.get('username', 'Guest')
    is_admin = session.get('is_admin', 0)
    
    # VULNERABILITY: XSS - unsanitized user input
    html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fruit Shop - Home</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .navbar {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px 40px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                }}
                .navbar h1 {{
                    font-size: 32px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .user-info {{
                    display: flex;
                    gap: 15px;
                    align-items: center;
                }}
                .user-badge {{
                    background: rgba(255,255,255,0.2);
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 14px;
                }}
                .admin-badge {{
                    background: #ffd700;
                    color: #333;
                    padding: 5px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .nav-links a {{
                    color: white;
                    text-decoration: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.1);
                    transition: background 0.3s;
                }}
                .nav-links a:hover {{
                    background: rgba(255,255,255,0.2);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .search-box {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                .search-box form {{
                    display: flex;
                    gap: 10px;
                }}
                .search-box input[type="text"] {{
                    flex: 1;
                    padding: 12px 20px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 16px;
                }}
                .search-box input[type="text"]:focus {{
                    outline: none;
                    border-color: #667eea;
                }}
                .search-box button {{
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.2s;
                }}
                .search-box button:hover {{
                    transform: translateY(-2px);
                }}
                .search-result {{
                    background: #f0f7ff;
                    padding: 10px 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 4px solid #667eea;
                }}
                .fruit-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 25px;
                    margin-top: 20px;
                }}
                .fruit-card {{
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                    transition: transform 0.3s, box-shadow 0.3s;
                }}
                .fruit-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                }}
                .fruit-icon {{
                    font-size: 60px;
                    text-align: center;
                    margin-bottom: 15px;
                }}
                .fruit-name {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 10px;
                    text-align: center;
                }}
                .fruit-price {{
                    font-size: 28px;
                    color: #667eea;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 8px;
                }}
                .fruit-stock {{
                    text-align: center;
                    color: #666;
                    margin-bottom: 15px;
                    font-size: 14px;
                }}
                .stock-high {{
                    color: #28a745;
                }}
                .stock-low {{
                    color: #ffc107;
                }}
                .stock-out {{
                    color: #dc3545;
                }}
                .buy-button {{
                    display: block;
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    transition: transform 0.2s;
                }}
                .buy-button:hover {{
                    transform: scale(1.05);
                }}
                .buy-button.disabled {{
                    background: #ccc;
                    cursor: not-allowed;
                    pointer-events: none;
                }}
                .no-results {{
                    text-align: center;
                    padding: 60px 20px;
                    color: #999;
                    font-size: 18px;
                }}
            </style>
        </head>
        <body>
            <div class="navbar">
                <h1>🍎 Fruit Shop</h1>
                <div class="user-info">
                    <div class="user-badge">👤 {username}</div>
                    {('<span class="admin-badge">ADMIN</span>' if is_admin else '')}
                    <div class="nav-links">
                        <a href="/login">Login</a>
                        {('<a href="/admin">Admin Panel</a>' if is_admin else '')}
                    </div>
                </div>
            </div>
            
            <div class="container">
                <div class="search-box">
                    <form>
                        <input type="text" name="search" value="{search}" placeholder="Search for fruits... (Try: <script>alert('XSS')</script>)">
                        <button type="submit">🔍 Search</button>
                    </form>
                </div>
                
                {('<div class="search-result">Search results for: ' + search + '</div>' if search else '')}
                
                <div class="fruit-grid">
    '''
    
    fruit_icons = {
        'Apple': '🍎',
        'Banana': '🍌',
        'Orange': '🍊',
        'Mango': '🥭'
    }
    
    found_results = False
    for fruit in fruits:
        if search.lower() in fruit[1].lower() or search == '':
            found_results = True
            stock_class = 'stock-high' if fruit[3] > 50 else ('stock-low' if fruit[3] > 0 else 'stock-out')
            stock_text = f'{fruit[3]} in stock' if fruit[3] > 0 else 'Out of stock'
            icon = fruit_icons.get(fruit[1], '🍇')
            button_class = '' if fruit[3] > 0 else 'disabled'
            
            html += f'''
                <div class="fruit-card">
                    <div class="fruit-icon">{icon}</div>
                    <div class="fruit-name">{fruit[1]}</div>
                    <div class="fruit-price">${fruit[2]:.2f}</div>
                    <div class="fruit-stock {stock_class}">{stock_text}</div>
                    <a href="/buy?id={fruit[0]}" class="buy-button {button_class}">
                        🛒 Add to Cart
                    </a>
                </div>
            '''
    
    if not found_results:
        html += '<div class="no-results">No fruits found matching your search 😢</div>'
    
    html += '''
                </div>
            </div>
        </body>
        </html>
    '''
    
    return render_template_string(html)

# VULNERABILITY: Insecure Direct Object Reference (IDOR)
@app.route('/buy')
def buy():
    fruit_id = request.args.get('id')
    
    # VULNERABILITY: SQL Injection
    conn = sqlite3.connect('fruits.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM fruits WHERE id={fruit_id}"
    cursor.execute(query)
    fruit = cursor.fetchone()
    
    if fruit and fruit[3] > 0:
        # VULNERABILITY: No authentication check
        cursor.execute(f"UPDATE fruits SET stock=stock-1 WHERE id={fruit_id}")
        conn.commit()
        conn.close()
        
        fruit_icons = {
            'Apple': '🍎',
            'Banana': '🍌',
            'Orange': '🍊',
            'Mango': '🥭'
        }
        icon = fruit_icons.get(fruit[1], '🍇')
        
        return render_template_string(f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Purchase Successful</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }}
                    .success-box {{
                        background: white;
                        padding: 50px;
                        border-radius: 20px;
                        text-align: center;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        max-width: 500px;
                        animation: slideIn 0.5s ease;
                    }}
                    @keyframes slideIn {{
                        from {{
                            opacity: 0;
                            transform: translateY(-20px);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateY(0);
                        }}
                    }}
                    .success-icon {{
                        font-size: 80px;
                        margin-bottom: 20px;
                        animation: bounce 1s ease;
                    }}
                    @keyframes bounce {{
                        0%, 100% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.2); }}
                    }}
                    h1 {{
                        color: #28a745;
                        margin-bottom: 15px;
                        font-size: 32px;
                    }}
                    .purchase-details {{
                        background: #f8f9fa;
                        padding: 25px;
                        border-radius: 12px;
                        margin: 25px 0;
                    }}
                    .fruit-icon {{
                        font-size: 60px;
                        margin-bottom: 15px;
                    }}
                    .fruit-name {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #333;
                        margin-bottom: 10px;
                    }}
                    .fruit-price {{
                        font-size: 24px;
                        color: #667eea;
                        font-weight: bold;
                    }}
                    .message {{
                        color: #666;
                        font-size: 16px;
                        margin-bottom: 30px;
                    }}
                    .btn-continue {{
                        display: inline-block;
                        padding: 15px 40px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 10px;
                        font-size: 18px;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }}
                    .btn-continue:hover {{
                        transform: translateY(-3px);
                    }}
                    .vulnerability-note {{
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 12px;
                        margin-top: 25px;
                        border-radius: 5px;
                        font-size: 13px;
                        color: #856404;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <div class="success-icon">✅</div>
                    <h1>Purchase Successful!</h1>
                    
                    <div class="purchase-details">
                        <div class="fruit-icon">{icon}</div>
                        <div class="fruit-name">{fruit[1]}</div>
                        <div class="fruit-price">${fruit[2]:.2f}</div>
                    </div>
                    
                    <p class="message">Your order has been placed successfully!</p>
                    
                    <a href="/" class="btn-continue">🛍️ Continue Shopping</a>
                    
                    <div class="vulnerability-note">
                        <strong>⚠️ Security Note:</strong> This purchase was completed without authentication! This demonstrates broken access control and IDOR vulnerabilities.
                    </div>
                </div>
            </body>
            </html>
        ''')
    
    conn.close()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Purchase Failed</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .error-box {
                    background: white;
                    padding: 50px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                .error-icon {
                    font-size: 80px;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #dc3545;
                    margin-bottom: 15px;
                }
                p {
                    color: #666;
                    margin-bottom: 30px;
                }
                a {
                    display: inline-block;
                    padding: 15px 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <div class="error-box">
                <div class="error-icon">❌</div>
                <h1>Purchase Failed</h1>
                <p>Item is out of stock or invalid!</p>
                <a href="/">← Back to Shop</a>
            </div>
        </body>
        </html>
    ''')

# VULNERABILITY: Broken Access Control
@app.route('/admin')
def admin():
    # VULNERABILITY: Weak authentication check, can be bypassed
    if session.get('is_admin'):
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Panel - Fruit Shop</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    .admin-header {
                        background: white;
                        padding: 30px;
                        border-radius: 15px 15px 0 0;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                    }
                    .admin-header h1 {
                        color: #1e3c72;
                        font-size: 32px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    .admin-header p {
                        color: #666;
                        margin-top: 10px;
                    }
                    .admin-content {
                        background: white;
                        padding: 30px;
                        border-radius: 0 0 15px 15px;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                        margin-top: 2px;
                    }
                    .warning-box {
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin-bottom: 25px;
                        border-radius: 5px;
                    }
                    .warning-box h3 {
                        color: #856404;
                        margin-bottom: 8px;
                        font-size: 16px;
                    }
                    .warning-box p {
                        color: #856404;
                        font-size: 14px;
                    }
                    .command-section {
                        background: #f8f9fa;
                        padding: 25px;
                        border-radius: 10px;
                        border: 2px solid #e9ecef;
                    }
                    .command-section h2 {
                        color: #333;
                        margin-bottom: 15px;
                        font-size: 20px;
                    }
                    .form-group {
                        margin-bottom: 20px;
                    }
                    .form-group label {
                        display: block;
                        color: #555;
                        margin-bottom: 8px;
                        font-weight: 500;
                    }
                    .form-group input {
                        width: 100%;
                        padding: 12px 15px;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 16px;
                        font-family: 'Courier New', monospace;
                        background: white;
                    }
                    .form-group input:focus {
                        outline: none;
                        border-color: #1e3c72;
                    }
                    .btn-execute {
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: transform 0.2s;
                    }
                    .btn-execute:hover {
                        transform: translateY(-2px);
                    }
                    .example-commands {
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin-top: 20px;
                        border: 1px solid #dee2e6;
                    }
                    .example-commands h3 {
                        color: #1e3c72;
                        font-size: 14px;
                        margin-bottom: 10px;
                    }
                    .example-commands code {
                        display: block;
                        background: #f8f9fa;
                        padding: 8px 12px;
                        margin: 5px 0;
                        border-radius: 4px;
                        font-family: 'Courier New', monospace;
                        color: #d63384;
                        border-left: 3px solid #1e3c72;
                    }
                    .back-link {
                        text-align: center;
                        margin-top: 20px;
                    }
                    .back-link a {
                        color: white;
                        text-decoration: none;
                        background: rgba(255,255,255,0.2);
                        padding: 10px 20px;
                        border-radius: 8px;
                        display: inline-block;
                        transition: background 0.3s;
                    }
                    .back-link a:hover {
                        background: rgba(255,255,255,0.3);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="admin-header">
                        <h1>⚙️ Admin Control Panel</h1>
                        <p>System Management & Command Execution</p>
                    </div>
                    <div class="admin-content">
                        <div class="warning-box">
                            <h3>⚠️ Vulnerability Warning</h3>
                            <p>This interface is vulnerable to command injection attacks. Any command entered will be executed on the server!</p>
                        </div>
                        
                        <div class="command-section">
                            <h2>🖥️ Execute System Command</h2>
                            <form action="/admin/command" method="post">
                                <div class="form-group">
                                    <label for="cmd">Command:</label>
                                    <input type="text" id="cmd" name="cmd" placeholder="Enter system command..." required>
                                </div>
                                <button type="submit" class="btn-execute">▶️ Execute Command</button>
                            </form>
                            
                            <div class="example-commands">
                                <h3>💡 Example Commands:</h3>
                                <code>ls -la</code>
                                <code>pwd</code>
                                <code>whoami</code>
                                <code>cat app.py</code>
                                <code>ps aux</code>
                            </div>
                        </div>
                    </div>
                    <div class="back-link">
                        <a href="/">← Back to Shop</a>
                    </div>
                </div>
            </body>
            </html>
        ''')
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Access Denied</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .error-box {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }
                .error-icon {
                    font-size: 60px;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #dc3545;
                    margin-bottom: 15px;
                }
                p {
                    color: #666;
                    margin-bottom: 25px;
                }
                a {
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: transform 0.2s;
                }
                a:hover {
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="error-box">
                <div class="error-icon">🚫</div>
                <h1>Access Denied</h1>
                <p>You need administrator privileges to access this page.</p>
                <a href="/login">Login as Admin</a>
            </div>
        </body>
        </html>
    ''')

# VULNERABILITY: Command Injection
@app.route('/admin/command', methods=['POST'])
def admin_command():
    if session.get('is_admin'):
        cmd = request.form['cmd']
        # VULNERABILITY: OS Command Injection
        result = subprocess.getoutput(cmd)
        return render_template_string(f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Command Result - Admin Panel</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 900px;
                        margin: 0 auto;
                    }}
                    .result-header {{
                        background: white;
                        padding: 25px;
                        border-radius: 15px 15px 0 0;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                    }}
                    .result-header h1 {{
                        color: #1e3c72;
                        font-size: 24px;
                        margin-bottom: 10px;
                    }}
                    .command-executed {{
                        background: #f8f9fa;
                        padding: 12px 15px;
                        border-radius: 8px;
                        font-family: 'Courier New', monospace;
                        color: #d63384;
                        border-left: 4px solid #28a745;
                    }}
                    .result-content {{
                        background: white;
                        padding: 25px;
                        border-radius: 0 0 15px 15px;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                        margin-top: 2px;
                    }}
                    .output-box {{
                        background: #1e1e1e;
                        color: #d4d4d4;
                        padding: 20px;
                        border-radius: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 14px;
                        line-height: 1.6;
                        overflow-x: auto;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        max-height: 500px;
                        overflow-y: auto;
                        border: 2px solid #333;
                    }}
                    .output-box::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    .output-box::-webkit-scrollbar-track {{
                        background: #2d2d2d;
                    }}
                    .output-box::-webkit-scrollbar-thumb {{
                        background: #555;
                        border-radius: 4px;
                    }}
                    .button-group {{
                        display: flex;
                        gap: 15px;
                        margin-top: 20px;
                    }}
                    .btn {{
                        padding: 12px 25px;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                        transition: transform 0.2s;
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                    }}
                    .btn-primary {{
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                    }}
                    .btn-secondary {{
                        background: #6c757d;
                        color: white;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="result-header">
                        <h1>✅ Command Executed Successfully</h1>
                        <div class="command-executed">$ {cmd}</div>
                    </div>
                    <div class="result-content">
                        <h2 style="margin-bottom: 15px; color: #333;">Output:</h2>
                        <div class="output-box">{result if result else '(No output)'}</div>
                        <div class="button-group">
                            <a href="/admin" class="btn btn-primary">← Execute Another Command</a>
                            <a href="/" class="btn btn-secondary">Back to Shop</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        ''')
    return "Access denied!"

# VULNERABILITY: Insecure Deserialization
@app.route('/export')
def export():
    conn = sqlite3.connect('fruits.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fruits")
    fruits = cursor.fetchall()
    conn.close()
    
    # VULNERABILITY: Pickle serialization can be exploited
    data = pickle.dumps(fruits)
    return data

# VULNERABILITY: Insecure Deserialization
@app.route('/import', methods=['POST'])
def import_data():
    data = request.get_data()
    # VULNERABILITY: Unpickling untrusted data
    fruits = pickle.loads(data)
    return f"Imported {len(fruits)} items"

if __name__ == '__main__':
    init_db()
    # VULNERABILITY: Debug mode enabled, 0.0.0.0 binding
    app.run(debug=True, host='0.0.0.0', port=5000)