from configs import deep_merge


def test_deep_merge1():
    # --- 使用示例 ---
    dict_a = {
        "app": {"name": "MyApp", "port": 8080},
        "db": {"host": "localhost", "port": 5432}
    }

    dict_b = {
        "app": {"port": 9000, "debug": True},  # 更新 port，增加 debug
        "cache": {"redis": True}  # 增加全新的 key
    }

    merged = deep_merge(dict_a, dict_b)
    print(merged)

def test_deep_merge2():
    # --- 使用示例 ---
    dict_a = {
        "app": {"name": "MyApp", "port": 8080},
        "db": {"host": "localhost", "port": 5432}
    }

    dict_b = {
        "app": {"id": 100, "debug": True},  # 更新 port，增加 debug
        "cache": {"redis": True}  # 增加全新的 key
    }

    merged = deep_merge(dict_a, dict_b)
    print(merged)
