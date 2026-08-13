from dataclasses import dataclass


@dataclass
class Leader:

    leader_id: str

    leader_name: str

    party: str

    state: str

    district: str

    constituency: str

    facebook_url: str