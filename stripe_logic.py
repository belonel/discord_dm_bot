import stripe
import config
stripe.api_key = config.STRIPE_KEY

def update_customer_metadata(cus_id, metadata_dict = {}):
    stripe.Customer.modify(
        str(cus_id),
        metadata = metadata_dict
    )

def update_customer_description(cus_id, new_description):
    stripe.Customer.modify(
        str(cus_id),
        description=new_description
    )
