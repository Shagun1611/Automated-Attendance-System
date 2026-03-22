from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app import app
from app.services.powerbi_service import PowerBIService
from datetime import datetime
import logging

# Initialize Power BI service
powerbi_service = PowerBIService()

@app.route('/api/powerbi/sync', methods=['POST'])
@jwt_required()
def sync_to_powerbi():
    """Sync attendance data to Power BI"""
    try:
        success, message = powerbi_service.sync_all_data()
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
    
    except Exception as e:
        logging.error(f"Power BI sync error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/powerbi/dashboard-url', methods=['GET'])
@jwt_required()
def get_powerbi_dashboard_url():
    """Get Power BI dashboard URL"""
    try:
        success, url = powerbi_service.get_dashboard_url()
        
        if success:
            return jsonify({'dashboard_url': url}), 200
        else:
            return jsonify({'error': url}), 400
    
    except Exception as e:
        logging.error(f"Get dashboard URL error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reports/attendance', methods=['GET'])
@jwt_required()
def export_attendance_report():
    """Export attendance report in various formats"""
    try:
        format_type = request.args.get('format', 'excel')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        class_name = request.args.get('class')
        section = request.args.get('section')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Export data
        success, data = powerbi_service.export_attendance_data(start_date, end_date)
        
        if not success:
            return jsonify({'error': data}), 400
        
        # Filter by class and section if provided
        if class_name or section:
            filtered_data = []
            for record in data:
                if class_name and record.get('class') != class_name:
                    continue
                if section and record.get('section') != section:
                    continue
                filtered_data.append(record)
            data = filtered_data
        
        # Export based on format
        if format_type.lower() == 'excel':
            success, filepath = powerbi_service.export_to_excel(data)
        elif format_type.lower() == 'csv':
            success, filepath = powerbi_service.export_to_csv(data)
        else:
            return jsonify({'error': 'Unsupported format. Use excel or csv'}), 400
        
        if success:
            return jsonify({
                'message': 'Report exported successfully',
                'filepath': filepath,
                'records_count': len(data)
            }), 200
        else:
            return jsonify({'error': filepath}), 400
    
    except Exception as e:
        logging.error(f"Export report error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reports/summary', methods=['GET'])
@jwt_required()
def get_attendance_summary():
    """Get attendance summary for reporting"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        success, summary_data = powerbi_service.generate_attendance_summary(start_date, end_date)
        
        if success:
            return jsonify({'summary': summary_data}), 200
        else:
            return jsonify({'error': summary_data}), 400
    
    except Exception as e:
        logging.error(f"Get summary error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500