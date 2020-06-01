from . import db

class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(200), unique=True, nullable=False)
    image_serial = db.Column(db.String(200), unique=True, nullable=False)
    predicted_main_tag = db.Column(db.Integer)
    actual_main_tag = db.Column(db.Integer)
    predicted_tags = db.relationship("PredictedTags", backref="image", lazy=True)
    actual_tags = db.relationship("ActualTags", backref="image", lazy=True)

    def __repr__(self):
        return "Image Name: {}, Image Number: {}".format(self.original_name, self.image_serial)

class PredictedTags(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("image.id"), nullable=False)
    tag_name = db.Column(db.String(100), nullable=False)
    tag_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "Tag Name: {}, Tag Number{}".format(self.tag_name, self.tag_number)

class ActualTags(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("image.id"), nullable=False)
    tag_name = db.Column(db.String(100), nullable=False)
    tag_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "Tag Name: {}, Tag Number{}".format(self.tag_name, self.tag_number)