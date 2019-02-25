import "sample31.sp"

/* A vehicle */
class Vehicle {
    var speed = 0;

    def Vehicle(sp) {
        speed = sp;
    }
}

"gg";

/*
 * A car.
 *
 * Car is a special type of Vehicle.
 */
class Car extends Vehicle, Iterable {
    /*
     * The 弟弟.
     */
    var d = new Vehicle(60);

    /*
     * Creates a new car.
     */
    def Car(sp) {
        Vehicle(sp);
    }
}

/*
 * A function.
 */
function f() {

}


if (main()) {
    println(getcwf());

    help(Car);
}
