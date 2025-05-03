def alias_to_json(alias):
    """
    Convert an alias object to a JSON-serializable dictionary.
    
    Args:
        alias: Alias object from bunq API
    
    Returns:
        dict: JSON-serializable alias data
    """
    if not alias:
        return None
        
    return {
        'iban': getattr(alias, 'iban', None),
        'is_light': getattr(alias, 'is_light', False),
        'display_name': getattr(alias, 'display_name', None),
        'avatar': getattr(alias, 'avatar', None),
        'label_user': {
            'uuid': getattr(alias.label_user, 'uuid', None) if hasattr(alias, 'label_user') else None,
            'display_name': getattr(alias.label_user, 'display_name', None) if hasattr(alias, 'label_user') else None,
            'country': getattr(alias.label_user, 'country', None) if hasattr(alias, 'label_user') else None,
            'avatar': getattr(alias.label_user, 'avatar', None) if hasattr(alias, 'label_user') else None,
            'public_nick_name': getattr(alias.label_user, 'public_nick_name', None) if hasattr(alias, 'label_user') else None
        } if hasattr(alias, 'label_user') else None,
        'country': getattr(alias, 'country', None)
    }

def geolocation_to_json(geolocation):
    """
    Convert a geolocation object to a JSON-serializable dictionary.
    
    Args:
        geolocation: Geolocation object from bunq API
    
    Returns:
        dict: JSON-serializable geolocation data
    """
    if not geolocation:
        return None
        
    return {
        'latitude': getattr(geolocation, 'latitude', None),
        'longitude': getattr(geolocation, 'longitude', None),
        'altitude': getattr(geolocation, 'altitude', 0),
        'radius': getattr(geolocation, 'radius', None)
    }

def payment_to_json(payment):
    """
    Convert a payment object to a JSON-serializable dictionary.
    Matches the exact format from the bunq API response.
    
    Args:
        payment: PaymentApiObject instance
    
    Returns:
        dict: JSON-serializable payment data
    """
    return {
        'id': payment.id_,
        'created': payment.created,
        'updated': payment.updated,
        'monetary_account_id': payment.monetary_account_id,
        'amount': {
            'currency': payment.amount.currency,
            'value': payment.amount.value
        },
        'description': payment.description,
        'type': payment.type_,
        'merchant_reference': payment.merchant_reference,
        'maturity_date': getattr(payment, 'maturity_date', None),
        'alias': alias_to_json(payment.alias),
        'counterparty_alias': alias_to_json(payment.counterparty_alias),
        'attachment': payment.attachment or [],
        'geolocation': geolocation_to_json(payment.geolocation),
        'batch_id': payment.batch_id,
        'conversation': getattr(payment, 'conversation', None),
        'allow_chat': getattr(payment, 'allow_chat', True),
        'scheduled_id': payment.scheduled_id,
        'address_billing': payment.address_billing,
        'address_shipping': payment.address_shipping
    } 