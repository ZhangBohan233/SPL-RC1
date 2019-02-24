import "sample31.sp"

class Vehicle {
    var speed = 0;

    def Vehicle(sp) {
        speed = sp;
    }
}

class Car extends Vehicle {
    var d = new Vehicle(60);

    def Car(sp) {
        Vehicle(sp);
    }
}


if (main()) {
    println(getcwf());
}
