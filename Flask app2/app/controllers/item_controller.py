from flask import Blueprint, jsonify, request
from app.models import Item
from app import db
import logging

logging.basicConfig(level=logging.DEBUG)

item_bp = Blueprint('items', __name__)

@item_bp.route('/filter', methods=['GET'])
def filter_items():
    filters = request.args.to_dict()

    # Convert 'null' values to None and retain keys
    filters = {key: (value if value and value.lower() != 'null' else None) for key, value in filters.items()}
    logging.debug(f"Received filters: {filters}")

    next_step = determine_next_step(filters)
    logging.debug(f"Determined next step: {next_step}")

    try:
        if next_step == 'final_article':
            options = get_distinct_values('article', filters)
            logging.debug(f"Re-fetching final articles: {options}")

            for option in options:
                option['final_article'] = option.pop('value')  # Rename 'article' to 'final_article'
        
        else:
            options = get_distinct_values(next_step, filters)
            logging.debug(f"Options for {next_step}: {options}")

        if next_step == 'quantity':  # Final step
            item = get_item_details(filters)
            if item:
                return jsonify({'next_step': next_step, 'item': item})
            else:
                return jsonify({'next_step': next_step, 'message': 'Item not found'})

        return jsonify({'next_step': next_step, 'options': options})

    except Exception as e:
        logging.error(f"Error in filter_items: {str(e)}")
        return jsonify({'error': str(e)})

def get_distinct_values(column, filters):
    logging.debug(f"Fetching distinct values for {column} with filters: {filters}")

    conditions = []
    if 'type' in filters and filters['type']:
        conditions.append(Item.type == filters['type'])
    if 'size' in filters and filters['size']:
        conditions.append(Item.size == filters['size'])
    if 'article' in filters and filters['article']:
        articles = filters['article'].split(',')
        conditions.append(Item.article.in_(articles))
    if 'cat1' in filters and filters['cat1']:
        conditions.append(Item.cat1 == filters['cat1'])
    if 'cat2' in filters and filters['cat2']:
        if filters['cat2'] == "None":
            conditions.append(Item.cat2.is_(None))
        else:
            conditions.append(Item.cat2 == filters['cat2'])
    if 'cat3' in filters and filters['cat3']:
        if filters['cat3'] == "None":
            conditions.append(Item.cat3.is_(None))
        else:
            conditions.append(Item.cat3 == filters['cat3'])

    # Use type_image_url for type, otherwise image_url
    image_column = Item.type_image_url if column == 'type' else Item.image_url

    subquery = (
        db.session.query(
            getattr(Item, column).label('value'),
            db.func.min(image_column).label('image_url')  # Select MIN image_url per group
        )
        .filter(*conditions)
        .group_by(getattr(Item, column))
        .distinct()
    )

    results = [{'value': row.value, 'image_url': row.image_url} for row in subquery.all()]
    
    logging.debug(f"Distinct {column} options: {results}")
    return results

def determine_next_step(filters):
    logging.debug(f"Determining next step with filters: {filters}")

    if not filters.get('type'):
        return 'type'
    if not filters.get('size'):
        return 'size'
    if not filters.get('article'):
        return 'article'
    if not filters.get('cat1'):
        return 'cat1'
    if not filters.get('cat2'):
        return 'cat2'
    
    # Skip cat3 if it's fully None and go directly to final article
    has_cat3 = db.session.query(Item).filter(Item.article.in_(filters['article'].split(',')), Item.cat3.isnot(None)).count() > 0
    if not has_cat3:
        return 'final_article'

    return 'cat3'

def get_item_details(filters):
    logging.debug(f"Fetching item details with filters: {filters}")

    item = db.session.query(Item).filter_by(**filters).first()
    if not item:
        return None

    return {
        'item_id': item.id,
        'type': item.type,
        'size': item.size,
        'article': item.article,
        'cat1': item.cat1,
        'cat2': item.cat2,
        'cat3': item.cat3,
        'mrp': item.mrp,
        'image_url': item.image_url
    }
