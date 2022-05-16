from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Reference: https://argyle.com/docs/developer-tools/api-reference#employment-data-profiles


class Address(BaseModel):
    line1: Optional[str]  # street
    line2: Optional[str]  # additionalInfo
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]  # zip
    country: Optional[str]


class Profile(BaseModel):
    id: Optional[str]
    account: Optional[str]
    employer: Optional[str]
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = None
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    birth_date: Optional[str]
    picture_url: Optional[str]
    address: Optional[Address]
    ssn: Optional[str]
    marital_status: Optional[str]
    gender: Optional[str]
    metadata: Optional[str]
