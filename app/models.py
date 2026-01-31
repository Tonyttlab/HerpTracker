# Database Models for HerpTracker
from datetime import datetime, date
from app import db


class Reptile(db.Model):
    """Reptile model - main entity for tracking."""
    __tablename__ = 'reptiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    species = db.Column(db.String(100), nullable=False)
    mutation = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedings = db.relationship('Feeding', backref='reptile', lazy='dynamic', 
                               cascade='all, delete-orphan', order_by='desc(Feeding.recorded_at)')
    sheddings = db.relationship('Shedding', backref='reptile', lazy='dynamic',
                                cascade='all, delete-orphan', order_by='desc(Shedding.recorded_at)')
    measurements = db.relationship('Measurement', backref='reptile', lazy='dynamic',
                                   cascade='all, delete-orphan', order_by='desc(Measurement.recorded_at)')
    defecations = db.relationship('Defecation', backref='reptile', lazy='dynamic',
                                  cascade='all, delete-orphan', order_by='desc(Defecation.recorded_at)')
    breedings = db.relationship('Breeding', backref='reptile', lazy='dynamic',
                                cascade='all, delete-orphan', order_by='desc(Breeding.recorded_at)')
    cleanings = db.relationship('Cleaning', backref='reptile', lazy='dynamic',
                                cascade='all, delete-orphan', order_by='desc(Cleaning.recorded_at)')
    
    def days_since_last_feeding(self):
        """Calculate days since last feeding."""
        last = self.feedings.first()
        if not last:
            return None
        delta = datetime.utcnow() - last.recorded_at
        return delta.days
    
    def days_since_last_shedding(self):
        """Calculate days since last shedding."""
        last = self.sheddings.first()
        if not last:
            return None
        delta = datetime.utcnow() - last.recorded_at
        return delta.days
    
    def days_since_last_defecation(self):
        """Calculate days since last defecation."""
        last = self.defecations.first()
        if not last:
            return None
        delta = datetime.utcnow() - last.recorded_at
        return delta.days
    
    def days_since_last_full_clean(self):
        """Calculate days since last full cleaning."""
        last = self.cleanings.filter_by(cleaning_type='full').first()
        if not last:
            return None
        delta = datetime.utcnow() - last.recorded_at
        return delta.days
    
    def latest_measurement(self):
        """Get the most recent measurement."""
        return self.measurements.first()
    
    def age_days(self):
        """Calculate age in days."""
        if not self.date_of_birth:
            return None
        delta = date.today() - self.date_of_birth
        return delta.days
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'species': self.species,
            'mutation': self.mutation,
            'gender': self.gender,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'days_since_feeding': self.days_since_last_feeding(),
            'days_since_shedding': self.days_since_last_shedding(),
            'days_since_defecation': self.days_since_last_defecation(),
            'age_days': self.age_days()
        }


class Feeding(db.Model):
    """Feeding record - immutable."""
    __tablename__ = 'feedings'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    food_type = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'food_type': self.food_type,
            'notes': self.notes
        }


class Shedding(db.Model):
    """Shedding record - immutable."""
    __tablename__ = 'sheddings'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    complete = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'complete': self.complete,
            'notes': self.notes
        }


class Measurement(db.Model):
    """Size measurement record - immutable."""
    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    length_cm = db.Column(db.Float, nullable=True)
    weight_g = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'length_cm': self.length_cm,
            'weight_g': self.weight_g,
            'notes': self.notes
        }


class Defecation(db.Model):
    """Defecation record - immutable."""
    __tablename__ = 'defecations'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'notes': self.notes
        }


class Breeding(db.Model):
    """Breeding record."""
    __tablename__ = 'breedings'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'notes': self.notes
        }


class Cleaning(db.Model):
    """Cage cleaning record."""
    __tablename__ = 'cleanings'
    
    id = db.Column(db.Integer, primary_key=True)
    reptile_id = db.Column(db.Integer, db.ForeignKey('reptiles.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cleaning_type = db.Column(db.String(50), nullable=False, default='spot') # 'full' or 'spot'
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reptile_id': self.reptile_id,
            'recorded_at': self.recorded_at.isoformat(),
            'cleaning_type': self.cleaning_type,
            'notes': self.notes
        }
