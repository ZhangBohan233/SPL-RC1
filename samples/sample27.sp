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

try {
    throw new Exception("233");
} catch (e1: TestException; e2: QuizException) {
    print(1);
} catch (e: Exception) {
    print(2);
}
