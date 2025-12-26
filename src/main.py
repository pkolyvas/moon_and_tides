import threading
import logging
import apploader
import tides
import moon
import display
import time

screen_owner = display.Screen()
current_moon = moon.Moon("current", time.time, 0)


def main():
    display.init_display()

    logging.basicConfig(
        filename=apploader.config['logging']['location'],
        encoding=apploader.config['logging']['encoding'],
        level=apploader.config['logging']['level']
    )
    logging.info('Moon and tides app started.')

    tide_thread = threading.Thread(
        target=tides.tide_worker,
        args=(screen_owner,)
    )
    moon_thread = threading.Thread(
        target=moon.moon_worker,
        args=(screen_owner, current_moon,)
    )
    button_thread = threading.Thread(
        target=display.button_worker,
        args=(screen_owner,)
    )
    display_thread = threading.Thread(
        target=display.display_worker,
        args=(screen_owner,)
    )
    moon_thread.start()
    tide_thread.start()
    button_thread.start()
    display_thread.start()

    # TODO: Deinit lights function on exit
    # TODO: Clean exit


if __name__ == "__main__":
    main()
