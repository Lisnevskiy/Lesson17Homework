from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    description = fields.String()
    trailer = fields.String()
    year = fields.Integer()
    rating = fields.Float()
    genre_id = fields.Integer()
    director_id = fields.Integer()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Integer()
    name = fields.String()


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        if director_id and genre_id:
            movies = Movie.query.filter_by(director_id=director_id, genre_id=genre_id).all()
            if not movies:
                return {'message': 'No movies found'}, 404
            movie_schema = MovieSchema(many=True)
            return movie_schema.dump(movies), 200

        if genre_id:
            movies = Movie.query.filter_by(genre_id=genre_id).all()
            if not movies:
                return {'message': 'No movies found'}, 404
            movie_schema = MovieSchema(many=True)
            return movie_schema.dump(movies), 200

        if director_id:
            movies = Movie.query.filter_by(director_id=director_id).all()
            if not movies:
                return {'message': 'No movies found'}, 404
            movie_schema = MovieSchema(many=True)
            return movie_schema.dump(movies), 200

        movies = Movie.query.all()
        if not movies:
            return {'message': 'No movies found'}, 404
        movie_schema = MovieSchema(many=True)
        return movie_schema.dump(movies), 200

    def post(self):
        reg_json = request.json
        new_movie = Movie(**reg_json)
        db.session.add(new_movie)
        db.session.commit()
        return '', 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return {'message': 'Movie not found'}, 404
        movie_schema = MovieSchema()
        return movie_schema.dump(movie), 200

    def put(self, mid):
        reg_json = request.json
        movie = Movie.query.get(mid)
        if not movie:
            return {'message': 'Movie not found'}, 404
        movie.title = reg_json.get('title')
        movie.description = reg_json.get('description')
        movie.trailer = reg_json.get('trailer')
        movie.year = reg_json.get('year')
        movie.rating = reg_json.get('rating')
        movie.genre_id = reg_json.get('genre_id')
        movie.director_id = reg_json.get('director_id')
        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return {'message': 'Movie not found'}, 404
        db.session.delete(movie)
        db.session.commit()
        return '', 204


@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        directors = Director.query.all()
        if not directors:
            return {'message': 'No directors found'}, 404
        director_schema = DirectorSchema(many=True)
        return director_schema.dump(directors), 200

    def post(self):
        reg_json = request.json
        new_director = Director(**reg_json)
        db.session.add(new_director)
        db.session.commit()
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        if not director:
            return {'message': 'Director not found'}, 404
        director_schema = DirectorSchema()
        return director_schema.dump(director), 200

    def put(self, did):
        reg_json = request.json
        director = Director.query.get(did)
        if not director:
            return {'message': 'Director not found'}, 404
        director.name = reg_json.get('name')
        db.session.commit()
        return '', 204

    def delete(self, did):
        director = Director.query.get(did)
        if not director:
            return {'message': 'Director not found'}, 404
        db.session.delete(director)
        db.session.commit()
        return '', 204


@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        genres = Genre.query.all()
        if not genres:
            return {'message': 'No genres found'}, 404
        genre_schema = GenreSchema(many=True)
        return genre_schema.dump(genres), 200

    def post(self):
        reg_json = request.json
        new_genre = Genre(**reg_json)
        db.session.add(new_genre)
        db.session.commit()
        return '', 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return {'message': 'Genre not found'}, 404
        genre_schema = GenreSchema()
        return genre_schema.dump(genre), 200

    def put(self, gid):
        reg_json = request.json
        genre = Genre.query.get(gid)
        if not genre:
            return {'message': 'Genre not found'}, 404
        genre.name = reg_json.get('name')
        db.session.commit()
        return '', 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return {'message': 'Genre not found'}, 404
        db.session.delete(genre)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    app.run(host=host, port=port, debug=True)
