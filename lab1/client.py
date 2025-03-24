from utils import client


def main():
    while True:
        try:
            filename = input("输入传输文件路径：")
            client(filename, host="23.95.227.104")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
