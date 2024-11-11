from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict

@dataclass
class Order:
    order_id: str
    customer_id: str
    customer_name: str
    order_date: datetime
    order_status: str
    campaign_id: str
    items: list

    def to_dict(self):
        data = asdict(self)
        data['order_date'] = self.order_date.isoformat()
        return data
    