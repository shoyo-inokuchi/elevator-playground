from elevator.buildings import BasicBuilding
from elevator.session import Session
import random
import simpy

RANDOM_SEED = 1


def run_simulation():
    """Set up simulation parameters and run the simulation."""
    random.seed(RANDOM_SEED)
    building = BasicBuilding(10, 1)
    session = Session(building, 36000)
    session.run()


if __name__ == '__main__':
    run_simulation()

