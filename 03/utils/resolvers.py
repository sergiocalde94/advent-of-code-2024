from pathlib import Path

import polars as pl


def _read_and_process_csv(filename: Path) -> pl.DataFrame:
    """
    Reads a CSV file and processes its content into a Polars DataFrame.

    Args:
        filename (Path): The path to the CSV file to be read.

    Returns:
        pl.DataFrame: A Polars DataFrame with processed data.
    """
    return (
        pl
        .read_csv(
            filename,
            has_header=False,
            separator="\n"
        )
        .select(pl.all().str.concat(delimiter="|"))
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
            pl
            .col("column_1")
            .str.extract_all(r"(mul\(\d+,\d+\))")
        )
        .explode("column_1")
        .select(
            pl.col("column_1").str.extract_groups(r"(\d+),(\d+)")
        )
        .with_columns(
            pl.col("column_1").struct.field("1").alias("a"),
            pl.col("column_1").struct.field("2").alias("b")
        )
        .select(
            pl.col("a").cast(pl.Int64).mul(
                pl.col("b").cast(pl.Int64)
            )
        )
        .sum()
        .item()
    )


def second_exercise(filename: Path) -> pl.DataFrame:
    df_processed = _read_and_process_csv(filename)

    return (
        df_processed
        .select(
            pl
            .col("column_1")
            .str.replace("\\n", "")
            .str.extract_all(r"(mul\(\d+,\d+\))")
            .alias("all_multiplications"),
            pl
            .col("column_1")
            .str.replace("\n", "")
            .str.extract_all(r"don\'t\(\).*?(?:do\(\)|$)")
            .list.eval(
                pl.element().str.extract_all(r"(mul\(\d+,\d+\))")
            )
            .list.eval(
                pl.element().flatten()
            )
            .alias("to_remove")
        )
        .explode("all_multiplications")
        .with_columns(
            pl.int_range(0, pl.len())
            .over("all_multiplications")
            .alias("index_by_row")
        )
        .with_row_index()
        .explode("to_remove")
        .with_columns(
            (
                pl.col("all_multiplications") == pl.col("to_remove")
            ).sum().over("index", "index_by_row").alias("n_to_remove")
        )
        .select(
            pl.col("index"),
            pl.col("index_by_row"),
            pl.col("all_multiplications"),
            pl.col("n_to_remove")
        )
        .unique()
        .filter(
            pl.col("index_by_row") >= pl.col("n_to_remove")
        )
        .select(
            pl.col("all_multiplications").str.extract_groups(r"(\d+),(\d+)")
        )
        .with_columns(
            pl.col("all_multiplications").struct.field("1").alias("a"),
            pl.col("all_multiplications").struct.field("2").alias("b")
        )
        .select(
            pl.col("a").cast(pl.Int64).mul(
                pl.col("b").cast(pl.Int64)
            )
        )
        .sum()
        .item()
    )
