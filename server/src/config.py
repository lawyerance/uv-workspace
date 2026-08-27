from configs import LocalSettings
from examples.config import Setting

if __name__ == '__main__':
    settings = Setting()
    print(settings.model_dump())
