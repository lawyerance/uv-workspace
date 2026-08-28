from examples.db import convert_postgres_jdbc_to_sa


def test_convert_postgres_jdbc_to_sa():
    # --- 使用示例 ---
    jdbc_url = "jdbc:postgresql://localhost:5432/mydb?ssl=true&connectTimeout=30000&currentSchema=public&ApplicationName=MyApp"

    pool = convert_postgres_jdbc_to_sa(
        jdbc_url,
        username="postgres",
        password="123456",
        pool_size=5,
        max_overflow=10
    )
