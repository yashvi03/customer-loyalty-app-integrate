from flask import Blueprint, jsonify, request
from app.models import CardTable, Item, WIPQuotation, MarginTable, FinalQuotation
from app import db
from sqlalchemy.exc import SQLAlchemyError
import uuid

pickMargin_bp = Blueprint('pickmargins', __name__)

@pickMargin_bp.route('/add_margin/<string:quotation_id>', methods=['POST'])
def add_or_update_margin(quotation_id):
    try:
        # Get the data from the request
        data = request.get_json()
        print("Received data:", data)  # Debugging log
        
        # Fetch the quotation based on the quotation_id
        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        
        if not quotation:
            return jsonify({'error': 'Quotation not found'}), 404
        
        added_margins = []
        
        # Loop through each item in the incoming data (since it's an array of objects)
        for item in data:
            mc_name = item.get("mc_name")
            margin_value = item.get("margin")
            
            # Try to find the margin by mc_name
            existing_margin = MarginTable.query.filter_by(mc_name=mc_name).first()
            
            # If the margin exists, update it
            if existing_margin:
                print(f"Updating existing margin for {mc_name}")
                existing_margin.margin = margin_value
                db.session.commit()
                added_margins.append({
                    "margin_id": existing_margin.margin_id,
                    "mc_name": existing_margin.mc_name,
                    "margin": existing_margin.margin
                })
            
            else:
                # If the margin does not exist, create a new one
                margin_id = str(uuid.uuid4())  # Generate a new margin_id
                
                # Create a new margin record
                new_margin = MarginTable(
                    margin_id=margin_id,
                    mc_name=mc_name,
                    margin=margin_value
                )
                
                print(f"Adding new margin: {new_margin}")
                
                # Add the new margin to the database
                db.session.add(new_margin)
                db.session.commit()
                
                added_margins.append({
                    "margin_id": new_margin.margin_id,
                    "mc_name": new_margin.mc_name,
                    "margin": new_margin.margin
                })

        return jsonify({
            'message': 'Margins added/updated successfully',
            'added_margins': added_margins  # Return the list of added or updated margins
        }), 200
    
    except Exception as e:
        # Log the error and return a response
        return jsonify({'error': str(e)}), 500
    except SQLAlchemyError as e:
        print("SQLAlchemyError:", str(e))  # Debugging log
        db.session.rollback()
        if 'duplicate key value' in str(e):
            return jsonify({"error": "Duplicate margin entry"}), 400
        return jsonify({"error": f"Database error: {str(e)}"}), 400
    
    # # Required fields for margin
    # required_fields = [ "mc_name", "margin"]
    # for field in required_fields:
    #     if field not in data:
    #         print(f"Missing field: {field}")  # Debugging log
    #         return jsonify({"error": f"Missing required field: {field}"}), 400

    # try:
    #     margin_value = float(data.get("margin"))
    #     print("Margin value:", margin_value)  # Debugging log
        
    #     # Check if there's already an existing margin for the quotation_id
    #     existing_margin = PickMargin.query.filter_by(
    #         quotation_id=data["quotation_id"]
    #     ).first()

    #     if existing_margin:
    #         # If margin exists, update the existing margin
    #         existing_margin.mc_name = data["mc_name"]
    #         existing_margin.margin = margin_value
    #         db.session.commit()
    #         return jsonify({
    #             "message": "Margin updated successfully",
    #             "id": existing_margin.id,
    #             "mc_name": existing_margin.mc_name,
    #             "margin": existing_margin.margin
    #         }), 200
    #     else:
    #         # Create new margin if no existing margin found
    #         new_margin = PickMargin(
    #             quotation_id=data["quotation_id"],  # Link to the quotation_id
    #             mc_name=data.get("mc_name"),
    #             margin=margin_value,
    #         )
            
    #         # Add the new margin and commit to the database
    #         db.session.add(new_margin)
    #         db.session.commit()

    #         return jsonify({
    #             "message": "Margin added successfully",
    #             "id": new_margin.id,  # This will be the auto-generated id
    #             "mc_name": new_margin.mc_name,
    #             "margin": new_margin.margin
    #         }), 201

    # except ValueError as ve:
    #     print("ValueError:", str(ve))  # Debugging log
    #     return jsonify({"error": "Margin must be a numerical value"}), 400

    # except SQLAlchemyError as e:
    #     print("SQLAlchemyError:", str(e))  # Debugging log
    #     db.session.rollback()
    #     if 'duplicate key value' in str(e):
    #         return jsonify({"error": "Duplicate margin entry"}), 400
    #     return jsonify({"error": f"Database error: {str(e)}"}), 400

    # finally:
    #     db.session.remove()  # Ensures the session is cleaned up after each request


@pickMargin_bp.route('/get_mc_name/<string:quotation_id>', methods=['GET'])
def get_margin(quotation_id):
    try:
        mc_names = []  # Define this outside the loop to accumulate unique mc_names across all cards
        unique_mc_names = set()  # Use a set to track unique mc_names
        
        # Fetch the specific quotation using the quotation_id
        if quotation_id and 'WIP' in quotation_id:
            quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        else:
            quotation = FinalQuotation.query.filter_by(quotation_id=quotation_id).first()

            
        if not quotation:
            return jsonify({'error': 'Quotation not found'}), 404
        
        # Get cards associated with the specific quotation
        cards = CardTable.query.filter(CardTable.card_id.in_(quotation.card_ids)).all()  # Get cards linked to the quotation
        
        for card in cards:
            items = card.items or []  # Ensure items is iterable, in case it's None or invalid
            
            for item in items:  # Assuming card.items is a list of item IDs
                item_id = item.get('item_id')
                if item_id:
                    item_record = Item.query.filter_by(item_id=item_id).first()
                    if item_record and item_record.mc_name not in unique_mc_names:
                        unique_mc_names.add(item_record.mc_name)  # Add to set for uniqueness
                        mc_names.append({'mc_name': item_record.mc_name})  # Append unique names only
                        
        return jsonify({'mc_names': mc_names})  # Return unique mc_names from all cards for this quotation
    except Exception as e:
        return jsonify({'error': str(e)}), 400


    #         # Use mc_names as needed
    # except SQLAlchemyError as e:
    #     print("SQLAlchemyError:", str(e))  # Debugging log
    #     return jsonify({"error": f"Database error: {str(e)}"}), 500
                    
                            
                            
    #     page = request.args.get('page', 1, type=int)
    #     per_page = request.args.get('per_page', 10, type=int)
    #     pickmargin = PickMargin.query.paginate(page=page, per_page=per_page, error_out=False)

    #     result = [
    #         {
    #             "id": m,
    #             "quotation_id": margin.quotation_id,  # Return quotation_id along with margin data
    #             "mc_name": margin.mc_name,
    #         }
    #         for margin in pickmargin.items
    #     ]
    #     return jsonify({"margins": result, "total": pickmargin.total}), 200

    # except SQLAlchemyError as e:
    #     print("SQLAlchemyError:", str(e))  # Debugging log
    #     return jsonify({"error": f"Database error: {str(e)}"}), 500

    # finally:
    #     db.session.remove()  # Ensures the session is cleaned up after each request
