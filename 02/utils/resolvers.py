from pathlib import Path

import polars as pl


def _read_and_process_csv(filename: Path,
                          as_list: bool = True) -> pl.DataFrame:
    """
    Reads a CSV file and processes its content into a Polars DataFrame.

    Args:
        filename (Path): The path to the CSV file to be read.
        as_list (bool): Whether to return the column as a list or not.

    Returns:
        pl.DataFrame: A Polars DataFrame with processed data.
    """
    df = (
        pl
        .read_csv(
            filename,
            has_header=False
        )
    )

    return (
        df
        .with_columns(
            pl
            .col("column_1")
            .str.split(" ")
            .cast(pl.List(pl.Int64))
        ) if as_list else df
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
            pl.col("column_1")
            .list.diff()
            .list.eval(
                pl.element().is_between(1, 3)
            )
            .list.all()
            .alias("is_safe_ascending"),
            pl.col("column_1")
            .list.diff()
            .list.eval(
                pl.element().is_between(-3, -1)
            )
            .list.all()
            .alias("is_safe_descending")
        )
        .max_horizontal()
        .sum()
    )


def second_exercise(filename: Path) -> pl.DataFrame:
    df_processed = _read_and_process_csv(filename, as_list=False)

    return (
        df_processed
        .with_row_index()
        .with_columns(
            pl.col("column_1")
            .repeat_by(
                pl.col("column_1")
                .str.split(" ")
                .list.len() + 1  # All combinations plus the original
            )
        )
        .explode("column_1")
        .with_columns(
            pl.int_range(pl.len(), dtype=pl.UInt32).over(
                "index"
            ).alias("index_to_drop"),
            pl.col("column_1").str.split(" ").cast(pl.List(pl.Int64))
        )
        .with_columns(
            pl.col("index_to_drop").cast(int) - pl.lit(1)
        )
        .select(
            pl.col("index"),
            pl.when(pl.col("index_to_drop") == pl.lit(-1))
            .then(pl.col("column_1"))
            .otherwise(
                pl.col("column_1")
                .list.slice(0, pl.col("index_to_drop"))
                .list.concat(
                    pl.col("column_1")
                    .list.slice(
                        pl.col("index_to_drop") + 1,
                        pl.col("column_1").list.len()
                    )
                )
            )
            .alias("column_1")
        )
        .with_columns(
            pl.col("column_1")
            .list.diff()
            .list.eval(
                pl.element().is_between(1, 3)
            )
            .list.all()
            .alias("is_safe_ascending"),
            pl.col("column_1")
            .list.diff()
            .list.eval(
                pl.element().is_between(-3, -1)
            )
            .list.all()
            .alias("is_safe_descending")
        )
        .group_by("index")
        .agg(
            pl.col("is_safe_ascending").max(),
            pl.col("is_safe_descending").max()
        )
        .drop("index")
        .max_horizontal()
        .sum()
    )
