from sqlalchemy import text
from sqlalchemy.engine import Engine


INDEX_STATEMENTS = (
    """
    CREATE INDEX IF NOT EXISTS idx_prediction_logs_churn_probability
    ON prediction_logs (churn_probability)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_prediction_logs_customer_segment
    ON prediction_logs (customer_segment)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_prediction_logs_created_at
    ON prediction_logs (created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_prediction_logs_user_id
    ON prediction_logs (user_id)
    """,
)


def ensure_prediction_indexes(engine: Engine) -> None:
    with engine.begin() as connection:
        for statement in INDEX_STATEMENTS:
            connection.execute(text(statement))
