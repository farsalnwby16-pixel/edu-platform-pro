from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "المنصة تعمل بكفاءة عالية!"

if __name__ == "__main__":
    app.run()

