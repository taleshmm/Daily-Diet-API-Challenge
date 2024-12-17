from database import db


class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))
    date = db.Column(db.DateTime, nullable=False)
    is_inside_diet = db.Column(db.Boolean, nullable=False, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
