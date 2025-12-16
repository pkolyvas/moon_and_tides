import threading
import logging
import apploader
import tides
import moon


def main():
    logging.basicConfig(
        filename=apploader.config['logging']['location'],
        encoding=apploader.config['logging']['encoding'],
        level=apploader.config['logging']['level']
    )
    logging.info('Moon and tides app started.')

    tide_thread = threading.Thread(target=tides.tide_worker)
    moon_thread = threading.Thread(target=moon.moon_worker)
    moon_thread.start()
    tide_thread.start()

    # TODO: Deinit lights function on exit
    # TODO: Clean exit


if __name__ == "__main__":
    main()
