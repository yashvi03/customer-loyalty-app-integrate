import logging
from flask import Blueprint, jsonify, request
from app.models import CardTable, Item
from app import db
import uuid

card_bp = Blueprint('cards', __name__)

@card_bp.route('/cards', methods=['POST'])
def add_card():
    try:
        data = request.json
        items_data = data.get('items')  # List of {'article': article_name, 'quantity': qty}

        if not items_data:
            return jsonify({"error": "Items are required"}), 400

        # Generate a new UUID for card_id
        card_id = str(uuid.uuid4())

        # Create a list for storing item data
        items = []

        for item_data in items_data:
            article = item_data.get('name')
            quantity = item_data.get('quantity')

            # Build the filters for querying the Item table
            filters = {
                'type': data.get('type'),
                'size': data.get('size'),
                'article': article,
                'cat1': data.get('cat1'),
                'cat2': data.get('cat2'),
                'cat3': data.get('cat3')
            }

            # Remove any filters where the value is None
            filters = {key: value for key, value in filters.items() if value is not None}

            # Query for the item using the constructed filters
            item = Item.query.filter_by(**filters).first()

            if not item:
                return jsonify({"error": f"Item with article '{article}' not found."}), 400

            # Append the item details to the items list
            items.append({'item_id': str(item.item_id), 'quantity': quantity})

        # Create a new card entry
        new_card = CardTable(
            card_id=card_id,  # Using the generated UUID
            type=data.get('type'),
            size=data.get('size'),
            items=items  # Store items as a JSON list
        )

        # Add the new card to the CardTable
        db.session.add(new_card)
        db.session.commit()

        # Return a response with the newly created card details
        return jsonify({
            "message": "Card added successfully",
            "card": {
                "card_id": card_id,
                "type": new_card.type,
                "size": new_card.size,
                "items": items  # Directly return the items list
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@card_bp.route('/update_card/<string:card_id>', methods=['PUT'])
def update_card(card_id):
    try:
        data = request.json
        items_data = data.get('items')  # List of {'article': article_name, 'quantity': qty}

        if not items_data:
            return jsonify({"error": "Items are required"}), 400
        card = CardTable.query.filter_by(card_id=card_id).first()
        if not card:
            return jsonify({"error": "Card not found"}), 404
        card.type = data.get('type', card.type)
        card.size = data.get('size', card.size)
            
        updated_items = []
        for item_data in items_data:
            article = item_data.get('name')
            quantity = item_data.get('quantity')

            filters = {
                'type': data.get('type', card.type),
                'size': data.get('size', card.size),
                'article': article,
            }
            filters = {key: value for key, value in filters.items() if value is not None}
            item = Item.query.filter_by(**filters).first()
            if not item:
                return jsonify({"error": f"Item with article '{article}' not found."}), 400
            updated_items.append({'item_id': str(item.item_id), 'quantity': quantity})

        card.items = updated_items  # Update the items list
        db.session.commit()
        return jsonify({"message": "Card updated successfully", "card_id": card.card_id}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


    
@card_bp.route('/cards', methods=['GET'])
def get_all_cards():
    try:
        cards = CardTable.query.all()
        card_list = []
        
        for card in cards:
            item_details = []
            items = card.items
            
            for item in items:  # Assuming card.items is a list of item IDs
                item_id = item.get('item_id')
                quantity = item.get('quantity')
                if item_id:
                    item_record = Item.query.filter_by(item_id = item_id).first()
                    if item_record:
                        item_details.append({'item_id': item_record.item_id, 'article': item_record.article, 'quantity': quantity,'cat1':item_record.cat1,'cat2':item_record.cat2,'cat3':item_record.cat3})
            
            card_data = {
                'card_id': str(card.card_id),
                'type': card.type,
                'size': card.size,
                'items': item_details  # Use item details instead of raw item IDs
            }
            card_list.append(card_data)
            print(card_data)
        
        return jsonify({'cards': card_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@card_bp.route('/get_card_by_id/<string:card_id>', methods=['GET'])
def get_card_by_id(card_id):
    try:
        card = CardTable.query.filter_by(card_id=card_id).first()
        print(card)
        
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        if card:
            item_details = []
            items = card.items
            
            for item in items:  # Assuming card.items is a list of item IDs
                item_id = item.get('item_id')
                quantity = item.get('quantity')
                if item_id:
                    item_record = Item.query.filter_by(item_id = item_id).first()
                    if item_record:
                        item_details.append({'item_id': item_record.item_id, 'article': item_record.article, 'quantity': quantity})
         

        card_data = {
            'card_id': str(card.card_id),
            'type': card.type,
            'size': card.size,
            'items': item_details
        }
        
        print(card_data)

        return jsonify({'card': card_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@card_bp.route('delete_card/<string:card_id>', methods=['DELETE'])
def delete_card(card_id):
    try:
        # Delete items associated with the form_id
        deleted_card = CardTable.query.filter_by(card_id=card_id).delete()

        # Commit changes
        db.session.commit()
        if deleted_card == 0:
            return jsonify({"error": "No card found to delete"}), 404

        logging.info(f"Form with form_id={card_id} deleted successfully")
        return jsonify({"message": "Form deleted successfully"}), 200

    except Exception as e:
        logging.error(f"Error while deleting form_id={card_id}: {e}")
        return jsonify({"error": str(e)}), 500