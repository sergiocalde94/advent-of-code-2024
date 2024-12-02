from pathlib import Path

import polars as pl


def _read_and_process_csv(filename: Path) -> pl.DataFrame:
    """
    Reads a CSV file and processes its content into a Polars DataFrame.

    Args:
        filename (Path): The path to the CSV file to be read.

    Returns:
        pl.DataFrame: A Polars DataFrame with processed data. The DataFrame
        contains two columns, 'field_0' and 'field_1', both cast to Int64 type.
    """
    df = pl.read_csv(filename, has_header=False)

    return (
        df.with_columns(pl.col("column_1").str.split_exact("   ", n=1))
        .unnest("column_1")
        .select(
            pl.col("field_0").cast(pl.Int64),
            pl.col("field_1").cast(pl.Int64)
        )
    )

def first_exercise(filename: Path) -> pl.DataFrame:
        """
        Processes a CSV file and computes the absolute difference
        sum of two columns.

        Args:
            filename (Path): The path to the CSV file to be processed.

        Returns:
            pl.DataFrame: A DataFrame containing the result of the absolute
                difference sum of the two specified columns.
        """
        df_processed = _read_and_process_csv(filename)

        return (
            df_processed
            .select(
                (pl.col("field_0").sort()
                - pl.col("field_1").sort())
                .abs()
                .sum()
                .alias("result")
            )
            ["result"]
            [0]
        )

def second_exercise(filename: Path) -> pl.DataFrame:
        df_processed = _read_and_process_csv(filename)

        return (
            df_processed
            .join(
                df_processed["field_1"].value_counts(),
                left_on="field_0",
                right_on="field_1",
                how="inner"
            )
            .select(
                pl.col("field_0")
                .mul(pl.col("count"))
                .sum()
                .alias("result")
            )
            ["result"]
            [0]
        )
