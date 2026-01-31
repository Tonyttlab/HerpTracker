# Routes for HerpTracker
import os
import uuid
import csv
import io
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app import db
from app.models import Reptile, Feeding, Shedding, Measurement, Defecation, Breeding, Cleaning

main = Blueprint('main', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """Save uploaded image and return the filename."""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


# ============ Page Routes ============

@main.route('/')
def index():
    """Dashboard - show all reptiles."""
    reptiles = Reptile.query.order_by(Reptile.name).all()
    return render_template('index.html', reptiles=reptiles)


@main.route('/reptile/<int:reptile_id>')
def reptile_detail(reptile_id):
    """Reptile profile page."""
    reptile = Reptile.query.get_or_404(reptile_id)
    return render_template('reptile.html', reptile=reptile)


@main.route('/reptile/new')
def new_reptile():
    """New reptile form page."""
    return render_template('form.html', reptile=None, mode='create')


@main.route('/reptile/<int:reptile_id>/edit')
def edit_reptile(reptile_id):
    """Edit reptile form page."""
    reptile = Reptile.query.get_or_404(reptile_id)
    return render_template('form.html', reptile=reptile, mode='edit')


# ============ Export Route ============

@main.route('/export')
def export_data():
    """Export all data as a ZIP file containing CSVs."""
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Define models to export
        models = {
            'reptiles': Reptile,
            'feedings': Feeding,
            'sheddings': Shedding,
            'measurements': Measurement,
            'defecations': Defecation,
            'breedings': Breeding,
            'cleanings': Cleaning
        }
        
        for name, model in models.items():
            # Create CSV in memory
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            
            # Get column headers
            columns = [c.name for c in model.__table__.columns]
            writer.writerow(columns)
            
            # Write data rows
            records = model.query.all()
            for record in records:
                writer.writerow([getattr(record, col) for col in columns])
                
            # Add to ZIP
            zf.writestr(f'{name}.csv', csv_buffer.getvalue())
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'herptracker_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    )


# ============ API Routes - Reptile CRUD ============

@main.route('/api/reptile', methods=['POST'])
def create_reptile():
    """Create a new reptile."""
    try:
        name = request.form.get('name')
        species = request.form.get('species')
        
        if not name or not species:
            return jsonify({'error': 'Name and species are required'}), 400
        
        reptile = Reptile(
            name=name,
            species=species,
            mutation=request.form.get('mutation'),
            gender=request.form.get('gender'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() 
                          if request.form.get('date_of_birth') else None
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = save_image(file)
                if filename:
                    reptile.image_path = filename
        
        db.session.add(reptile)
        db.session.commit()
        
        return jsonify({'success': True, 'reptile': reptile.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>', methods=['PUT'])
def update_reptile(reptile_id):
    """Update an existing reptile."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        reptile.name = request.form.get('name', reptile.name)
        reptile.species = request.form.get('species', reptile.species)
        reptile.mutation = request.form.get('mutation', reptile.mutation)
        reptile.gender = request.form.get('gender', reptile.gender)
        
        if request.form.get('date_of_birth'):
            reptile.date_of_birth = datetime.strptime(
                request.form.get('date_of_birth'), '%Y-%m-%d'
            ).date()
        
        # Handle new image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                # Delete old image if exists
                if reptile.image_path:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], reptile.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = save_image(file)
                if filename:
                    reptile.image_path = filename
        
        db.session.commit()
        return jsonify({'success': True, 'reptile': reptile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>', methods=['DELETE'])
def delete_reptile(reptile_id):
    """Delete a reptile and all its records."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        # Delete image file if exists
        if reptile.image_path:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], reptile.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(reptile)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ API Routes - Records CRUD ============

@main.route('/api/reptile/<int:reptile_id>/feeding', methods=['POST'])
def add_feeding(reptile_id):
    """Add a feeding record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        feeding = Feeding(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            food_type=request.form.get('food_type'),
            notes=request.form.get('notes')
        )
        
        db.session.add(feeding)
        db.session.commit()
        
        return jsonify({'success': True, 'feeding': feeding.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>/shedding', methods=['POST'])
def add_shedding(reptile_id):
    """Add a shedding record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        shedding = Shedding(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            complete=request.form.get('complete', 'true').lower() == 'true',
            notes=request.form.get('notes')
        )
        
        db.session.add(shedding)
        db.session.commit()
        
        return jsonify({'success': True, 'shedding': shedding.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>/measurement', methods=['POST'])
def add_measurement(reptile_id):
    """Add a measurement record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        measurement = Measurement(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            length_cm=float(request.form.get('length_cm')) if request.form.get('length_cm') else None,
            weight_g=float(request.form.get('weight_g')) if request.form.get('weight_g') else None,
            notes=request.form.get('notes')
        )
        
        db.session.add(measurement)
        db.session.commit()
        
        return jsonify({'success': True, 'measurement': measurement.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>/defecation', methods=['POST'])
def add_defecation(reptile_id):
    """Add a defecation record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        defecation = Defecation(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            notes=request.form.get('notes')
        )
        
        db.session.add(defecation)
        db.session.commit()
        
        return jsonify({'success': True, 'defecation': defecation.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>/breeding', methods=['POST'])
def add_breeding(reptile_id):
    """Add a breeding record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        breeding = Breeding(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            notes=request.form.get('notes')
        )
        
        db.session.add(breeding)
        db.session.commit()
        
        return jsonify({'success': True, 'breeding': breeding.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/reptile/<int:reptile_id>/cleaning', methods=['POST'])
def add_cleaning(reptile_id):
    """Add a cleaning record."""
    try:
        reptile = Reptile.query.get_or_404(reptile_id)
        
        recorded_at = datetime.utcnow()
        if request.form.get('recorded_at'):
            recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        
        cleaning = Cleaning(
            reptile_id=reptile.id,
            recorded_at=recorded_at,
            cleaning_type=request.form.get('cleaning_type', 'spot'),
            notes=request.form.get('notes')
        )
        
        db.session.add(cleaning)
        db.session.commit()
        
        return jsonify({'success': True, 'cleaning': cleaning.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ API Routes - Update/Delete Records ============

@main.route('/api/feeding/<int:record_id>', methods=['PUT'])
def update_feeding(record_id):
    """Update a feeding record."""
    try:
        feeding = Feeding.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            feeding.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('food_type') is not None:
            feeding.food_type = request.form.get('food_type')
        if request.form.get('notes') is not None:
            feeding.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'feeding': feeding.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/feeding/<int:record_id>', methods=['DELETE'])
def delete_feeding(record_id):
    """Delete a feeding record."""
    try:
        feeding = Feeding.query.get_or_404(record_id)
        db.session.delete(feeding)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/shedding/<int:record_id>', methods=['PUT'])
def update_shedding(record_id):
    """Update a shedding record."""
    try:
        shedding = Shedding.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            shedding.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('complete') is not None:
            shedding.complete = request.form.get('complete', 'true').lower() == 'true'
        if request.form.get('notes') is not None:
            shedding.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'shedding': shedding.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/shedding/<int:record_id>', methods=['DELETE'])
def delete_shedding(record_id):
    """Delete a shedding record."""
    try:
        shedding = Shedding.query.get_or_404(record_id)
        db.session.delete(shedding)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/measurement/<int:record_id>', methods=['PUT'])
def update_measurement(record_id):
    """Update a measurement record."""
    try:
        measurement = Measurement.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            measurement.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('length_cm') is not None:
            measurement.length_cm = float(request.form.get('length_cm')) if request.form.get('length_cm') else None
        if request.form.get('weight_g') is not None:
            measurement.weight_g = float(request.form.get('weight_g')) if request.form.get('weight_g') else None
        if request.form.get('notes') is not None:
            measurement.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'measurement': measurement.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/measurement/<int:record_id>', methods=['DELETE'])
def delete_measurement(record_id):
    """Delete a measurement record."""
    try:
        measurement = Measurement.query.get_or_404(record_id)
        db.session.delete(measurement)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/defecation/<int:record_id>', methods=['PUT'])
def update_defecation(record_id):
    """Update a defecation record."""
    try:
        defecation = Defecation.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            defecation.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('notes') is not None:
            defecation.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'defecation': defecation.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/defecation/<int:record_id>', methods=['DELETE'])
def delete_defecation(record_id):
    """Delete a defecation record."""
    try:
        defecation = Defecation.query.get_or_404(record_id)
        db.session.delete(defecation)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/breeding/<int:record_id>', methods=['PUT'])
def update_breeding(record_id):
    """Update a breeding record."""
    try:
        breeding = Breeding.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            breeding.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('notes') is not None:
            breeding.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'breeding': breeding.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/breeding/<int:record_id>', methods=['DELETE'])
def delete_breeding(record_id):
    """Delete a breeding record."""
    try:
        breeding = Breeding.query.get_or_404(record_id)
        db.session.delete(breeding)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/cleaning/<int:record_id>', methods=['PUT'])
def update_cleaning(record_id):
    """Update a cleaning record."""
    try:
        cleaning = Cleaning.query.get_or_404(record_id)
        
        if request.form.get('recorded_at'):
            cleaning.recorded_at = datetime.strptime(request.form.get('recorded_at'), '%Y-%m-%dT%H:%M')
        if request.form.get('cleaning_type'):
            cleaning.cleaning_type = request.form.get('cleaning_type')
        if request.form.get('notes') is not None:
            cleaning.notes = request.form.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'cleaning': cleaning.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/cleaning/<int:record_id>', methods=['DELETE'])
def delete_cleaning(record_id):
    """Delete a cleaning record."""
    try:
        cleaning = Cleaning.query.get_or_404(record_id)
        db.session.delete(cleaning)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ API Routes - Get Records ============

@main.route('/api/reptile/<int:reptile_id>/records')
def get_records(reptile_id):
    """Get all records for a reptile."""
    reptile = Reptile.query.get_or_404(reptile_id)
    
    return jsonify({
        'feedings': [f.to_dict() for f in reptile.feedings.limit(50).all()],
        'sheddings': [s.to_dict() for s in reptile.sheddings.limit(50).all()],
        'measurements': [m.to_dict() for m in reptile.measurements.limit(50).all()],
        'defecations': [d.to_dict() for d in reptile.defecations.limit(50).all()],
        'breedings': [b.to_dict() for b in reptile.breedings.limit(50).all()],
        'cleanings': [c.to_dict() for c in reptile.cleanings.limit(50).all()]
    })
