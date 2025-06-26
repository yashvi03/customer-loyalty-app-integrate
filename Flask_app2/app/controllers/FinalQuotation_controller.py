from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import FinalQuotation, CardTable, MarginTable, Customer, Item, ItemPricing
from app import db

final_quotation_bp = Blueprint('final_quotation', __name__)

@final_quotation_bp.route('/final_quotation', methods=['POST'])
def create_quotation():
    try:
        data = request.get_json()

        # Extracting data safely
        quotation_id = data.get("quotation_id")
        customer_id = data.get("customer_id")
        card_ids = data.get("card_ids", [])
        margin_ids = data.get("margin_ids", [])

        if not quotation_id or not customer_id:
            return jsonify({"error": "quotation_id and customer_id are required"}), 400

        # Remove "WIP_" prefix if present
        if quotation_id.startswith("WIP_"):
            quotation_id = quotation_id[4:]
            
        # First get all quotations for this customer
        customer_quotations = FinalQuotation.query.filter_by(customer_id=customer_id).all()
        
        # Debug print
        print(f"Found {len(customer_quotations)} quotations for customer {customer_id}")
        print(f"New quotation details - card_ids: {card_ids}, margin_ids: {margin_ids}")
        
        # Then manually check if any have the same content
        for existing in customer_quotations:
            # Debug prints
            print(f"Comparing existing quotation {existing.quotation_id}")
            print(f"Existing card_ids: {existing.card_ids}, Type: {type(existing.card_ids)}")
            print(f"New card_ids: {card_ids}, Type: {type(card_ids)}")
            
            # Convert to consistent format (strings) and sort
            try:
                existing_card_ids = [str(id) for id in existing.card_ids] if existing.card_ids else []
                new_card_ids = [str(id) for id in card_ids] if card_ids else []
                
                existing_margin_ids = [str(id) for id in existing.margin_ids] if existing.margin_ids else []
                new_margin_ids = [str(id) for id in margin_ids] if margin_ids else []
                
                # Sort for consistent comparison
                existing_card_ids.sort()
                new_card_ids.sort()
                existing_margin_ids.sort()
                new_margin_ids.sort()
                
                print(f"Formatted existing card_ids: {existing_card_ids}")
                print(f"Formatted new card_ids: {new_card_ids}")
                print(f"Formatted existing margin_ids: {existing_margin_ids}")
                print(f"Formatted new margin_ids: {new_margin_ids}")
                
                # Check if they match after normalization
                if existing_card_ids == new_card_ids and existing_margin_ids == new_margin_ids:
                    print("Match found!")
                    return jsonify({
                        "message": "A quotation with the exact same details already exists", 
                        "quotation_id": existing.quotation_id
                    }), 200
            except Exception as e:
                print(f"Error during comparison: {str(e)}")
                continue  # Move to next quotation if this one has errors

        # If we reach here, no duplicate was found, so create a new one
        print("No duplicate found, creating new quotation")
        quotation = FinalQuotation(
            quotation_id=quotation_id,
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
        print(f"Error creating quotation: {str(e)}")
        return jsonify({"error": str(e)}), 400


@final_quotation_bp.route('/preview_final_quotation/<string:quotation_id>', methods=['GET'])
def preview_quotation(quotation_id):
    try:
        quotation = FinalQuotation.query.filter_by(quotation_id=quotation_id).first()
        if not quotation:
            return jsonify({"error": "Quotation not found"}), 404

        # Fetch related data
        cards = CardTable.query.filter(CardTable.card_id.in_(quotation.card_ids)).all()
        margins = MarginTable.query.filter(MarginTable.margin_id.in_(quotation.margin_ids)).all()
        customer = Customer.query.filter_by(customer_id=quotation.customer_id).first()

        card_data = []  # Store cards with item names
        margin_data = []  # Store margin details

        # Add margin data (id + percentage)
        for margin in margins:
            margin_dict = {
                "margin_id": margin.margin_id,
                'mc_name': margin.mc_name,
                "margin": float(margin.margin) if margin.margin else 0.0  # Convert margin to float
            }
            margin_data.append(margin_dict)

        # Process cards and items
        for card in cards:
            card_dict = card.to_dict()  # Convert card data to a dictionary
            card_items = []

            # Fetching item names for each item in card
            for item in card.items:  # Assuming card.items is a list of dictionaries or IDs
                item_id = item.get('item_id') if isinstance(item, dict) else item  # Adjust based on structure
                quantity = item.get('quantity')

                if item_id:
                    item_record = Item.query.filter_by(item_id=item_id).first()
                    if item_record:
                        item_dict = {
                            "item_id": item_id,
                            "image_url": item_record.image_url,
                            "article": item_record.article,
                            "quantity": quantity,
                            "gst" : item_record.gst,
                            "make" : item_record.make,
                            'mc_name':item_record.mc_name,
                            'cat1':item_record.cat1,
                            'cat2':item_record.cat2,
                            'cat3':item_record.cat3,
                        }

                        # Fetch item pricing details
                        item_pricing_record = ItemPricing.query.filter_by(discountcategory=item_record.discount_category).first()

                        if item_pricing_record:
                            # Convert Decimal values to float
                            mrp = float(item_record.mrp)
                            discount = float(item_pricing_record.discount) if item_pricing_record.discount else 0.0
                            netrate = float(item_pricing_record.netrate) if item_pricing_record.netrate else 0.0
                            margin_percentage = margin_data[0]["margin"] if margin_data else 0.0

                            # Calculate final price
                            if discount > 0:
                                price = mrp - (mrp * (discount / 100))
                                final_price = price + (price * (margin_percentage / 100))
                            elif netrate > 0:
                                final_price = netrate + (netrate * (margin_percentage / 100))
                            else:
                                final_price = mrp
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
                'billing_address': customer.billing_address if customer else 'Unknown',
                'shipping_address': customer.shipping_address if customer else 'Unknown',
                'phone_number': customer.phone_number if customer else None,
                'whatsapp_number': customer.whatsapp_number if customer else None,
            },
            "date_created": quotation.date_created,
            "date_modified": quotation.date_modified
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    
@final_quotation_bp.route('/get_final_quotations', methods=['GET'])
def get_all_quotations():
    try:
        quotations = db.session.query(FinalQuotation.quotation_id, Customer.name).join(Customer, FinalQuotation.customer_id == Customer.customer_id).all()

        if not quotations:
            return jsonify({"error": "No quotations found"}), 404

        all_quotations_data = [{"quotation_id": q.quotation_id, "name": q.name} for q in quotations]

        return jsonify({"quotations": all_quotations_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500