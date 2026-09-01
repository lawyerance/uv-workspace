import io


def test_mege():
    from omegaconf import OmegaConf

    yaml_conf = """
server:
  host: localhost
  port: 80

client:
  url: http://${server.host}:${server.port}/
  server_port: ${server.port}
  # relative interpolation
  description: Client of ${.url}
    """
    conf_io = io.StringIO(yaml_conf)
    conf = OmegaConf.load(conf_io)

    assert conf['client']['url'] == 'http://localhost:80/'
    assert conf['client']['description'] == 'Client of http://localhost:80/'
