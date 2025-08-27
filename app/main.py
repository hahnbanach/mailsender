from mailsender.api.main import app


if __name__ == "__main__":
    import argparse
    import logging
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    log_level = "debug" if args.debug else "info"
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=log_level)
