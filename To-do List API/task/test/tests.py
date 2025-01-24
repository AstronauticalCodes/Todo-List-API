from hstest import dynamic_test
from .base import TodoApiToolTest


class TodoApiToolTestRunner(TodoApiToolTest):
    funcs = [
        # task 2
        TodoApiToolTest.check_database,
        TodoApiToolTest.check_multiple_json_response,
    ]

    @dynamic_test(data=funcs)
    def test(self, func):
        return func(self)


if __name__ == '__main__':
    TodoApiToolTestRunner().run_tests()
