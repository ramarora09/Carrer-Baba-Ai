import pandas as pd
from utils.role_data import ROLE_DATA
def calculate_role_demand():
    roles=list(ROLE_DATA.keys())

    demand=[
        95,92,90,88,85,
        87,84,89,91,90,
        83,93,86,80,78,88
    ]

    return pd.DataFrame({
        "role":roles,
        "demand_score":demand
    })


def get_role_skills(role):
    return ROLE_DATA.get(role,{}).get("skills",[])



def get_role_companies(role):
    return ROLE_DATA.get(role,{}).get("companies",[])