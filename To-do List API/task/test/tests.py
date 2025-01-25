from hstest import dynamic_test
from .base import TodoApiToolTest


class TodoApiToolTestRunner(TodoApiToolTest):
    funcs = [
        # task 3


        TodoApiToolTest.check_not_logined_tasks,
        TodoApiToolTest.check_logined_tasks,

        TodoApiToolTest.check_logined_task,
        TodoApiToolTest.check_not_logined_task,

        TodoApiToolTest.check_edit_task,

    ]

    @dynamic_test(data=funcs)
    def test(self, func):
        return func(self)


if __name__ == '__main__':
    TodoApiToolTestRunner().run_tests()
