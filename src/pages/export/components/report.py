from __future__ import annotations
from datetime import datetime

import pandas as pd

from src.data.utils import make_json_safe
from src.data.profile import profile_dataframe
from src.data.store import get_store




def build_report(df: pd.DataFrame) -> dict[str, Any]:
    """Assemble the base export report shared by the export page downloads."""
    store= get_store()
    profile = profile_dataframe(df)
    return make_json_safe({
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_name": store['source_name'],
        "final_shape": list(store['current_df'].shape) if store is not None else None,
        "transformations": store["transform_log"],
        "final_profile":{
        "duplicates_count": profile["duplicates_count"],
        "missing_summary": profile["missing"].to_dict(orient="records"),
    }})
