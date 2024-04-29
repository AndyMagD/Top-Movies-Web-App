import requests
from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


#CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)

##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Float, nullable=False, default=0.0)
    year = db.Column(db.Float, nullable=False)
    review = db.Column(db.String(100), nullable=False, default='')
    img_url = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


class AddMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    ranking = FloatField('Ranking', validators=[DataRequired()])
    year = FloatField('Year', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

class RateMovieForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])  # Add the review field
    submit = SubmitField('Submit Rating')

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    movies = Movie.query.all()  # Query all movies from the database
    return render_template("index.html", title="Home", message="Welcome to my website!", movies=movies)

@app.route("/edit/<int:movie_id>", methods=['GET', 'POST'])
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = RateMovieForm()

    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))  # Redirect to the homepage after updating

    return render_template("edit.html", title="Edit Movie Rating", form=form, movie=movie)


API_KEY = "eef4080521c5734bc14485c25854457d"
API_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(API_URL, params={"api_key": API_KEY, "query": movie_title})
        movie_data = response.json()["results"]
        return render_template("select.html", options=movie_data)
    return render_template("add.html", form=form)


@app.route("/find", methods=["POST"])
def find_movie():
    selected_movie_id = request.form.get("selected_movie_id")
    if selected_movie_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{selected_movie_id}"
        response = requests.get(movie_api_url, params={"api_key": API_KEY})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=int(data.get("release_date").split("-")[0]) if data.get("release_date") else None,
            img_url=f"{MOVIE_DB_IMAGE_URL}{data.get('poster_path')}" if data.get("poster_path") else None,
            description=data.get("overview")
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit_movie", movie_id=new_movie.id))
    return redirect(url_for("add_movie"))


if __name__ == '__main__':
    app.run(debug=True)
