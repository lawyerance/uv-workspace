import json
import os.path

if __name__ == '__main__':
    parent_path = os.path.dirname(os.path.dirname(__file__))
    sni = 'www.akamai.com'
    host = '104.160.45.10'
    port = 443
    pbk = 'jgroijcWYH3yIut7e0BGeoqMFRegZYKCQUh6gO4cWWA'
    with open(os.path.join(parent_path, 'xray.json'), mode='r', encoding='UTF-8') as f:
        json_data = json.load(f)
        first_inbound = json_data.get('inbounds')[0]

        settings = first_inbound.get('settings')
        # vless://2d3687c7-98e6-49f2-8ff8-53133ddf8d14@104.160.45.10:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.akamai.com&fp=chrome&pbk=2hylMKk-3VNmj6POqw9sfjfhmCXjv966XGowpAludCI&sid=e5139704&type=tcp
        id = settings.get('clients')[0].get('id')

        shorts = first_inbound.get('streamSettings').get('realitySettings').get('shortIds')

        for sid in shorts:
            print(
                f'vless://{id}@{host}:{port}?encryption=none&flow=xtls-rprx-vision&security=reality&sni={sni}&fp=chrome&pbk={pbk}&type=tcp')
