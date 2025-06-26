from datetime import datetime
from sqlalchemy import func
from flask import Blueprint, jsonify, request
from app.models import CardTable, Item, WIPQuotation, Customer, MarginTable, ItemPricing
from app import db

wip_quotation_bp = Blueprint('wip_quotation', __name__)

from datetime import datetime

def generate_quotation_id():
    today_date = datetime.today().strftime('%Y%m%d')
    latest_quotation = db.session.query(WIPQuotation).filter(WIPQuotation.quotation_id.like(f'WIP_{today_date}_%')).order_by(WIPQuotation.quotation_id.desc()).first()
    
    if latest_quotation:
        latest_serial = int(latest_quotation.quotation_id.split('_')[-2])  # Extract serial number
        serial_number = latest_serial + 1
    else:
        serial_number = 1
    
    serial_number_str = f"{serial_number:03d}"
    timestamp = datetime.now().strftime('%H%M%S')  # Get current time in HHMMSS format

    return f"WIP_{today_date}_{serial_number_str}_{timestamp}"

@wip_quotation_bp.route('/create_quotation', methods=['POST','GET'])
def create_quotation():
    try:
         
        quotation_id = generate_quotation_id()
        new_quotation = WIPQuotation(
            quotation_id=quotation_id,
            customer_id=None,
            card_ids=[],
            margin_ids=[],
            date_created=datetime.now(),
            date_modified=datetime.now()
        )
        db.session.add(new_quotation)
        db.session.commit()

        return jsonify({"message": "Quotation created", "quotation_id": quotation_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@wip_quotation_bp.route('/add_card_to_quotation', methods=['POST'])
def add_card_to_quotation():
    try:
        data = request.get_json()
        quotation_id = data.get('quotation_id')
        print(quotation_id)
        card_id = data.get('card_id')
        print(card_id)
        

        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        if not quotation:
            return jsonify({"error": "Quotation not found"}), 404
        print(f"Existing card_ids: {quotation.card_ids}") 

        if card_id not in quotation.card_ids:
            quotation.card_ids.append(card_id)
            print(f"Updated card_ids: {quotation.card_ids}")
            quotation.date_modified = datetime.now()
            db.session.flush()
            print(quotation)
            db.session.commit()
            
        
        print("Changes committed.")

        return jsonify({"message": "Card added to quotation", "quotation_id": quotation_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@wip_quotation_bp.route('/add_margin_to_quotation', methods=['POST'])
def add_margin_to_quotation():
    try:
        data = request.get_json()
        quotation_id = data.get('quotation_id')
        margin_id = data.get('margin_id')

        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        print(quotation)
        if not quotation:
            return jsonify({"error": "Quotation not found"}), 404

        if margin_id not in quotation.margin_ids:
            quotation.margin_ids.append(margin_id)
            print(f"Updated margin_ids: {quotation.margin_ids}")
            quotation.date_modified = datetime.now()
            db.session.flush()
            
            db.session.commit()
        print(quotation)
        return jsonify({"message": "Margin added to quotation", "quotation_id": quotation_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@wip_quotation_bp.route('/add_customer_to_quotation', methods=['POST'])
def add_customer_to_quotation():
    try:
        data = request.get_json()
        print(data)
        quotation_id = data.get('quotation_id')
        customer_id = data.get('customer_id') or None
        print(customer_id)

        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        print(quotation)
        if not quotation:
            return jsonify({"error": "Quotation not found"}), 404
        
        quotation.customer_id = customer_id
        print(quotation)

        # Commit the change to the database
        
        db.session.commit()

        # Return a success response
        return jsonify({"message": "Customer added to quotation", "quotation_id": quotation_id, "customer_id": customer_id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@wip_quotation_bp.route('/preview_quotation/<string:quotation_id>', methods=['GET'])
def preview_quotation(quotation_id):
    try:
        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        if not quotation:
            return jsonify({"error": "Quotation not found"}), 404

        # Fetch related data
        cards = CardTable.query.filter(CardTable.card_id.in_(quotation.card_ids)).all()
        margins = MarginTable.query.filter(MarginTable.margin_id.in_(quotation.margin_ids)).all()
        customer = Customer.query.filter_by(customer_id=quotation.customer_id).first()

        card_data = []  # Store cards with item names
        margin_data = []  # Store margin details

        for margin in margins:
            margin_dict = {
                "margin_id": margin.margin_id,
                'mc_name': margin.mc_name,
                "margin": float(margin.margin) if margin.margin else 0.0  # Convert margin to float
            }
            margin_data.append(margin_dict)

      
        for card in cards:
            card_dict = card.to_dict()  
            card_items = []

            for item in card.items: 
                item_id = item.get('item_id') if isinstance(item, dict) else item 
                quantity = item.get('quantity')

                if item_id:
                    item_record = Item.query.filter_by(item_id=item_id).first()
                    if item_record:
                        item_dict = {
                            "item_id": item_id,
                            "image_url": item_record.image_url,  # Add image_url from Item table
                            "article": item_record.article,
                            "cat1": item_record.cat1,
                            "cat2": item_record.cat2,
                            "cat3": item_record.cat3,
                            "quantity": quantity,
                            "gst" : item_record.gst,
                            "make" : item_record.make,
                            'mc_name': item_record.mc_name,
                        }

                        item_pricing_record = ItemPricing.query.filter_by(discountcategory=item_record.discount_category).first()

                        if item_pricing_record:
                            mrp = float(item_record.mrp)
                            discount = float(item_pricing_record.discount) if item_pricing_record.discount else 0.0
                            netrate = float(item_pricing_record.netrate) if item_pricing_record.netrate else 0.0
                            margin_percentage = margin_data[0]["margin"] if margin_data else 0.0

                            if discount > 0:
                                price = mrp - (mrp * (discount / 100))
                                final_price = price + (price * (margin_percentage / 100))
                            elif netrate > 0:
                                final_price = netrate + (netrate * (margin_percentage / 100))
                            else:
                                final_price = mrp  # Default to MRP if no discount/netrate

                            total_price = final_price * quantity

                            # Store pricing details
                            item_dict["final_price"] = str(final_price)
                            item_dict["total_price"] = str(total_price)

                        card_items.append(item_dict)

            card_dict["items"] = card_items  # Add items to card
            card_data.append(card_dict)

        return jsonify({
            "quotation_id": quotation.quotation_id,
            "cards": card_data,
            "margins": margin_data,
            "customer": {
                "customer_id": customer.customer_id if customer else None,
                'title': customer.title if customer else None,
                "name": customer.name if customer else "Unknown",
                "project_name": customer.project_name if customer else "Unknown",
                "billing_address": customer.billing_address if customer else "Unknown",
                'shipping_address': customer.shipping_address if customer else 'Unknown',
                'phone_number': customer.phone_number if customer else None,
                'whatsapp_number': customer.whatsapp_number if customer else None,
            },
            "date_created": quotation.date_created,
            "date_modified": quotation.date_modified
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@wip_quotation_bp.route('/get_all_quotations', methods=['GET'])
def get_all_quotations():
    try:
        quotations = db.session.query(WIPQuotation.quotation_id, Customer.name).join(Customer, WIPQuotation.customer_id == Customer.customer_id).all()

        if not quotations:
            return jsonify({"error": "No quotations found"}), 404

        all_quotations_data = [{"quotation_id": q.quotation_id, "name": q.name} for q in quotations]

        return jsonify({"quotations": all_quotations_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@wip_quotation_bp.route('/delete_quotation/<string:quotation_id>', methods=['DELETE'])
def delete_quotation(quotation_id):
    try:
        quotation = WIPQuotation.query.filter_by(quotation_id=quotation_id).first()
        db.session.delete(quotation)
        db.session.commit()
        return jsonify({"message": "Quotation deleted from wip table", "quotation_id": quotation_id}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
     

@wip_quotation_bp.route('/wip_quotation/', methods=['POST'])
def create_wip_quotation():
    try:
        data = request.get_json()
        quotation_id = generate_quotation_id()

        # Extracting other fields from request body
        customer_id = data.get("customer_id")
        card_ids = data.get("card_ids", [])  # Default to empty list if not provided
        margin_ids = data.get("margin_ids", [])

        # Creating a new quotation instance with provided quotation_id
        quotation = WIPQuotation(
            quotation_id=quotation_id,  # Taken from URL
            customer_id=customer_id,
            card_ids=card_ids,
            margin_ids=margin_ids,
            date_created=datetime.now(),
            date_modified=datetime.now()
        )

        db.session.add(quotation)
        db.session.commit()

        return jsonify({"message": "Quotation created", "quotation_id": quotation.quotation_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
