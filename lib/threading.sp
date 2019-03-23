import "functions"


class Thread {

    var process;

    function Thread(tar_name, args) {
        var target = eval(tar_name);

        process = natives.thread(target, tar_name, args);
    }

    function set_daemon(d) {
        process.set_daemon(d);
    }

    function start() {
        process.start();
    }

    function alive() {
        return process.alive();
    }
}


class ThreadPool {


    function ThreadPool(pool_size) {

    }
}

/*
 * Blocks the main thread until the <thread> finishes.
 */
function await(thread) {
    while (thread.alive()) {
        system.sleep(1);
    }
}

function is_alive(th) {
    return th.alive();
}

function await_all(thread_list) {
    while (any(is_alive, thread_list)) {
        system.sleep(1);
    }
}
