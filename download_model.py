import gdown

url = "https://drive.google.com/uc?id={}".format("1-3WMIEco9X8IQTPvUKjgkQY5ZAsytd28")

if __name__ == "__main__":
    gdown.download(
        url,
        output="./models/kremlin_gpt/pytorch_model.bin",
        quiet=True,
        use_cookies=False,
    )
    print("done")
