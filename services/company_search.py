"""
Smart stock search over the local Indian company mapping.
"""

import pandas as pd
from config.settings import COMPANY_MAPPING_PATH


class CompanySearch:
    def __init__(self, mapping_path: str = COMPANY_MAPPING_PATH):
        self.df = pd.read_csv(mapping_path)
        self._search_df = self.df.copy()
        for col in ["name", "group", "sector", "ticker"]:
            self._search_df[col + "_lower"] = self._search_df[col].str.lower()

    def search(self, query: str) -> pd.DataFrame:
        if not query or not query.strip():
            return self.df.iloc[0:0]

        q = query.strip().lower()

        exact_ticker = self._search_df[self._search_df["ticker_lower"] == q]
        if not exact_ticker.empty:
            return self._drop_helper_cols(exact_ticker)

        exact_ticker_no_suffix = self._search_df[
            self._search_df["ticker_lower"].str.replace(".ns", "", regex=False) == q
        ]
        if not exact_ticker_no_suffix.empty:
            return self._drop_helper_cols(exact_ticker_no_suffix)

        exact_name = self._search_df[self._search_df["name_lower"] == q]
        if not exact_name.empty:
            return self._drop_helper_cols(exact_name)

        group_match = self._search_df[self._search_df["group_lower"].str.contains(q, na=False)]
        name_match = self._search_df[self._search_df["name_lower"].str.contains(q, na=False)]
        sector_match = self._search_df[self._search_df["sector_lower"].str.contains(q, na=False)]

        combined = pd.concat([name_match, group_match, sector_match]).drop_duplicates(
            subset="ticker"
        )
        return self._drop_helper_cols(combined)

    @staticmethod
    def _drop_helper_cols(df: pd.DataFrame) -> pd.DataFrame:
        keep = ["ticker", "name", "group", "sector"]
        return df[keep].reset_index(drop=True)

    def list_groups(self):
        return sorted(self.df["group"].unique().tolist())

    def list_sectors(self):
        return sorted(self.df["sector"].unique().tolist())
