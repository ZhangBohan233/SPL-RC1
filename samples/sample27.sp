import "exception"

class TestException extends Exception {
    function TestException(msg) {
        Exception(msg);
    }
}

class QuizException extends Exception {
    function QuizException(msg) {
        Exception(msg);
    }
}

function t(a, b=null) {
    try {
        throw new TestException("asd");
    } catch (e: TestException) {
        return 1;
    } finally {
        return 3;
    }
}

print(t(1, 2));
