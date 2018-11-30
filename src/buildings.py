import simpy
from random import randint
from sim_utils import print_status, rand_call
from abc import ABC, abstractmethod


class Building(ABC):
    def __init__(self, num_floors, elevators):
        """
        :param int num_floors: number of floors
        :param list[Elevator] elevators: list of elevator instances
        """
        self.env = None
        self.process = None

        self.num_floors = num_floors
        self.num_elevators = len(elevators)
        self.elevators = elevators

        # Map of floor to length of respective queue
        self.floor_queues = {}
        for i in range(1, num_floors + 1):
            self.floor_queues[i] = 0

        # ID assignment to each elevator
        for i in range(self.num_elevators):
            self.elevators[i].id = i + 1

        self.all_calls = []

    def set_env(self, env):
        self.env = env
        self.process = env.process(self.start())

    def update_floor_queues(self):
        pass

    @abstractmethod
    def start(self):
        """ Start generating random elevator calls and dispatching elevators."""
        pass

    @abstractmethod
    def generate_call(self):
        """ Generates a call from an origin floor to a destination floor according to some distribution."""
        pass

    @abstractmethod
    def select_elevator(self, call):
        """ Judiciously selects an elevator to handle a generated call."""
        pass

    @abstractmethod
    def process_call(self, call, elevator):
        """ Tell selected elevator how to process the call."""
        pass


class BasicBuilding(Building):
    """
    A building with a basic dispatcher.

    Dispatches elevator calls according to basic elevator algorithm (SCAN):
         1) While there are people in the elevator or people waiting in the
             direction of the elevator, keep heading in that direction and
             pickup/dropoff as necessary.
         2) Once elevator has exhausted all requests in its current direction,
             reverse direction and go to step 1) if there are requests. Else, stop
             and wait for a call (or potentially move to another floor deemed more
             effective)
    """

    def start(self):
        while True:
            # TODO: handle specified distribution instead of simple random
            yield self.env.timeout(randint(30, 30))
            call = self.generate_call()
            elevator = self.select_elevator(call)
            self.process_call(call, elevator)

    def generate_call(self):
        call = rand_call(self.env.now, self.num_floors)
        print_status(self.env.now, f'[Generate] call {call.id}: floor {call.origin} to {call.dest}')
        self.floor_queues[call.origin] += 1
        self.all_calls.append(call)
        return call

    def select_elevator(self, call):
        selected = self.elevators[0]

        print_status(self.env.now,
                     f'[Select] call {call.id}: Elevator {selected.id}')
        return selected

    def new_process_call(self, call, elevator):
        elevator.queued_calls.append(call)

    def process_call(self, call, elevator):
        elevator.move_to(call.origin)
        elevator.pick_up()
        call.wait_time = self.env.now - call.orig_time
        print_status(self.env.now, f'call {call.id} waited {call.wait_time / 10} s')
        elevator.move_to(call.dest)
        elevator.drop_off()
        call.done = True
        call.process_time = self.env.now - call.orig_time

        print_status(self.env.now, f'[Done] call {call.id}')