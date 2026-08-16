import os,sqlite3,secrets
from flask import Flask,request,redirect,url_for,session,render_template,flash
from werkzeug.utils import secure_filename
BASE=os.path.dirname(os.path.abspath(__file__)); DB=os.path.join(BASE,"vertex.db"); UP=os.path.join(BASE,"static","uploads"); os.makedirs(UP,exist_ok=True)
app=Flask(__name__); app.secret_key=os.getenv("SECRET_KEY",secrets.token_hex(32)); USER=os.getenv("ADMIN_USER","admin"); PASS=os.getenv("ADMIN_PASS","ChangeMe123!")
CATS=[("lighting","Lighting"),("cables","Cables & Wiring"),("switches","Switches & Sockets"),("protection","Protection"),("tools","Electrical Tools"),("solar","Solar Equipment")]
SERV=[("Electrical installation supplies","Materials for domestic, commercial and contractor projects."),("Solar equipment","Panels, batteries, inverters and charge controllers."),("Product sourcing","Send the product name or a photo and ask us to source it."),("Electrical tools","Testers, pliers, multimeters and installation tools."),("Customer enquiries","Confirm current price, stock and suitable options."),("Nairobi delivery","Ask us about delivery arrangements.")]
def D(): c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 c=D(); c.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,category TEXT,price REAL,stock INTEGER,description TEXT,specs TEXT,image TEXT,active INTEGER DEFAULT 1)"); c.execute("CREATE TABLE IF NOT EXISTS enquiries(id INTEGER PRIMARY KEY AUTOINCREMENT,customer TEXT,phone TEXT,message TEXT,products TEXT,created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)");
 if c.execute("SELECT COUNT(*) FROM products").fetchone()[0]==0:
  seed=[("LED Bulb 12W","lighting",250,50,"Energy-efficient LED bulb.","12W\n220–240V\nLED"),("LED Flood Light 100W","lighting",2500,30,"High-output outdoor floodlight.","100W\nIP65"),("Electrical Cable","cables",0,0,"Cable options for installations.","Multiple sizes"),("Wall Switch","switches",350,75,"Wall switch for common installations.","Multiple designs"),("Socket Outlet","switches",350,75,"Socket outlets and accessories.","Multiple styles"),("Circuit Breaker","protection",650,40,"Electrical protection equipment.","Multiple ratings"),("Voltage Tester","tools",0,0,"Electrical testing tool.","Multiple models"),("Digital Multimeter","tools",1200,20,"Measurement and troubleshooting tool.","Digital\nMultiple functions"),("Solar Panel 200W","solar",15000,30,"Solar PV panel.","200W\nPV panel"),("Solar Inverter 1KVA","solar",18500,20,"Power conversion equipment.","1KVA"),("Solar Battery","solar",0,0,"Solar energy storage.","Multiple capacities"),("Solar Charge Controller","solar",0,0,"Solar charge management.","Multiple ratings")]; c.executemany("INSERT INTO products(name,category,price,stock,description,specs) VALUES(?,?,?,?,?,?)",seed)
 c.commit(); c.close()
def admin(f):
 from functools import wraps
 @wraps(f)
 def w(*a,**k): return f(*a,**k) if session.get("admin") else redirect(url_for("login",next=request.path))
 return w
@app.context_processor
def ctx(): return dict(categories=CATS,services=SERV,phone="0114 799 832",wa="254114799832")
@app.route("/")
def home(): c=D(); p=c.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC LIMIT 8").fetchall(); c.close(); return render_template("home.html",featured=p)
@app.route("/shop")
def shop():
 q=request.args.get("q",""); cat=request.args.get("category",""); sql="SELECT * FROM products WHERE active=1"; a=[]
 if cat: sql+=" AND category=?"; a.append(cat)
 if q: sql+=" AND (name LIKE ? OR description LIKE ?)"; a += ["%"+q+"%","%"+q+"%"]
 c=D(); p=c.execute(sql+" ORDER BY id DESC",a).fetchall(); c.close(); return render_template("shop.html",products=p,q=q,selected=cat)
@app.route("/product/<int:id>")
def product(id): c=D(); p=c.execute("SELECT * FROM products WHERE id=? AND active=1",(id,)).fetchone(); c.close(); return render_template("product.html",p=p) if p else ("Not found",404)
@app.route("/services")
def services(): return render_template("services.html")
@app.route("/contact")
def contact(): return render_template("contact.html")
@app.route("/admin/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  if request.form.get("username")==USER and request.form.get("password")==PASS: session["admin"]=1; return redirect(request.args.get("next") or "/admin")
  flash("Wrong login details")
 return render_template("login.html")
@app.route("/admin/logout")
def logout(): session.clear(); return redirect("/")
@app.route("/admin")
@admin
def dashboard(): c=D(); p=c.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC").fetchall(); s=(c.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0],c.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0],c.execute("SELECT COALESCE(SUM(stock),0) FROM products").fetchone()[0]); c.close(); return render_template("admin.html",products=p,stats=s)
@app.route("/admin/save",methods=["POST"])
@admin
def save():
 pid=request.form.get("id"); image=request.form.get("old_image",""); f=request.files.get("image")
 if f and f.filename:
  ext=os.path.splitext(secure_filename(f.filename))[1].lower();
  if ext not in [".jpg",".jpeg",".png",".webp"]: flash("Use JPG, PNG or WebP"); return redirect("/admin")
  fn=secrets.token_hex(8)+ext; f.save(os.path.join(UP,fn)); image="uploads/"+fn
 vals=(request.form.get("name"),request.form.get("category"),float(request.form.get("price") or 0),int(request.form.get("stock") or 0),request.form.get("description",""),request.form.get("specs",""),image)
 c=D();
 if pid: c.execute("UPDATE products SET name=?,category=?,price=?,stock=?,description=?,specs=?,image=? WHERE id=?",vals+(pid,))
 else: c.execute("INSERT INTO products(name,category,price,stock,description,specs,image) VALUES(?,?,?,?,?,?,?)",vals)
 c.commit(); c.close(); flash("Product saved"); return redirect("/admin")
@app.route("/admin/delete/<int:id>",methods=["POST"])
@admin
def delete(id): c=D(); c.execute("UPDATE products SET active=0 WHERE id=?",(id,)); c.commit(); c.close(); return redirect("/admin")
@app.route("/admin/enquiries")
@admin
def enquiries(): c=D(); r=c.execute("SELECT * FROM enquiries ORDER BY created DESC").fetchall(); c.close(); return render_template("enquiries.html",rows=r)
@app.route("/api/enquiry",methods=["POST"])
def api_enquiry():
 d=request.form; c=D(); c.execute("INSERT INTO enquiries(customer,phone,message,products) VALUES(?,?,?,?)",(d.get("customer",""),d.get("phone",""),d.get("message",""),d.get("products",""))); c.commit(); c.close(); return {"ok":True}
@app.route("/health")
def health(): return "OK"
if __name__=="__main__": init(); app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)))
