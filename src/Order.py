from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    order_id: str
    customer_id: str
    customer_name: str
    order_date: datetime
    order_status: str
    campaign_id: str
    items: list

    