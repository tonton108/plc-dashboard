# models.py
from backend.db import db
from datetime import datetime

class Equipment(db.Model):
    __tablename__ = 'equipments'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(50), unique=True, nullable=False)
    manufacturer = db.Column(db.String(50))
    series = db.Column(db.String(50))
    ip = db.Column(db.String(100))
    mac_address = db.Column(db.String(50))  # 追加
    hostname = db.Column(db.String(100))    # 追加
    port = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    status = db.Column(db.String(50), default="正常")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, equipment_id, manufacturer="", series="", ip="", mac_address="", hostname="", port=0, interval=60, status="正常"):
        self.equipment_id = equipment_id
        self.manufacturer = manufacturer
        self.series = series
        self.ip = ip
        self.mac_address = mac_address
        self.hostname = hostname
        self.port = port
        self.interval = interval
        self.status = status

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'))  # equipments.id を参照
    current = db.Column(db.Float)
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)