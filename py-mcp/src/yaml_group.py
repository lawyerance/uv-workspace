import yaml

if __name__ == "__main__":
    with open("config/group.yaml", "r") as f:
        group = yaml.load_all(f, Loader=yaml.FullLoader)
        for group in group:
            print(group)
