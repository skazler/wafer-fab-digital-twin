import polars as pl

class SPCService:
    @staticmethod
    def calculate_spc_metrics(telemetry_data: list):
        """
        Takes a list of dicts from SQLAlchemy and returns 
        enriched data with Control Limits.
        """
        if not telemetry_data:
            return []

        # convert to Polars DataFrame for high-performance processing
        df = pl.DataFrame(telemetry_data)
        
        # assume telemetry has a 'value' column (e.g. temperature)
        val_col = "value" 
        
        mean_val = df[val_col].mean()
        std_dev = df[val_col].std()
        
        # standard 3-sigma limits used in semiconductor fabs
        ucl = mean_val + (3 * std_dev)
        lcl = mean_val - (3 * std_dev)
        
        # add columns for the chart and flag violations
        enriched_df = df.with_columns([
            pl.lit(ucl).alias("ucl"),
            pl.lit(lcl).alias("lcl"),
            pl.lit(mean_val).alias("process_mean"),
            # rule 1: point outside 3-Sigma
            pl.when((pl.col(val_col) > ucl) | (pl.col(val_col) < lcl))
              .then(pl.lit(True))
              .otherwise(pl.lit(False))
              .alias("is_violation")
        ])
        
        return enriched_df.to_dicts()
