from app import db
import datetime

class LightSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auto = db.Column(db.String(64), index=True)
    frequency = db.Column(db.Integer, index=True)
    
    def __repr__(self):
        return '<LightSetting {}>'.format(self.id)
    
    def __init__(self, auto, frequency):
        self.auto = auto
        self.frequency= frequency
        
    def as_dict(self):
        return {"id": self.id, "auto": self.auto, "frequency": self.frequency}
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
     
class WateringSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(db.Integer, index=True)
    frequency = db.Column(db.Integer, index=True)
    duration = db.Column(db.Float, index=True)
    
    def __repr__(self):
        return '<WateringSetting {}>'.format(self.id)
    
    def as_dict(self):
        return {"id": self.id, "zone": self.zone, "frequency": self.frequency, "duration": self.duration}
        
class MoistureData(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	datetime = db.Column(db.DateTime, index=True)
	sensor = db.Column(db.Integer, index=True)
	value = db.Column(db.Integer, index=True)

class DailyLog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	datetime = db.Column(db.DateTime, index=True)
	PH = db.Column(db.Float, index=True)
	TDS = db.Column(db.Integer, index=True)
