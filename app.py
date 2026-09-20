from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "المنصة تعمل بنجاح!"

if __name__ == "__main__":
    app.run()

