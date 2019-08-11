from app import db, ma
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Citizen(db.Model):
    """ Citizen Model """

    __tablename__ = "citizens"
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, nullable=False)
    town = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    relatives = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))
    import_id = db.Column(db.String(100), nullable=False)


class CitizenSchema(ma.ModelSchema):
    class Meta:
        model = Citizen








