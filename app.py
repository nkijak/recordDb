from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Artist %r>' % self.name

class ArtistSchema(ma.ModelSchema):
    class Meta:
        model = Artist

artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
    artist = db.relationship('Artist', backref=db.backref('albums', lazy=True))

    def __repr__(self):
        return '<Album %r>' % self.name

class AlbumSchema(ma.ModelSchema):
    class Meta:
        model = Album

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)


@app.route('/api/albums', methods=['GET', 'POST'])
def albums():
    if request.method == 'GET':
        return _list(albums_schema)
    return _new(album_schema)

def _list(schema):
    _all = schema.Meta.model.query.all()
    result = schema.dump(_all)
    return schema.jsonify(result.data)

def _new(schema):
    if request.is_json:
        data = request.json
    else:
        data = request.form
    results = schema.load(data)
    if results.errors:
        abort(400, jsonify(results.errors))
    db.session.add(results.data)
    db.session.commit()
    return schema.jsonify(results.data)

@app.route('/api/albums/<id>')
def album_detail(id):
    album = Album.get(id)
    return album_schema.jsonify(album)

@app.route('/api/artists', methods=['GET', 'POST'])
def artists():
    if request.method == 'GET':
        return _list(artists_schema)
    return _new(artist_schema)
        
def _list_artists():
    all_artists = Artist.all()
    result = artsts_schema.dump(all_artists)
    return jsonify(result.data)

@app.route('/api/artist/<id>')
def artist_detail(id):
    artist = Artist.get(id)
    return artist_schema.jsonify(artist)
