from store.citizens.app import create_app, db, ma

app = create_app()
db.init_app(app)
ma.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)

