from sqlalchemy import create_pool_from_url, make_url


def convert_postgres_jdbc_to_sa(jdbc_url: str, username: str = None, password: str = None,
                                **pool_kwargs):
    """将PostgreSQL JDBC URL转换为SQLAlchemy连接池"""

    if jdbc_url.startswith("jdbc:"):
        sa_url_str = jdbc_url[5:]

    # 解析URL
    url = make_url(sa_url_str)
    jdbc_params = url.query  # 原始JDBC参数

    # PostgreSQL参数映射表
    pg_mapping = {
        # SSL相关
        'ssl': ('sslmode', lambda v: 'require' if v.lower() == 'true' else 'disable'),
        'sslmode': ('sslmode', None),
        'sslrootcert': ('sslrootcert', None),
        'sslfactory': ('sslcrl', None),  # 不完全对应，需注意

        # 超时相关（毫秒→秒）
        'loginTimeout': ('connect_timeout', None),  # JDBC和Python都是秒
        'connectTimeout': ('connect_timeout', lambda v: str(int(v) // 1000)),
        'socketTimeout': ('read_timeout', lambda v: str(int(v) // 1000)),

        # 性能优化
        'prepareThreshold': ('prepared_statement_cache_size', None),
        'reWriteBatchedInserts': ('batch_inserts', lambda v: '1' if v.lower() == 'true' else '0'),
        'binaryTransfer': ('use_binary', lambda v: v.lower() == 'true'),

        # 会话配置
        'currentSchema': ('options', lambda v: f"-c search_path={v}"),
        'ApplicationName': ('application_name', None),

        # TCP保活
        'tcpKeepAlive': ('keepalives', lambda v: '1' if v.lower() == 'true' else '0'),

        # 高可用
        'targetServerType': ('target_session_attrs',
                             lambda v: 'primary' if v == 'master' else 'any'),
        'loadBalanceHosts': ('load_balance', lambda v: v.lower() == 'true'),
        'hostRecheckSeconds': ('host_recheck_seconds', None),
    }

    # 执行转换
    sa_params = {}
    for jdbc_key, (sa_key, converter) in pg_mapping.items():
        if jdbc_key in jdbc_params:
            value = jdbc_params[jdbc_key]
            if converter:
                try:
                    value = converter(value)
                except Exception as e:
                    print(f"warning：transform url param {jdbc_key}={value} fail: {e}")
            if sa_key:
                sa_params[sa_key] = value

    # 注入账号密码（如果提供）
    if username:
        url = url.set(username=username)
    if password:
        url = url.set(password=password)

    # 替换查询参数
    url = url.set(query=sa_params)

    # 创建连接池
    pool = create_pool_from_url(url, **pool_kwargs)

    # 打印转换结果供调试
    print(f"转换后URL: {url}")
    print(f"转换后参数: {sa_params}")

    return pool
